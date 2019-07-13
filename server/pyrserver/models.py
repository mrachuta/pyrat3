import uuid
import pytz
from django.db import models
from datetime import datetime
from django.utils import timezone
from time import gmtime, strftime


def short_uuid():
    return uuid.uuid4().hex[:8]


class Client(models.Model):

    """
    Client model.
    client_id is a primary key, to make harder recognize if client is associated
    already with server or not.
    Django has only UUIDField, which can't store short UUID. If default field is
    function, each client receive the same uuid. It must be object.
    There was no way to return short uuid as object directly to default field,
    so separate function was written, and called as object.
    """

    client_id = models.CharField(primary_key=True, default=short_uuid, editable=False, max_length=8)
    pc_uuid = models.CharField(max_length=36)
    join_datetime = models.DateTimeField(default=timezone.now)
    mac = models.CharField(max_length=12)
    os = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=2)
    ext_ip = models.GenericIPAddressField()
    int_ip = models.GenericIPAddressField()
    job_id = models.CharField(max_length=6, null=True, default='empty')
    job_datetime = models.DateTimeField(default=strftime('%Y-%m-%d %H:%M:%S', gmtime(0)))
    job = models.TextField(max_length=20, null=True, default='empty')
    job_args = models.TextField(max_length=500, null=True, default='{}')
    job_result = models.TextField(max_length=5000, null=True, default='empty')
    last_activity_datetime = models.DateTimeField(default=strftime('%Y-%m-%d %H:%M:%S', gmtime(0)))
    objects = models.Manager()

    def __str__(self):
        return self.client_id

    @property
    def ping(self):
        curr_time = datetime.now(tz=pytz.utc)
        delta = curr_time - self.last_activity_datetime
        return delta.seconds

