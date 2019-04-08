from django import forms
from .models import Client


class ClientSendCommandForm(forms.ModelForm):

    pc_uuid = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), to_field_name='pc_uuid')

    class Meta:

        model = Client

        fields = [
            'last_command_id',
            'last_command',
            'last_command_args'
        ]

        labels = {
            'last_command_id': 'Last command ID',
            'last_command': 'Last command',
            'last_command_args': 'Last command args'
        }

        widgets = {
            'last_command_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }

    field_order = [
        'pc_uuid',
        'last_command_id',
        'last_command',
        'last_command_args',
    ]

    """
    def __init__(self, *args, **kwargs):
        super(GateAddForm, self).__init__(*args, **kwargs)
        self.fields['tram'].required = False
        self.fields['car'].required = False
        self.fields['bogie'].required = False
        self.fields['operation_no'].max_length = 6
        self.fields['operation_no'].min_length = 6
        self.fields['operation_no'].label = u'Numer operacji'
        self.fields['operation_no'].widget = forms.TextInput(attrs={'size': '5px', 'maxlength': '6'})
    """


class ClientSendFileForm(forms.Form):

    file = forms.FileField()

    class Meta:

        pass
