# Generated by Django 3.1.7 on 2021-05-27 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('law_case', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='legal_advice_builder.lawcasetemplate')),
            ],
        ),
        migrations.CreateModel(
            name='Lawsuit',
            fields=[
                ('template_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='legal_advice_builder.template')),
                ('plaintiff', models.TextField(blank=True)),
                ('defendant', models.TextField(blank=True)),
                ('reason', models.TextField(blank=True)),
                ('amount_in_dispute', models.TextField(blank=True)),
                ('claims', models.TextField(blank=True)),
                ('facts_of_the_case', models.TextField(blank=True)),
                ('justification', models.TextField(blank=True)),
            ],
            bases=('legal_advice_builder.template',),
        ),
        migrations.AddField(
            model_name='lawcase',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='legal_advice_builder.template'),
        ),
    ]
