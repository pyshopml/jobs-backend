# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-08 11:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0003_auto_20170505_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='keywords',
            field=models.ManyToManyField(blank=True, to='vacancies.Tag'),
        ),
    ]