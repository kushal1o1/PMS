# Generated by Django 5.0.3 on 2024-08-12 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userhome', '0007_billpost_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='deadinfo',
            name='deaddesc',
            field=models.TextField(blank=True, null=True),
        ),
    ]