from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ProfilAdmin, ProfilGuru, ProfilSiswa, Angkatan, Jadwal, Absensi
from django import forms
from .signals import thread_data

# Custom User Creation Form


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = '__all__'

    def save(self, commit=True):
        # Save cleaned data to thread-local storage
        thread_data.cleaned_data = self.cleaned_data
        return super().save(commit)

# Custom User Admin


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'groups'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # If editing an existing object
            return self.readonly_fields + ('username', 'groups')
        return self.readonly_fields

# Custom form for ProfilAdmin


class ProfilAdminForm(forms.ModelForm):
    class Meta:
        model = ProfilAdmin
        fields = '__all__'
        exclude = ['user']

# Custom admin class for ProfilAdmin


class ProfilAdminAdmin(admin.ModelAdmin):
    form = ProfilAdminForm

# Custom form for ProfilGuru


class ProfilGuruForm(forms.ModelForm):
    class Meta:
        model = ProfilGuru
        fields = '__all__'
        exclude = ['user']

# Custom admin class for ProfilGuru


class ProfilGuruAdmin(admin.ModelAdmin):
    form = ProfilGuruForm

# Custom form for ProfilSiswa


class ProfilSiswaForm(forms.ModelForm):
    class Meta:
        model = ProfilSiswa
        fields = '__all__'
        exclude = ['user']

# Custom admin class for ProfilSiswa


class ProfilSiswaAdmin(admin.ModelAdmin):
    form = ProfilSiswaForm


# Register models and admin classes
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ProfilAdmin, ProfilAdminAdmin)
admin.site.register(ProfilGuru, ProfilGuruAdmin)
admin.site.register(ProfilSiswa, ProfilSiswaAdmin)
admin.site.register(Angkatan)
admin.site.register(Jadwal)
admin.site.register(Absensi)
