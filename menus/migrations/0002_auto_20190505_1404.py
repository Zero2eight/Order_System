# Generated by Django 2.1.7 on 2019-05-05 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='work_id',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
