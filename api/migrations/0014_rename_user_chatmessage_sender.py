# Generated by Django 4.2 on 2023-05-29 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_thread_chatmessage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatmessage',
            old_name='user',
            new_name='sender',
        ),
    ]
