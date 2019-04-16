from django import forms
from .models import Client


class ClientSendCommandForm(forms.ModelForm):

    class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):

        def label_from_instance(self, obj):
            return '{} ({}/{})'.format(obj.pc_uuid, obj.ext_ip, obj.int_ip)

    client_id = CustomModelMultipleChoiceField(
        queryset=Client.objects.all(),
        to_field_name='client_id',
        label='Select client(s):',
    )

    class Meta:

        commands = (
            ('popup', 'Show popup'),
            ('run_command', 'Run command'),
            ('file_download', 'Download file on remote host'),
            ('screenshoot', 'Make screenshoot'),
            ('file_upload', 'Upload file from remote host'),
        )

        model = Client

        fields = [
            'last_command_id',
            'last_command',
            'last_command_args'
        ]

        labels = {
            'last_command_id': 'Command ID',
            'last_command': 'Command to execute',
            'last_command_args': 'Command arguments'
        }

        widgets = {
            'last_command_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_command': forms.RadioSelect(choices=commands),
        }

    field_order = [
        'last_command_id',
        'client_id',
        'last_command',
        'last_command_args',
    ]
    '''
    def __init__(self, *args, **kwargs):
        super(ClientSendCommandForm, self).__init__(*args, **kwargs)
        self.fields['ext_ip'].required = False
        self.fields['int_ip'].required = False
        self.fields['bogie'].required = False
        #self.fields['operation_no'].max_length = 6
        #self.fields['operation_no'].min_length = 6
        #self.fields['operation_no'].label = u'Numer operacji'
        #self.fields['operation_no'].widget = forms.TextInput(attrs={'size': '5px', 'maxlength': '6'})
    '''


class ClientSendFileForm(forms.Form):

    file = forms.FileField()

    class Meta:

        pass
