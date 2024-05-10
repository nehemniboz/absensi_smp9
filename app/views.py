from .forms import UserCreateForm, UserUpdateForm, ProfilAdminCreateForm, ProfilAdminUpdateForm, ProfilGuruCreateForm, ProfilGuruUpdateForm, ProfilSiswaCreateForm, ProfilSiswaUpdateForm, AngkatanCreateForm, AngkatanUpdateForm, JadwalUpdateForm, AbsensiCreateForm, AbsensiUpdateForm, UserProfileForm
from .models import User, ProfilAdmin, ProfilGuru, ProfilSiswa, Angkatan, Jadwal, Absensi
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.db import IntegrityError
from django.http import HttpRequest
from django.contrib.auth import logout

from .decorators import check_group

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

def index(request):
    context = {}
    
    return render(request, 'index.html', context)

def absen(request, jadwal):
    # Get the Jadwal object based on the jadwal parameter
    jadwal_object = get_object_or_404(Jadwal, nama__iexact=jadwal)
    
    context = {
        'jadwal': jadwal_object
    }

    return render(request, 'absen.html', context)


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
            return JsonResponse({'message': 'Siswa not found', 'type': 'failed'}, status=200)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=400)


# Render PDF
@login_required
@check_group(['SISWA'])
def render_pdf_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')

        # Retrieve the user object using the user ID
        try:
            user = User.objects.get(id=user_id)
            siswa_instance = ProfilSiswa.objects.get(user=user)
        except (User.DoesNotExist, ProfilSiswa.DoesNotExist):
            return HttpResponse('Invalid user ID')

        template_path = 'qr_pdf.html'

        # Get the name and NISN from the ProfilSiswa instance
        nama = siswa_instance.nama
        nisn = siswa_instance.nisn
        # Generate the hash
        qr_code_hash = siswa_instance.hash

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
        return HttpResponse('Method not allowed')


@login_required
def dashboard(request):
    qr_code = ''
    if request.user.groups.filter(name='SISWA').exists():
        siswa_instance = ProfilSiswa.objects.get(user=request.user)
        qr_code = siswa_instance.hash

    context = {
        'qr_code': qr_code,
    }

    return render(request, 'dashboard.html', context)

