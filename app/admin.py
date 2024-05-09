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

    def save_model(self, request, obj, form, change):
        if change:
            original_instance = User.objects.get(pk=obj.pk)
            original_groups = original_instance.groups.all()
            new_groups = form.cleaned_data.get('groups')
            if new_groups and not original_groups == new_groups:
                raise forms.ValidationError("Cannot update user groups.")
        super().save_model(request, obj, form, change)


# Register models and admin classes
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ProfilAdmin)
admin.site.register(ProfilGuru)
admin.site.register(ProfilSiswa)
admin.site.register(Angkatan)
admin.site.register(Jadwal)
admin.site.register(Absensi)
