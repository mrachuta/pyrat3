from django.contrib import admin
from .models import Client

# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    list_display = [field.name for field in Client._meta.get_fields()]
    date_hierarchy = 'join_datetime'


admin.site.register(Client, ClientAdmin)