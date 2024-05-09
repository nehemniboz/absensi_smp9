from django.db import models
from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
import datetime
import hashlib

SECRET_KEY = '6e240d77b96eebbb74d1d37078f38d79fb20fb4fa0f9065c963bd3d3addcde65'


def unique_user_validator(value):
    from .models import ProfilAdmin, ProfilGuru, ProfilSiswa

    if ProfilAdmin.objects.filter(user=value).exists() \
            or ProfilGuru.objects.filter(user=value).exists() \
            or ProfilSiswa.objects.filter(user=value).exists():
        raise ValidationError(
            'This user is already associated with another profile.')


def get_current_time():
    return datetime.datetime.now().time()


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class Jadwal(models.Model):
    nama = models.CharField(max_length=20, null=True)
    waktu = models.TimeField(default='06:00')

    def __str__(self):
        return self.nama


class ProfileBase(models.Model):
    nama = models.CharField(max_length=50, null=True)
    alamat = models.CharField(max_length=50, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, validators=[
                                unique_user_validator])
    email = models.EmailField(
        max_length=50, unique=False, null=True, blank=True)

    class Meta:
        abstract = True


class Angkatan(models.Model):
    tahun_ajaran = models.IntegerField(
        validators=[MinValueValidator(1984), max_value_current_year], unique=True)
    jumlah = models.IntegerField(default=0)
    kuota = models.IntegerField(default=100)

    # def calculate_jumlah(self):
    #     return self.profilsiswa_set.count()  # Count the related ProfilSiswa objects

    def save(self, *args, **kwargs):
        # self.jumlah = self.calculate_jumlah()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.tahun_ajaran)


class ProfilSiswa(ProfileBase):
    angkatan = models.ForeignKey(Angkatan, on_delete=models.CASCADE, null=True)
    nisn = models.PositiveIntegerField(
        validators=[MinValueValidator(100000000), MaxValueValidator(10000000000)], null=True)
    hash = models.CharField(max_length=255, null=True)

    def generate_hash(self):
        text_to_hash = f"{self.user.username}{SECRET_KEY}"
        hash_object = hashlib.sha256(text_to_hash.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    @classmethod
    def get_akun_by_hash(cls, hash_value):
        try:
            return cls.objects.get(hash=hash_value)
        except cls.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        self.nama = self.user.username
        self.hash = self.generate_hash()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class ProfilAdmin(ProfileBase):

    def __str__(self):
        return self.user.username


class ProfilGuru(ProfileBase):

    def __str__(self):
        return self.user.username


class Absensi(models.Model):
    profil_siswa = models.ForeignKey(ProfilSiswa, on_delete=models.CASCADE)
    jadwal = models.ForeignKey(Jadwal, on_delete=models.CASCADE)
    tanggal = models.DateField(auto_now_add=True)
    waktu = models.TimeField(default=get_current_time)
    status = models.CharField(max_length=10, choices=[
                              ('hadir', 'Hadir'), ('absen', 'Absen')])

    class Meta:
        unique_together = ('profil_siswa', 'jadwal', 'tanggal')

    def calculate_status(self):
        current_time = get_current_time()
        jadwal_time = self.jadwal.waktu

        if self.jadwal.nama.lower() == 'masuk':
            if current_time < jadwal_time:
                self.status = 'hadir'
            else:
                self.status = 'absen'
        elif self.jadwal.nama.lower() == 'pulang':
            if current_time < jadwal_time:
                self.status = 'absen'
            else:
                self.status = 'hadir'

    def save(self, *args, **kwargs):
        self.calculate_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.profil_siswa} - {self.waktu} - {self.jadwal} - {self.status}'
