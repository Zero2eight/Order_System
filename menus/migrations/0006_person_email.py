# Generated by Django 2.1.7 on 2019-05-09 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0005_auto_20190509_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='email',
            field=models.CharField(default='123@qq.com', max_length=100),
            preserve_default=False,
        ),
    ]
