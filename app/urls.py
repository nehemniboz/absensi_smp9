
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('informasi_akun/', views.informasi_akun, name='informasi_akun'),
    path('informasi_akun_update/<int:pk>/',
         views.informasi_akun_update, name='informasi_akun_update'),
    path('informasi_akun_delete/<int:pk>/',
         views.informasi_akun_delete, name='informasi_akun_delete'),
    path('absen/<str:jadwal>/', views.index, name="index"),
    path('qr_pdf/', views.render_pdf_view, name="qr_pdf"),
    path('qr_codes/', views.qr_code_check, name='qr_code_check'),
]
