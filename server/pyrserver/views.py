import os
import random
import string
from .models import Client
from django.views import generic
from django.conf import settings
from rest_framework import views
from rest_framework import status
from rest_framework import response
from rest_framework import generics
from django.http import JsonResponse
from rest_framework import exceptions
from rest_framework import pagination
from rest_framework import permissions
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from pyrgui.forms import ClientSendFileForm
from .serializers import ClientSerializer, ClientSerializerRead


def new_job_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_job_id(request):

    """
    Function-based view used by AJAX-request, to get new job_id for form (after submit)
    """

    job_id = new_job_id()

    return JsonResponse({'job_id': job_id})


class ClientUploadFile(generic.FormView):

    """
    Form used for file uploading from client to server.
    """

    template_name = 'pyrgui/upload.html'
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
            file = form.cleaned_data['file']
            client_id = self.kwargs['pk']
            # Save file in following path: /media/<client_id/
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, client_id))
            fs.save(file.name, file)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):

        return JsonResponse(
            {
                'client_id': self.kwargs['pk'],
                'message': 'File uploaded',
            },
            status=status.HTTP_201_CREATED,
        )

    def form_invalid(self, form, **kwargs):

        return JsonResponse(
            {
                'cliend_id': self.kwargs['pk'],
                'message': 'Upload failed',
            },
            status=status.HTTP_400_BAD_REQUEST,

        )


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
