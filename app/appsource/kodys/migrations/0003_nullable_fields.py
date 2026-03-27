# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('kodys', '0002_auto_20191214_1307'),
    ]
    operations = [
        migrations.AlterField(
            model_name='ma_application_contacts',
            name='DISPLAY_ORDER',
            field=models.IntegerField(default=1000, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tx_patients',
            name='AGE',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
