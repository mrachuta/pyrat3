# Generated by Django 2.1.7 on 2019-07-13 14:53

from django.db import migrations, models
import django.utils.timezone
import pyrserver.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('client_id', models.CharField(default=pyrserver.models.short_uuid, editable=False, max_length=8, primary_key=True, serialize=False)),
                ('pc_uuid', models.CharField(max_length=36)),
                ('join_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('mac', models.CharField(max_length=12)),
                ('os', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=2)),
                ('ext_ip', models.GenericIPAddressField()),
                ('int_ip', models.GenericIPAddressField()),
                ('job_id', models.CharField(default='empty', max_length=6, null=True)),
                ('job_datetime', models.DateTimeField(default='1970-01-01 00:00:00')),
                ('job', models.TextField(default='empty', max_length=20, null=True)),
                ('job_args', models.TextField(default='{}', max_length=500, null=True)),
                ('job_result', models.TextField(default='empty', max_length=5000, null=True)),
                ('last_activity_datetime', models.DateTimeField(default='1970-01-01 00:00:00')),
            ],
        ),
    ]
