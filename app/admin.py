from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import ProfilAdmin, ProfilGuru, ProfilSiswa, Angkatan


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',
                  'groups')  # Tambahkan bidang 'groups'


class MyUserAdmin(BaseUserAdmin):
    add_form = MyUserCreationForm  # Gunakan formulir kustom saat menambah pengguna baru
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Tambahkan 'groups' di sini
            'fields': ('username', 'password1', 'password2', 'groups'),
        }),
    )

    def get_group_names(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    # Nama yang akan ditampilkan di admin
    get_group_names.short_description = 'Groups'

    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_superuser', 'get_group_names')


# Daftarkan kelas admin kustom Anda
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(ProfilAdmin)
admin.site.register(ProfilGuru)
admin.site.register(ProfilSiswa)
admin.site.register(Angkatan)
