# Generated by Django 5.1.1 on 2024-10-22 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0006_alter_api_json_object'),
    ]

    operations = [
        migrations.AlterField(
            model_name='api',
            name='json_object',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
