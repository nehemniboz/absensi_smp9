# Generated by Django 5.0.4 on 2024-06-03 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_profiladmin_user_alter_profilguru_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absensi',
            name='status',
            field=models.CharField(choices=[('hadir', 'Hadir'), ('terlambat', 'Terlambat')], max_length=10),
        ),
    ]
