from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver
from .models import ProfilSiswa, ProfilAdmin, ProfilGuru, Angkatan
from django.contrib.auth.models import User, Group
from datetime import datetime
# Define thread-local storage for cleaned data
import threading
thread_data = threading.local()

# Signal Receiver to Create Profile


def current_year():
    return datetime.now().year


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        angkatan, created = Angkatan.objects.get_or_create(
            tahun_ajaran=current_year())
        cleaned_data = getattr(thread_data, 'cleaned_data', None)
        if cleaned_data and 'groups' in cleaned_data:
            groups = cleaned_data['groups']
            for group in groups:
                if group.name == 'GURU':
                    ProfilGuru.objects.create(
                        user=instance, nama=instance.username)
                elif group.name == 'SISWA':
                    ProfilSiswa.objects.create(
                        user=instance, nama=instance.username, angkatan=angkatan)
                elif group.name == 'ADMIN':
                    ProfilAdmin.objects.create(
                        user=instance, nama=instance.username)
