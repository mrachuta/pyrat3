from django import forms
from .models import Client


class ClientSendCommandForm(forms.ModelForm):

    class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):

        """
        Custom field, for control of label of each client in field.
        Otherwise, model display method had to be changed,
        and change would be available for all model-related views.
        """

        def label_from_instance(self, obj):
            return '{} ({}/{})'.format(obj.pc_uuid, obj.ext_ip, obj.int_ip)

    client_id = CustomModelMultipleChoiceField(
        queryset=Client.objects.all().order_by('-join_datetime'),
        # Set value for each client in field as client_id
        to_field_name='client_id',
        label='Select client(s):',
    )

    class Meta:

        available_jobs = (
            ('popup', 'Show popup'),
            ('run_command', 'Run command'),
            ('file_download', 'Download file on remote host'),
            ('screenshot', 'Make screenshot'),
            ('file_upload', 'Upload file from remote host'),
            ('delete', 'Delete client from database')
        )

        model = Client

        fields = [
            'job_id',
            'job',
            'job_args'
        ]

        labels = {
            'job_id': 'Job ID',
            'job': 'Job to execute',
            'job_args': 'Job arguments'
        }

        widgets = {
            'job_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'job': forms.RadioSelect(choices=available_jobs),
        }

    field_order = [
        'job_id',
        'client_id',
        'job',
        'job_args',
    ]


class ClientSendFileForm(forms.Form):

    file = forms.FileField()

    class Meta:

        pass
