# Generated by Django 2.0.2 on 2018-09-04 23:28

from django.db import migrations
import extra_apps.DjangoUeditor.models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20180903_0116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='detail',
            field=extra_apps.DjangoUeditor.models.UEditorField(default='', verbose_name='课程详情'),
        ),
    ]
