from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):

    class Meta:

        model = Client
        fields = (
            'id',
            'pc_uuid',
            'join_datetime',
            'mac',
            'os',
            'name',
            'ext_ip',
            'int_ip',
            'country',
            'last_command_id',
            'last_command_datetime',
            'last_command',
            'last_command_args',
            'last_command_result',
            'last_activity_datetime',
        )
        extra_kwargs = {
            'last_command_id': {'required': False},
            'last_command_datetime': {'required': False},
            'last_command': {'required': False},
            'last_command_args': {'required': False},
            'last_command_result': {'required': False},
            'last_activity_datetime': {'required': False},
        }

