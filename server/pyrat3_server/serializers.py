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
            'job_id',
            'job_datetime',
            'job',
            'job_args',
            'job_result',
            'last_activity_datetime',
        )
        extra_kwargs = {
            'job_id': {'required': False},
            'job_datetime': {'required': False},
            'job': {'required': False},
            'job_args': {'required': False},
            'job_result': {'required': False},
            'last_activity_datetime': {'required': False},
        }

