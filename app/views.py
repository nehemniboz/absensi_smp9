from .forms import UserCreateForm, UserUpdateForm, ProfilAdminCreateForm, ProfilAdminUpdateForm, ProfilGuruCreateForm, ProfilGuruUpdateForm, ProfilSiswaCreateForm, ProfilSiswaUpdateForm, AngkatanCreateForm, AngkatanUpdateForm, JadwalCreateForm, JadwalUpdateForm, AbsensiCreateForm, AbsensiUpdateForm
from .models import User, ProfilAdmin, ProfilGuru, ProfilSiswa, Angkatan, Jadwal, Absensi
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.db import IntegrityError
from django.http import HttpRequest

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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


@login_required
def dashboard(request):
    # if request.method == 'POST':
    #     form = forms.CustomUserCreationForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('dashboard')  # Redirect to a success page or URL
    # else:
    # form = forms.CustomUserCreationForm()

    user_create_form = UserCreateForm()
    user_update_form = UserUpdateForm()
    profil_admin_create_form = ProfilAdminCreateForm()
    profil_admin_update_form = ProfilAdminUpdateForm()
    profil_guru_create_form = ProfilGuruCreateForm()
    profil_guru_update_form = ProfilGuruUpdateForm()
    profil_siswa_create_form = ProfilSiswaCreateForm()
    profil_siswa_update_form = ProfilSiswaUpdateForm()
    angkatan_create_form = AngkatanCreateForm()
    angkatan_update_form = AngkatanUpdateForm()
    jadwal_update_form = JadwalUpdateForm()
    absensi_create_form = AbsensiCreateForm()
    absensi_update_form = AbsensiUpdateForm()

    context = {
        'form': absensi_create_form,
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


# @login_required
# def informasi_akun(request):

#     form = forms.InformasiAkunCreateForm()

#     if request.method == 'POST':
#         form = forms.InformasiAkunCreateForm(request.POST)

#         if form.is_valid():
#             form.save()
#             return redirect('informasi_akun')

#     context = {
#         'informasi_akuns': models.InformasiAkun.objects.all(),
#         'create': form,

#     }

#     return render(request, 'informasi_akun.html', context)


# @login_required
# def informasi_akun_update(request, pk):
#     informasi_akun = get_object_or_404(models.InformasiAkun, pk=pk)
#     form = forms.InformasiAkunUpdateForm(instance=informasi_akun)

#     if request.method == 'POST':
#         form = forms.InformasiAkunUpdateForm(
#             request.POST, instance=informasi_akun)

#         if form.is_valid():
#             form.save()
#             return redirect('informasi_akun')

#     context = {
#         'update': form,

#     }

#     return render(request, 'informasi_akun_update.html', context)


# @login_required
# def informasi_akun_delete(request, pk):
#     informasi_akun = get_object_or_404(models.InformasiAkun, pk=pk)

#     if request.method == 'POST':
#         informasi_akun.delete()
#         return redirect('informasi_akun')

#     return redirect('informasi_akun')


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


# User Views
@login_required
def index_user(request):
    users = User.objects.all()
    return render(request, 'index_user.html', {'users': users})


@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('index_user')
    else:
        form = UserCreateForm()
    return render(request, 'create_user.html', {'form': form})


@login_required
def update_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('index_user')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'user': user})


@login_required
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('index_user')

# Profil Admin Views


@login_required
def index_profil_admin(request):
    profil_admins = ProfilAdmin.objects.all()
    return render(request, 'index_profil_admin.html', {'profil_admins': profil_admins})


@login_required
def create_profil_admin(request):
    if request.method == 'POST':
        form = ProfilAdminCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Admin created successfully.')
            return redirect('dashboard')
    else:
        form = ProfilAdminCreateForm()
    return render(request, 'create_profil_admin.html', {'form': form})