@login_required
def user_profile_update(request):
    user = request.user
    form = UserProfileForm(instance=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            logout(request)
            return redirect('user_profile_update')

    context = {
        'form': form
    }

    return render(request, 'user_profile_update.html', context)


# User Views
@login_required
@check_group(['ADMIN'])
def index_user(request):
    # Get all users excluding the currently logged-in user
    users = User.objects.exclude(pk=request.user.pk)
    return render(request, 'index_user.html', {'users': users})


@login_required
@check_group(['ADMIN'])
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
@check_group(['ADMIN'])
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
    return render(request, 'update_user.html', {'form': form})


@login_required
@check_group(['ADMIN'])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('index_user')

# Profil Admin Views


@login_required
@check_group(['ADMIN'])
def index_profil_admin(request):
    profil_admins = ProfilAdmin.objects.all()
    return render(request, 'index_profil_admin.html', {'profil_admins': profil_admins})


@login_required
@check_group(['ADMIN'])
def create_profil_admin(request):
    if request.method == 'POST':
        form = ProfilAdminCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Admin created successfully.')
            return redirect('index_profil_admin')
    else:
        form = ProfilAdminCreateForm()
    return render(request, 'create_profil_admin.html', {'form': form})


@login_required
@check_group(['ADMIN'])
def update_profil_admin(request, pk):
    profil_admin = get_object_or_404(ProfilAdmin, pk=pk)
    if request.method == 'POST':
        form = ProfilAdminUpdateForm(request.POST, instance=profil_admin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Admin updated successfully.')
            return redirect('index_profil_admin')
    else:
        form = ProfilAdminUpdateForm(instance=profil_admin)
    return render(request, 'update_profil_admin.html', {'form': form})


@login_required
@check_group(['ADMIN'])
def delete_profil_admin(request, pk):
    profil_admin = get_object_or_404(ProfilAdmin, pk=pk)
    profil_admin.delete()
    messages.success(request, 'Profil Admin deleted successfully.')
    return redirect('index_profil_admin')

# Profil Guru Views


@login_required
@check_group(['ADMIN', 'GURU'])
def index_profil_guru(request):
    profil_gurus = ProfilGuru.objects.all()
    return render(request, 'index_profil_guru.html', {'profil_gurus': profil_gurus})


@login_required
@check_group(['ADMIN', 'GURU'])
def create_profil_guru(request):
    if request.method == 'POST':
        form = ProfilGuruCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Guru created successfully.')
            return redirect('index_profil_guru')
    else:
        form = ProfilGuruCreateForm()
    return render(request, 'create_profil_guru.html', {'form': form})


@login_required
@check_group(['ADMIN', 'GURU'])
def update_profil_guru(request, pk):
    profil_guru = get_object_or_404(ProfilGuru, pk=pk)
    if request.method == 'POST':
        form = ProfilGuruUpdateForm(request.POST, instance=profil_guru)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Guru updated successfully.')
            return redirect('index_profil_guru')
    else:
        form = ProfilGuruUpdateForm(instance=profil_guru)
    return render(request, 'update_profil_guru.html', {'form': form})


@login_required
@check_group(['ADMIN', 'GURU'])
def delete_profil_guru(request, pk):
    profil_guru = get_object_or_404(ProfilGuru, pk=pk)
    profil_guru.delete()
    messages.success(request, 'Profil Guru deleted successfully.')
    return redirect('index_profil_guru')

# Profil Siswa Views


@login_required
@check_group(['ADMIN', 'GURU'])
def index_profil_siswa(request):
    profil_siswas = ProfilSiswa.objects.all()
    return render(request, 'index_profil_siswa.html', {'profil_siswas': profil_siswas})


@login_required
@check_group(['ADMIN', 'GURU'])
def create_profil_siswa(request):
    if request.method == 'POST':
        form = ProfilSiswaCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Siswa created successfully.')
            return redirect('index_profil_siswa')
    else:
        form = ProfilSiswaCreateForm()
    return render(request, 'create_profil_siswa.html', {'form': form})


@login_required
@check_group(['ADMIN', 'GURU'])
def update_profil_siswa(request, pk):
    profil_siswa = get_object_or_404(ProfilSiswa, pk=pk)
    if request.method == 'POST':
        form = ProfilSiswaUpdateForm(request.POST, instance=profil_siswa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Siswa updated successfully.')
            return redirect('index_profil_siswa')
    else:
        form = ProfilSiswaUpdateForm(instance=profil_siswa)
    return render(request, 'update_profil_siswa.html', {'form': form})


@login_required
@check_group(['ADMIN', 'GURU'])
def delete_profil_siswa(request, pk):
    profil_siswa = get_object_or_404(ProfilSiswa, pk=pk)
    profil_siswa.delete()
    messages.success(request, 'Profil Siswa deleted successfully.')
    return redirect('index_profil_siswa')

# Angkatan Views


@login_required
@check_group(['ADMIN', 'GURU', 'SISWA'])
def index_angkatan(request):
    angkatans = Angkatan.objects.all()
    return render(request, 'index_angkatan.html', {'angkatans': angkatans})


@login_required
@check_group(['ADMIN', 'GURU'])
def create_angkatan(request):
    if request.method == 'POST':
        form = AngkatanCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Angkatan created successfully.')
            return redirect('index_angkatan')
    else:
        form = AngkatanCreateForm()
    return render(request, 'create_angkatan.html', {'form': form})


@login_required
@check_group(['ADMIN', 'GURU'])
def update_angkatan(request, pk):
    angkatan = get_object_or_404(Angkatan, pk=pk)
    if request.method == 'POST':
        form = AngkatanUpdateForm(request.POST, instance=angkatan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Angkatan updated successfully.')
            return redirect('index_angkatan')
    else:
        form = AngkatanUpdateForm(instance=angkatan)
    return render(request, 'update_angkatan.html', {'form': form})


@login_required
@check_group(['ADMIN', 'GURU'])
def delete_angkatan(request, pk):
    angkatan = get_object_or_404(Angkatan, pk=pk)
    angkatan.delete()
    messages.success(request, 'Angkatan deleted successfully.')
    return redirect('index_angkatan')

# Jadwal Views


@login_required
@check_group(['ADMIN'])
def index_jadwal(request):
    jadwals = Jadwal.objects.all()
    return render(request, 'index_jadwal.html', {'jadwals': jadwals})


@login_required
@check_group(['ADMIN'])
def update_jadwal(request, pk):
    jadwal = get_object_or_404(Jadwal, pk=pk)
    if request.method == 'POST':
        form = JadwalUpdateForm(request.POST, instance=jadwal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jadwal updated successfully.')
            return redirect('index_jadwal')
    else:
        form = JadwalUpdateForm(instance=jadwal)
    return render(request, 'update_jadwal.html', {'form': form, 'jadwal': jadwal})

# Absensi Views


@login_required
@check_group(['ADMIN', 'GURU', 'SISWA'])
def index_absensi(request):
    absensis = Absensi.objects.all()
    return render(request, 'index_absensi.html', {'absensis': absensis})


@login_required
@check_group(['ADMIN', 'GURU'])
def create_absensi(request):
    if request.method == 'POST':
        form = AbsensiCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Absensi created successfully.')
            return redirect('index_absensi')
    else:
        form = AbsensiCreateForm()
    return render(request, 'create_absensi.html', {'form': form})


@login_required
@check_group(['ADMIN', 'GURU'])
def update_absensi(request, pk):
    absensi = get_object_or_404(Absensi, pk=pk)
    if request.method == 'POST':
        form = AbsensiUpdateForm(request.POST, instance=absensi)
        if form.is_valid():
            form.save()
            messages.success(request, 'Absensi updated successfully.')
            return redirect('index_absensi')
    else:
        form = AbsensiUpdateForm(instance=absensi)
    return render(request, 'update_absensi.html', {'form': form})


@login_required
@check_group(['ADMIN', 'GURU'])
def delete_absensi(request, pk):
    absensi = get_object_or_404(Absensi, pk=pk)
    absensi.delete()
    messages.success(request, 'Absensi deleted successfully.')
    return redirect('index_absensi')
