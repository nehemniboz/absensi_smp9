# Generated by Django 5.0.4 on 2024-05-07 08:18

import app.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_profiladmin_email_alter_profilguru_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jadwal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=20, null=True)),
                ('waktu', models.TimeField(default='06:00')),
            ],
        ),
        migrations.AddField(
            model_name='profilsiswa',
            name='hash',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='profilsiswa',
            name='nisn',
            field=models.PositiveIntegerField(null=True, validators=[django.core.validators.MinValueValidator(100000000), django.core.validators.MaxValueValidator(10000000000)]),
        ),
        migrations.CreateModel(
            name='Absensi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tanggal', models.DateField(auto_now_add=True)),
                ('waktu', models.TimeField(default=app.models.get_current_time)),
                ('status', models.CharField(choices=[('hadir', 'Hadir'), ('absen', 'Absen')], max_length=10)),
                ('profil_siswa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.profilsiswa')),
                ('jadwal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.jadwal')),
            ],
            options={
                'unique_together': {('profil_siswa', 'jadwal', 'waktu')},
            },
        ),
    ]