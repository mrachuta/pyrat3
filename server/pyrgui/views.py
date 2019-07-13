import os
import pytz
from shutil import rmtree
from datetime import datetime
from django.views import generic
from django.conf import settings
from pyrserver.models import Client
from django.shortcuts import render
from django.http import JsonResponse
from pyrserver.views import new_job_id
from .forms import ClientSendCommandForm


class Index(generic.edit.FormView):

    """
    Main view with
    """

    template_name = 'pyrgui/index.html'
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
                        rmtree(os.path.join(settings.MEDIA_ROOT, str(client_id)))
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
    template_name = 'pyrgui/client_table.html'
    paginate_by = 10

    def get_queryset(self):

        return Client.objects.all().order_by('-join_datetime')


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
        'pyrgui/files.html',
        {'files_dict': files_dict, 'client': client},
    )
