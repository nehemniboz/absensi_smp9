from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
import hashlib
SECRET_KEY = '6e240d77b96eebbb74d1d37078f38d79fb20fb4fa0f9065c963bd3d3addcde65'


def get_current_time():
    return datetime.datetime.now().time()


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class Jadwal(models.Model):
    nama = models.CharField(max_length=20, null=True)
    # Default value for finish time is '17:00' (afternoon)
    waktu = models.TimeField(default='06:00')
    # Other fields for schedule

    def __str__(self):
        return self.nama

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
    nisn = models.PositiveIntegerField(
        validators=[MinValueValidator(100000000), MaxValueValidator(10000000000)], null=True)
    hash = models.CharField(max_length=255, null=True)

    def generate_hash(self):
        # Using hashlib to generate a SHA-256 hash
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
        # Mengambil nama dari pengguna terkait
        self.nama = self.user.username  # Memperbarui nama siswa
        self.hash = self.generate_hash()  # Generate hash when saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

# Tabel profil guru


class ProfilGuru(BaseModel):

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
        # Define unique constraint for combination of jadwal and date
        unique_together = ('profil_siswa', 'jadwal', 'waktu')

    def calculate_status(self):
        current_time = get_current_time()
        jadwal_time = self.jadwal.waktu

        if self.jadwal.nama.lower() == 'masuk':
            if current_time < jadwal_time:  # If current time is before the jadwal time
                self.status = 'hadir'
            else:
                self.status = 'absen'
        elif self.jadwal.nama.lower() == 'pulang':
            if current_time < jadwal_time:  # If current time is before the jadwal time
                self.status = 'absen'
            else:
                self.status = 'hadir'

    def save(self, *args, **kwargs):
        self.calculate_status()  # Calculate status before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.profil_siswa} - {self.date} - {self.jadwal} - {self.status}'
