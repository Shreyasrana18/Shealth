# Generated by Django 3.2.6 on 2021-08-27 22:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shealth', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='last_login',
        ),
    ]