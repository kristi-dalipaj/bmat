# Generated by Django 4.0.4 on 2022-05-01 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='iswc',
            field=models.CharField(blank=True, db_index=True, max_length=11, null=True, unique=True),
        ),
    ]