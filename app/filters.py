import django_filters
from django import forms
from .models import Absensi


class AbsensiFilter(django_filters.FilterSet):
    tanggal = django_filters.DateFilter(
        field_name='tanggal',
        label='Tanggal',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Absensi
        fields = ['tanggal']
