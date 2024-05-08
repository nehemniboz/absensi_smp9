
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
#     path('informasi_akun/', views.informasi_akun, name='informasi_akun'),
#     path('informasi_akun_update/<int:pk>/',
#          views.informasi_akun_update, name='informasi_akun_update'),
#     path('informasi_akun_delete/<int:pk>/',
#          views.informasi_akun_delete, name='informasi_akun_delete'),
    path('absen/<str:jadwal>/', views.index, name="index"),
    path('qr_pdf/', views.render_pdf_view, name="qr_pdf"),
    path('qr_codes/', views.qr_code_check, name='qr_code_check'),
    
#     path('create_user/', views.create_user, name='create_user'),
#     path('create_profil_admin/', views.create_profil_admin,
#          name='create_profil_admin'),
#     path('create_profil_guru/', views.create_profil_guru,
#          name='create_profil_guru'),
#     path('create_profil_siswa/', views.create_profil_siswa,
#          name='create_profil_siswa'),
#     path('create_angkatan/', views.create_angkatan, name='create_angkatan'),
#     path('update_angkatan/<int:pk>/',
#          views.update_angkatan, name='update_angkatan'),
#     path('update_jadwal/<int:pk>/', views.update_jadwal, name='update_jadwal'),
#     path('create_absensi/', views.create_absensi, name='create_absensi'),
#     path('update_absensi/<int:pk>/', views.update_absensi, name='update_absensi'),
]
