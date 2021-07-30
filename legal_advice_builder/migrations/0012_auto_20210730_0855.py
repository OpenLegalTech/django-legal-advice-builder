# Generated by Django 3.1.7 on 2021-07-30 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0011_auto_20210724_1717'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lawcase',
            name='law_case_template',
        ),
        migrations.AlterField(
            model_name='question',
            name='field_type',
            field=models.CharField(choices=[('TX', 'Long multiline Text input'), ('SO', 'Pick one of multiple options'), ('MO', 'Pick several of multiple options'), ('SL', 'Short single line text input'), ('DT', 'Date'), ('YN', 'Yes/No')], default='SO', max_length=2),
        ),
    ]
