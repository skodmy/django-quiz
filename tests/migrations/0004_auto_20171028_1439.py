# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-28 14:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0003_auto_20171028_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='demo.Subj'),
        ),
        migrations.DeleteModel(
            name='Subject',
        ),
    ]