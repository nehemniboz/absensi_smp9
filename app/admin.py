from django.contrib import admin
from django.contrib.auth.models import User
from .models import ProfilAdmin, ProfilGuru, ProfilSiswa, Angkatan, Jadwal, Absensi





admin.site.register(ProfilAdmin)
admin.site.register(ProfilGuru)
admin.site.register(ProfilSiswa)
admin.site.register(Angkatan)
admin.site.register(Jadwal)
admin.site.register(Absensi)
