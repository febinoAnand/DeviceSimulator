# Generated by Django 4.2.4 on 2024-10-25 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicedata',
            name='timestamp',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
