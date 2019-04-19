from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):

    class Meta:

        model = Client
        fields = (
            'client_id',
            'pc_uuid',
            'join_datetime',
            'mac',
            'os',
            'name',
            'ext_ip',
            'int_ip',
            'country',
            'command_id',
            'command_datetime',
            'command',
            'command_args',
            'command_result',
            'last_activity_datetime',
        )
        extra_kwargs = {
            'command_id': {'required': False},
            'command_datetime': {'required': False},
            'command': {'required': False},
            'command_args': {'required': False},
            'command_result': {'required': False},
            'last_activity_datetime': {'required': False},
        }

