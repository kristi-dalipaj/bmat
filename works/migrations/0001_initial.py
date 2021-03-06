# Generated by Django 4.0.4 on 2022-05-01 10:51

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RawWork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024)),
                ('contributors', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1024), size=None)),
                ('iswc', models.CharField(blank=True, max_length=11, null=True)),
                ('issues', models.BooleanField(default=False)),
                ('errors', models.CharField(blank=True, max_length=2056, null=True)),
                ('processed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WorkFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('checksum_str', models.CharField(max_length=2056, unique=True)),
                ('size', models.IntegerField(default=0)),
                ('ingested', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024)),
                ('contributors', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1024), size=None)),
                ('iswc', models.CharField(blank=True, max_length=11, null=True, unique=True)),
                ('raw_data', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work', to='works.rawwork')),
            ],
        ),
        migrations.AddField(
            model_name='rawwork',
            name='file',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='works.workfile'),
        ),
    ]