@login_required
def update_profil_admin(request, pk):
    profil_admin = get_object_or_404(ProfilAdmin, pk=pk)
    if request.method == 'POST':
        form = ProfilAdminUpdateForm(request.POST, instance=profil_admin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Admin updated successfully.')
            return redirect('dashboard')
    else:
        form = ProfilAdminUpdateForm(instance=profil_admin)
    return render(request, 'update_profil_admin.html', {'form': form, 'profil_admin': profil_admin})


@login_required
def delete_profil_admin(request, pk):
    profil_admin = get_object_or_404(ProfilAdmin, pk=pk)
    profil_admin.delete()
    messages.success(request, 'Profil Admin deleted successfully.')
    return redirect('dashboard')

# Profil Guru Views


@login_required
def index_profil_guru(request):
    profil_gurus = ProfilGuru.objects.all()
    return render(request, 'index_profil_guru.html', {'profil_gurus': profil_gurus})


@login_required
def create_profil_guru(request):
    if request.method == 'POST':
        form = ProfilGuruCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Guru created successfully.')
            return redirect('dashboard')
    else:
        form = ProfilGuruCreateForm()
    return render(request, 'create_profil_guru.html', {'form': form})


@login_required
def update_profil_guru(request, pk):
    profil_guru = get_object_or_404(ProfilGuru, pk=pk)
    if request.method == 'POST':
        form = ProfilGuruUpdateForm(request.POST, instance=profil_guru)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Guru updated successfully.')
            return redirect('dashboard')
    else:
        form = ProfilGuruUpdateForm(instance=profil_guru)
    return render(request, 'update_profil_guru.html', {'form': form, 'profil_guru': profil_guru})


@login_required
def delete_profil_guru(request, pk):
    profil_guru = get_object_or_404(ProfilGuru, pk=pk)
    profil_guru.delete()
    messages.success(request, 'Profil Guru deleted successfully.')
    return redirect('dashboard')

# Profil Siswa Views


@login_required
def index_profil_siswa(request):
    profil_siswas = ProfilSiswa.objects.all()
    return render(request, 'index_profil_siswa.html', {'profil_siswas': profil_siswas})


@login_required
def create_profil_siswa(request):
    if request.method == 'POST':
        form = ProfilSiswaCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Siswa created successfully.')
            return redirect('dashboard')
    else:
        form = ProfilSiswaCreateForm()
    return render(request, 'create_profil_siswa.html', {'form': form})


@login_required
def update_profil_siswa(request, pk):
    profil_siswa = get_object_or_404(ProfilSiswa, pk=pk)
    if request.method == 'POST':
        form = ProfilSiswaUpdateForm(request.POST, instance=profil_siswa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Siswa updated successfully.')
            return redirect('dashboard')
    else:
        form = ProfilSiswaUpdateForm(instance=profil_siswa)
    return render(request, 'update_profil_siswa.html', {'form': form, 'profil_siswa': profil_siswa})


@login_required
def delete_profil_siswa(request, pk):
    profil_siswa = get_object_or_404(ProfilSiswa, pk=pk)
    profil_siswa.delete()
    messages.success(request, 'Profil Siswa deleted successfully.')
    return redirect('dashboard')

# Angkatan Views


@login_required
def index_angkatan(request):
    angkatans = Angkatan.objects.all()
    return render(request, 'index_angkatan.html', {'angkatans': angkatans})


@login_required
def create_angkatan(request):
    if request.method == 'POST':
        form = AngkatanCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Angkatan created successfully.')
            return redirect('dashboard')
    else:
        form = AngkatanCreateForm()
    return render(request, 'create_angkatan.html', {'form': form})


@login_required
def update_angkatan(request, pk):
    angkatan = get_object_or_404(Angkatan, pk=pk)
    if request.method == 'POST':
        form = AngkatanUpdateForm(request.POST, instance=angkatan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Angkatan updated successfully.')
            return redirect('dashboard')
    else:
        form = AngkatanUpdateForm(instance=angkatan)
    return render(request, 'update_angkatan.html', {'form': form, 'angkatan': angkatan})


@login_required
def delete_angkatan(request, pk):
    angkatan = get_object_or_404(Angkatan, pk=pk)
    angkatan.delete()
    messages.success(request, 'Angkatan deleted successfully.')
    return redirect('dashboard')

# Jadwal Views


@login_required
def index_jadwal(request):
    jadwals = Jadwal.objects.all()
    return render(request, 'index_jadwal.html', {'jadwals': jadwals})


@login_required
def update_jadwal(request, pk):
    jadwal = get_object_or_404(Jadwal, pk=pk)
    if request.method == 'POST':
        form = JadwalUpdateForm(request.POST, instance=jadwal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jadwal updated successfully.')
            return redirect('dashboard')
    else:
        form = JadwalUpdateForm(instance=jadwal)
    return render(request, 'update_jadwal.html', {'form': form, 'jadwal': jadwal})

# Absensi Views


@login_required
def index_absensi(request):
    absensis = Absensi.objects.all()
    return render(request, 'index_absensi.html', {'absensis': absensis})


@login_required
def create_absensi(request):
    if request.method == 'POST':
        form = AbsensiCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Absensi created successfully.')
            return redirect('dashboard')
    else:
        form = AbsensiCreateForm()
    return render(request, 'create_absensi.html', {'form': form})


@login_required
def update_absensi(request, pk):
    absensi = get_object_or_404(Absensi, pk=pk)
    if request.method == 'POST':
        form = AbsensiUpdateForm(request.POST, instance=absensi)
        if form.is_valid():
            form.save()
            messages.success(request, 'Absensi updated successfully.')
            return redirect('dashboard')
    else:
        form = AbsensiUpdateForm(instance=absensi)
    return render(request, 'update_absensi.html', {'form': form, 'absensi': absensi})


@login_required
def delete_absensi(request, pk):
    absensi = get_object_or_404(Absensi, pk=pk)
    absensi.delete()
    messages.success(request, 'Absensi deleted successfully.')
    return redirect('dashboard')
