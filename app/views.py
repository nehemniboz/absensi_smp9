from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from . import forms  # Import your custom user creation form
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from . import forms
from . import models

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import HttpRequest

from xhtml2pdf import pisa

from .models import ProfilSiswa, Jadwal, Absensi
# Create your views here.


def get_current_host(request: HttpRequest) -> str:
    scheme = request.is_secure() and "https" or "http"
    return f'{scheme}://{request.get_host()}/'


def link_callback(uri, rel, request):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    HOSTNAME = get_current_host(request)

    return f"{HOSTNAME}{uri}"


# @login_required

def dashboard(request):
    # if request.method == 'POST':
    #     form = forms.CustomUserCreationForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('dashboard')  # Redirect to a success page or URL
    # else:
    # form = forms.CustomUserCreationForm()
    
    user_create_form = forms.UserCreateForm()
    user_update_form = forms.UserUpdateForm()
    profil_admin_create_form = forms.ProfilAdminCreateForm()
    profil_admin_update_form = forms.ProfilAdminUpdateForm()
    profil_guru_create_form = forms.ProfilGuruCreateForm()
    profil_guru_update_form = forms.ProfilGuruUpdateForm()
    profil_siswa_create_form = forms.ProfilSiswaCreateForm()
    profil_siswa_update_form = forms.ProfilSiswaUpdateForm()
    angkatan_create_form = forms.AngkatanCreateForm()
    angkatan_update_form = forms.AngkatanUpdateForm()
    jadwal_update_form = forms.JadwalUpdateForm()
    absensi_create_form = forms.AbsensiCreateForm()
    absensi_update_form = forms.AbsensiUpdateForm()

    context = {
        'context': {

            'user_create_form': user_create_form,
            'user_update_form': user_update_form,
            'profil_admin_create_form': profil_admin_create_form,
            'profil_admin_update_form': profil_admin_update_form,
            'profil_guru_create_form': profil_guru_create_form,
            'profil_guru_update_form': profil_guru_update_form,
            'profil_siswa_create_form': profil_siswa_create_form,
            'profil_siswa_update_form': profil_siswa_update_form,
            'angkatan_create_form': angkatan_create_form,
            'angkatan_update_form': angkatan_update_form,
            'jadwal_update_form': jadwal_update_form,
            'absensi_create_form': absensi_create_form,
            'absensi_update_form': absensi_update_form,

        }
    }

    return render(request, 'dashboard.html', context)


@login_required
def informasi_akun(request):

    form = forms.InformasiAkunCreateForm()

    if request.method == 'POST':
        form = forms.InformasiAkunCreateForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('informasi_akun')

    context = {
        'informasi_akuns': models.InformasiAkun.objects.all(),
        'create': form,

    }

    return render(request, 'informasi_akun.html', context)


@login_required
def informasi_akun_update(request, pk):
    informasi_akun = get_object_or_404(models.InformasiAkun, pk=pk)
    form = forms.InformasiAkunUpdateForm(instance=informasi_akun)

    if request.method == 'POST':
        form = forms.InformasiAkunUpdateForm(
            request.POST, instance=informasi_akun)

        if form.is_valid():
            form.save()
            return redirect('informasi_akun')

    context = {
        'update': form,

    }

    return render(request, 'informasi_akun_update.html', context)


@login_required
def informasi_akun_delete(request, pk):
    informasi_akun = get_object_or_404(models.InformasiAkun, pk=pk)

    if request.method == 'POST':
        informasi_akun.delete()
        return redirect('informasi_akun')

    return redirect('informasi_akun')


def index(request, jadwal):
    # Get the Jadwal object based on the jadwal parameter
    jadwal_object = get_object_or_404(Jadwal, nama__iexact=jadwal)

    akun_instance = ProfilSiswa.objects.first()
    qr_code_hash = akun_instance.hash

    context = {
        'qr_code': qr_code_hash,
        'jadwal': jadwal_object
    }

    return render(request, 'index.html', context)


def qr_code_check(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data')
        jadwal_name = request.POST.get('jadwal')

        akun = ProfilSiswa.get_akun_by_hash(qr_data)

        if akun:
            now_jadwal = Jadwal.objects.filter(
                nama__iexact=jadwal_name).latest('waktu')

            if now_jadwal:
                try:
                    absensi = Absensi(profil_siswa=akun, jadwal=now_jadwal)
                    absensi.save()
                    return JsonResponse({'message': f'QR code data received successfully {now_jadwal}', 'data': qr_data, 'type': 'success'}, status=200)
                except IntegrityError:
                    return JsonResponse({'message': f'Absensi record already exists for this akun, jadwal, and date combination {now_jadwal}', 'type': 'failed'}, status=200)
            else:
                return JsonResponse({'message': 'Jadwal not found', 'type': 'failed'}, status=200)
        else:
            return JsonResponse({'message': 'ProfilSiswa not found', 'type': 'failed'}, status=200)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=400)


# Render PDF

def render_pdf_view(request):
    template_path = 'qr_pdf.html'

    # Or retrieve it based on some condition
    akun_instance = ProfilSiswa.objects.first()

    # Ensure akun_instance exists before proceeding
    if akun_instance:
        # Get the name and NISN from the ProfilSiswa instance
        nama = akun_instance.nama
        nisn = akun_instance.nisn
        # Generate the hash
        qr_code_hash = akun_instance.hash

        context = {
            'qr_code': qr_code_hash,
            'name': nama,
            'nisn': nisn
        }

        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nama}.pdf"'

        template = get_template(template_path)
        html = template.render(context)

        pisa_status = pisa.CreatePDF(
            html, dest=response, link_callback=lambda uri, rel: link_callback(uri, rel, request))

        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        # Handle case where no ProfilSiswa instance is found
        return HttpResponse('No ProfilSiswa instance found')
