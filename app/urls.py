
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


    path('index_user/', views.index_user, name='index_user'),
    path('create_user/', views.create_user, name='create_user'),
    path('update_user/<int:pk>/', views.update_user, name='update_user'),
    path('delete_user/<int:pk>/', views.delete_user, name='delete_user'),

    path('index_profil_admin/', views.index_profil_admin,
         name='index_profil_admin'),
    path('create_profil_admin/', views.create_profil_admin,
         name='create_profil_admin'),
    path('update_profil_admin/<int:pk>/', views.update_profil_admin,
         name='update_profil_admin'),
    path('delete_profil_admin/<int:pk>/', views.delete_profil_admin,
         name='delete_profil_admin'),

    path('index_profil_guru/', views.index_profil_guru,
         name='index_profil_guru'),
    path('create_profil_guru/', views.create_profil_guru,
         name='create_profil_guru'),
    path('update_profil_guru/<int:pk>/', views.update_profil_guru,
         name='update_profil_guru'),
    path('delete_profil_guru/<int:pk>/', views.delete_profil_guru,
         name='delete_profil_guru'),

    path('index_profil_siswa/', views.index_profil_siswa,
         name='index_profil_siswa'),
    path('create_profil_siswa/', views.create_profil_siswa,
         name='create_profil_siswa'),
    path('update_profil_siswa/<int:pk>/', views.update_profil_siswa,
         name='update_profil_siswa'),
    path('delete_profil_siswa/<int:pk>/', views.delete_profil_siswa,
         name='delete_profil_siswa'),

    path('index_angkatan/', views.index_angkatan, name='index_angkatan'),
    path('create_angkatan/', views.create_angkatan, name='create_angkatan'),
    path('update_angkatan/<int:pk>/',
         views.update_angkatan, name='update_angkatan'),
    path('delete_angkatan/<int:pk>/',
         views.delete_angkatan, name='delete_angkatan'),

    path('index_jadwal/', views.index_jadwal, name='index_jadwal'),
    path('update_jadwal/<int:pk>/', views.update_jadwal, name='update_jadwal'),

    path('index_absensi/', views.index_absensi, name='index_absensi'),
    path('create_absensi/', views.create_absensi, name='create_absensi'),
    path('update_absensi/<int:pk>/', views.update_absensi, name='update_absensi'),
    path('delete_absensi/<int:pk>/', views.delete_absensi, name='delete_absensi'),
]
