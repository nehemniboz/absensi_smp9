from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.decorators import login_required

from . import forms 
from . import models
# Create your views here.

@login_required
def dashboard(request):

    context={
        'nama': 'arie',
        'create' : forms.InformasiAkunCreateForm(),
        'update' : forms.InformasiAkunUpdateForm(),
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

    context ={ 
        'informasi_akuns': models.InformasiAkun.objects.all(), 
        'create' : form,

    }

    return render(request, 'informasi_akun.html', context)

@login_required
def informasi_akun_update(request, pk):
    informasi_akun = get_object_or_404(models.InformasiAkun, pk=pk)
    form = forms.InformasiAkunUpdateForm(instance=informasi_akun)
    
    if request.method == 'POST':
        form = forms.InformasiAkunUpdateForm(request.POST, instance = informasi_akun)
        
        if form.is_valid():
            form.save()
            return redirect('informasi_akun')

    context ={ 
        'update' : form,

    }

    return render(request, 'informasi_akun_update.html', context)

@login_required
def informasi_akun_delete(request, pk):
    informasi_akun = get_object_or_404(models.InformasiAkun, pk=pk)
    
    if request.method == 'POST':
        informasi_akun.delete()  
        return redirect('informasi_akun')

    return redirect('informasi_akun')
