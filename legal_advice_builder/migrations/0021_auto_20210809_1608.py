# Generated by Django 3.1.7 on 2021-08-09 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0020_auto_20210806_1552'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='textblockcondition',
            unique_together=set(),
        ),
    ]