# Generated by Django 5.0.3 on 2024-05-06 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userhome', '0003_remove_poultry_poultryid_poultry_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poultry',
            name='poultryName',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]