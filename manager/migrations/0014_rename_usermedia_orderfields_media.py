# Generated by Django 3.2.9 on 2022-05-25 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0013_auto_20220525_1556'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderfields',
            old_name='usermedia',
            new_name='media',
        ),
    ]