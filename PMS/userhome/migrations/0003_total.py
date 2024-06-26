# Generated by Django 5.0.3 on 2024-05-09 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userhome', '0002_rename_poultry_billpost_poultryname'),
    ]

    operations = [
        migrations.CreateModel(
            name='Total',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('totalDana', models.IntegerField(default=0)),
                ('totalMedicine', models.IntegerField(default=0)),
                ('totalVaccine', models.IntegerField(default=0)),
                ('totalAmount', models.IntegerField(default=0)),
                ('poultryName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userhome.poultry')),
            ],
        ),
    ]
