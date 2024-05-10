from import_export import resources, fields
from .models import Absensi


class AbsensiResource(resources.ModelResource):
    class Meta:
        model = Absensi
        fields = ('profil_siswa__nama', 'jadwal__nama',
                  'tanggal', 'waktu', 'status')
