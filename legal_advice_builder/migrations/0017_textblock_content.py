# Generated by Django 3.1.7 on 2021-08-05 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0016_auto_20210805_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='textblock',
            name='content',
            field=models.TextField(default=''),
        ),
    ]
