# Generated by Django 3.2.9 on 2022-05-24 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installation', '0002_auto_20220523_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconstants',
            name='site_email',
            field=models.CharField(blank=True, default='armlogi@gmail.com', max_length=100, null=True),
        ),
    ]