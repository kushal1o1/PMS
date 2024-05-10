# Generated by Django 5.0.3 on 2024-05-10 09:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userhome', '0005_poultry_totaldead'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeadInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('totalDead', models.IntegerField(default=0)),
                ('deadDate', models.DateField(auto_now_add=True)),
                ('poultryName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userhome.poultry')),
            ],
        ),
    ]