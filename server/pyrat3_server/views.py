from django.shortcuts import render
from django.views import generic
from .models import Client
from .forms import ClientSendCommandForm, ClientSendFileForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import views
from rest_framework import status
from .serializers import ClientSerializer
from django.utils import timezone
import time
import random
import string
from os import path
import uuid

from datetime import datetime
import pytz

from django.http import JsonResponse

from ast import literal_eval

# Create your views here.
from django.http import HttpResponse, Http404


def new_command_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Index(generic.edit.FormView):

    template_name = 'pyrat3_server/index.html'
    form_class = ClientSendCommandForm
    initial = {'command_id': new_command_id}
    #success_url = 'index'

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            #print('FORM VALID')
            for client_id in form.cleaned_data['client_id']:
                #print(form.cleaned_data)
                #print(client_id)
                #print(type(client_id))
                #client = form.save(commit=False)
                client = Client.objects.get(client_id=client_id)
                client.command_id = form.cleaned_data['command_id']
                client.command = form.cleaned_data['command']
                client.command_datetime = datetime.now(tz=pytz.utc)
                client.command_args = form.cleaned_data['command_args']
                client.save()
            return self.form_valid(form)
        else:
            #print(form.cleaned_data)
            return self.form_invalid(form)

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        return JsonResponse({'form_valid': True}, status=200)

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return JsonResponse({'form_valid': False}, status=400)


def generate_command_id(request):

    command_id = new_command_id()

    return JsonResponse({'command_id': command_id})


class ClientTable(generic.ListView):

    context_object_name = 'clients'
    template_name = 'pyrat3_server/client_table.html'

    def get_queryset(self):

        return Client.objects.all().order_by('-join_datetime')


class ClientList(views.APIView):

    def get(self, request, format=None):

        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            try:
                client = Client.objects.get(pc_uuid=request.data['pc_uuid'])
                changes = []
                for key, value in request.data.items():
                    if getattr(client, key) != request.data[key]:
                        changes.append(key)
                        setattr(client, key, value)
                client.save()
                if changes:
                    return Response(data={'client_id': client.client_id, 'message': 'Exists, modified'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(data={'client_id': client.client_id, 'message': 'Exists, not modified'},
                                    status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                serializer.save()
                return Response(data={'client_id': serializer.data['client_id'], 'message': 'New, added'},
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientDetail(generics.RetrieveUpdateAPIView):

    #lookup_field = 'pc_uuid'
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientUploadFile(generic.FormView):

    template_name = 'pyrat3_server/upload.html'
    form_class = ClientSendFileForm

    def get(self, request, *args, **kwargs):

        if Client.objects.filter(pk=self.kwargs['pk']).exists():
            """Handle GET requests: instantiate a blank version of the form."""
            return self.render_to_response(self.get_context_data())
        else:
            raise Http404

    def post(self, request, *args, **kwargs):

        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            print(self.kwargs)
            print(form.cleaned_data)
            client_id = self.kwargs['pk']
            file = form.cleaned_data['file']
            fs = FileSystemStorage(location=path.join(settings.MEDIA_ROOT, client_id))
            fs.save(file.name, file)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):

        return HttpResponse('OK')

    # funkcja na odpowiedz w formie Json na valid i invalid form
