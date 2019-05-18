import os
import pytz
import random
import string
from .models import Client
from datetime import datetime
from django.views import generic
from django.conf import settings
from rest_framework import views
from rest_framework import status
from rest_framework import response
from django.shortcuts import render
from rest_framework import generics
from django.http import JsonResponse
from rest_framework import exceptions
from rest_framework import pagination
from rest_framework import permissions
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from .forms import ClientSendCommandForm, ClientSendFileForm
from .serializers import ClientSerializer, ClientSerializerRead


def new_job_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Index(generic.edit.FormView):

    """
    Main view with
    """

    template_name = 'pyrat3_server/index.html'
    form_class = ClientSendCommandForm
    initial = {'job_id': new_job_id}

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():

            """
            Custom save method for form object to skip some fields.
            Iteration over client_id (which is custom
            MultipleModelField) allow to distribute command in one shot
            to multiple clients.
            """

            for client_id in form.cleaned_data['client_id']:
                if form.cleaned_data['job'] != 'delete':
                    client = Client.objects.get(client_id=client_id)
                    client.job_id = form.cleaned_data['job_id']
                    client.job = form.cleaned_data['job']
                    # Set tz (timezone) to UTC for unify time objects
                    client.job_datetime = datetime.now(tz=pytz.utc)
                    client.job_args = form.cleaned_data['job_args']
                    client.save()
                else:
                    try:
                        os.rmdir(os.path.join(settings.MEDIA_ROOT, str(client_id)))
                    except FileNotFoundError:
                        pass
                    finally:
                        Client.objects.get(client_id=client_id).delete()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # Return validation status for javascript submitJob function
    def form_valid(self, form):
        return JsonResponse({'form_valid': True}, status=200)

    def form_invalid(self, form):
        return JsonResponse({'form_valid': False}, status=400)


class ClientTable(generic.ListView):

    """
    View used by AJAX-request, to get details of each client.
    """

    context_object_name = 'clients'
    template_name = 'pyrat3_server/client_table.html'
    paginate_by = 10

    def get_queryset(self):

        return Client.objects.all().order_by('-join_datetime')


class ClientUploadFile(generic.FormView):

    """
    Form used for file uploading from client to server.
    """

    template_name = 'pyrat3_server/upload.html'
    form_class = ClientSendFileForm

    def get(self, request, *args, **kwargs):

        """
        Prevent unregistered clients from access to form.
        Form will be generated only if valid client_id is given in url param.
        """

        if Client.objects.filter(pk=self.kwargs['pk']).exists():
            return self.render_to_response(self.get_context_data())
        else:
            raise Http404

    def post(self, request, *args, **kwargs):

        form = self.get_form()
        if form.is_valid():
            client_id = self.kwargs['pk']
            file = form.cleaned_data['file']
            # Save file in following path: /media/<client_id/
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, client_id))
            fs.save(file.name, file)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):

        return HttpResponse('OK')

    # Todo: response to valid/invalid form as JSON


def client_files(request, **kwargs):

    """
    Function based view for display file list for requested client.
    """

    client_id = kwargs['pk']
    client = Client.objects.get(pk=client_id)
    files_dict = {}
    # Get file-folder related to requested client
    with os.scandir(os.path.join(settings.MEDIA_ROOT, client_id)) as dir_content:
        for file in dir_content:
            file_attrs = {}

            """
            Solution found on Stackoverflow 
            https://stackoverflow.com/questions/10960477/how-to-read-file-attributes-in-directory
            """

            file_attrs['size'] = file.stat().st_size
            # Set tz (timezone) to UTC for unify time objects
            file_attrs['mtime'] = datetime.fromtimestamp(
                file.stat().st_mtime, tz=pytz.utc
            )
            files_dict[file.name] = file_attrs
    # Render a webpage with links to files
    return render(
        request,
        'pyrat3_server/files.html',
        {'files_dict': files_dict, 'client': client},
    )


def generate_job_id(request):

    """
    Function-based view used by AJAX-request, to get new job_id for form (after submit)
    """

    job_id = new_job_id()

    return JsonResponse({'job_id': job_id})


class ClientList(views.APIView):

    """
    Customized DRF-view for distribute list of clients
    """

    class StandardResultsSetPagination(pagination.PageNumberPagination):

        """
        Custom pagination. Applied only in ClientList view
        (due to this, not applied in settings.py using
        'DEFAULT_PAGINATION_CLASS').
        """

        page_size = 5
        page_size_query_param = 'page_size'
        max_page_size = 5

    class IsPostOrIsAuthenticated(permissions.BasePermission):

        """
        Custom permission, for access to ClientList via GET request.
        If authorization via Django is obtained, list of clients will
        be available. Otherwise, raise PermissionDenied error.
        """

        def has_permission(self, request, view):

            if request.method == 'POST':
                return True
            else:
                return request.user and request.user.is_authenticated

    # Set permission class as active
    permission_classes = (IsPostOrIsAuthenticated,)
    # Set pagination class as active
    pagination_class = StandardResultsSetPagination

    """
    In DRF custom class-based views, pagination must be applied
    by override some methods. Solution was found on:
    https://riptutorial.com/django-rest-framework/example/30604/-advanced-
    -pagination-on-non-generic-views-viewsets
    """

    def get(self, request, format=None):

        clients = Client.objects.all()
        page = self.paginate_queryset(clients)
        if page is not None:
            serializer = ClientSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    @property
    def paginator(self):

        """
        The paginator instance associated with the view, or `None`.
        """

        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):

        """
        Return a single page of results, or `None` if pagination is disabled.
        """

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):

        """
        Return a paginated style `Response` object for the given output data.
        """

        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def post(self, request, format=None):

        """
        POST requests are checked for client existing.
        If client exists, there is another check: does any client
        detail was changed?
        It prevents to create multiple clients (for example IP-adress
        has been changed, or client used another adapter to connect to network).
        Clients are recognized by UUID of PC, which in standard cases
        stay unchanged.
        If client not exist, a new object in DB is created.
        """

        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            try:
                client = Client.objects.get(pc_uuid=request.data['pc_uuid'])
                changes = []

                """
                Iterate over client attributes and compare it with this
                received via POST request.
                """

                for key, value in request.data.items():

                    """
                    If attribute in saved in DB instance is not the same
                    as attribute in POST data - add changed attribute name to list and
                    set this attribute (update client).
                    """

                    if getattr(client, key) != request.data[key]:
                        changes.append(key)
                        setattr(client, key, value)
                client.save()
                # If list with changed attributes is not empty, client was updated
                if changes:
                    return response.Response(
                        data={
                            'client_id': client.client_id,
                            'message': 'Exists, modified',
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return response.Response(
                        data={
                            'client_id': client.client_id,
                            'message': 'Exists, not modified',
                        },
                        status=status.HTTP_200_OK,
                    )
            # If client was not found in DB, create new object
            except ObjectDoesNotExist:
                serializer.save()
                return response.Response(
                    data={
                        'client_id': serializer.data['client_id'],
                        'message': 'New, added',
                    },
                    status=status.HTTP_201_CREATED,
                )
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # If information about insufficient privileges should be shown, raise NotAuthenticated()
    def permission_denied(self, request, message=None):
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.PermissionDenied()


class ClientDetail(generics.RetrieveUpdateAPIView):

    """
    DRF-view for distribute requested client details.
    """

    queryset = Client.objects.all()

    def get_serializer_class(self):

        """
        Limit fields distributed by GET vs other request type.
        Additional serializer was created to distribute only non-sensitive data.
        """

        method = self.request.method
        if method == 'GET':
            return ClientSerializerRead
        else:
            return ClientSerializer
