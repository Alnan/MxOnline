# Generated by Django 2.0.2 on 2018-09-02 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name='是否是公开课'),
        ),
    ]
