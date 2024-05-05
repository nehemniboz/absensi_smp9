from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


# BaseModel untuk mewarisi field dari InformasiAkun
class BaseModel(models.Model):
    nama = models.CharField(max_length=50)
    alamat = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=50, unique=True, null=True)

    class Meta:
        abstract = True


class Angkatan(models.Model):
    tahun_ajaran = models.IntegerField(
        validators=[MinValueValidator(1984), max_value_current_year], unique=True)
    jumlah = models.IntegerField(default=0)
    kuota = models.IntegerField(default=100)

    def __str__(self):
        return str(self.tahun_ajaran)


@receiver(post_save, sender=User)
def add_user_to_siswa_group(sender, instance, created, **kwargs):
    if created:
        siswa_group = Group.objects.get(name='siswa')  # Get the Siswa group
        instance.groups.add(siswa_group)  # Add the user to the Siswa group


@receiver(pre_delete, sender=User)
def remove_user_from_siswa_group(sender, instance, **kwargs):
    if instance.groups.filter(name='Siswa').exists():
        angkatan = instance.profilsiswa.angkatan
        angkatan.jumlah -= 1
        angkatan.save()


@receiver(post_save, sender=BaseModel)
def update_angkatan_jumlah(sender, instance, created, **kwargs):
    if created and isinstance(instance, ProfilSiswa):
        angkatan = instance.angkatan
        count = angkatan.profilsiswa_set.count()
        if angkatan.jumlah < angkatan.kuota and count > 0:
            angkatan.jumlah += 1
            angkatan.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.groups.filter(name='Admin').exists():
            ProfilAdmin.objects.create(user=instance)
        elif instance.groups.filter(name='Siswa').exists():
            angkatan = Angkatan.objects.get_or_create(
                tahun_ajaran=current_year())[0]
            ProfilSiswa.objects.create(user=instance, angkatan=angkatan)
            angkatan.jumlah += 1  # Tambah jumlah angkatan
            angkatan.save()  # Simpan perubahan
        elif instance.groups.filter(name='Guru').exists():
            ProfilGuru.objects.create(user=instance)


# Tabel profil admin
class ProfilAdmin(BaseModel):

    def __str__(self):
        return self.user.username


# Tabel profil siswa
class ProfilSiswa(BaseModel):
    angkatan = models.ForeignKey(Angkatan, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

# Tabel profil guru


class ProfilGuru(BaseModel):

    def __str__(self):
        return self.user.username
