from django.db import models
import uuid
from django.utils import timezone
from time import gmtime, strftime


# Create your models here.
class Client(models.Model):

    # change PK to ID due to prevent detection of associated clients

    client_id = models.CharField(primary_key=True, default=uuid.uuid4().hex[:8], editable=False, max_length=8)
    pc_uuid = models.CharField(max_length=36)
    join_datetime = models.DateTimeField(default=timezone.now)
    mac = models.CharField(max_length=12)
    os = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=2)
    ext_ip = models.GenericIPAddressField()
    int_ip = models.GenericIPAddressField()
    last_command_id = models.CharField(max_length=6, null=True, default='empty')
    last_command_datetime = models.DateTimeField(default=strftime('%Y-%m-%d %H:%M:%S', gmtime(0)))
    last_command = models.TextField(max_length=20, null=True, default='empty')
    last_command_args = models.TextField(max_length=500, null=True, default='{}')
    last_command_result = models.TextField(max_length=5000, null=True, default='empty')
    #last_command_result_datetime = models.DateTimeField(default=strftime('%Y-%m-%d %H:%M:%S', gmtime(0)))
    last_activity_datetime = models.DateTimeField(default=strftime('%Y-%m-%d %H:%M:%S', gmtime(0)))
    #ping = models.CharField(max_length=7, blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return self.client_id




