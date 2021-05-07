# Generated by Django 3.1.7 on 2021-05-06 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0003_lawcase_allow_download'),
    ]

    operations = [
        migrations.CreateModel(
            name='LawCaseTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('recipient', models.TextField(blank=True)),
                ('sender', models.TextField(blank=True)),
                ('date', models.CharField(blank=True, max_length=50)),
                ('subject', models.CharField(blank=True, max_length=200)),
                ('body', models.TextField()),
                ('signature', models.TextField(blank=True)),
            ],
        ),
    ]
