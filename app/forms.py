from django.forms import ModelForm
from .models import ProfilAdmin, ProfilSiswa, ProfilGuru, Angkatan
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.urls import reverse_lazy
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from django.forms import ModelForm, TypedChoiceField


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class ProfilBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))


class ProfilAdminForm(ProfilBaseForm):
    class Meta:
        model = ProfilAdmin
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('profil_admin')


class ProfilSiswaForm(ProfilBaseForm):
    class Meta:
        model = ProfilSiswa
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('profil_siswa')


class ProfilGuruForm(ProfilBaseForm):
    class Meta:
        model = ProfilGuru
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('profil_guru')


class ProfilAdminUpdateForm(ProfilBaseForm):
    class Meta:
        model = ProfilAdmin
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'profil_admin_update', kwargs={'pk': self.instance.pk})


class ProfilSiswaUpdateForm(ProfilBaseForm):
    class Meta:
        model = ProfilSiswa
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'profil_siswa_update', kwargs={'pk': self.instance.pk})


class ProfilGuruUpdateForm(ProfilBaseForm):
    class Meta:
        model = ProfilGuru
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'profil_guru_update', kwargs={'pk': self.instance.pk})


class AngkatanBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))


class AngkatanForm(AngkatanBaseForm):
    year = TypedChoiceField(
        coerce=int, choices=[], initial=current_year, empty_value=None)

    class Meta:
        model = Angkatan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('angkatan')
        # Range from 10 years before current year to 10 years after current year
        self.fields['year'].choices = [(i, i) for i in range(
            current_year() - 10, current_year() + 11)]


class AngkatanUpdateForm(AngkatanBaseForm):
    year = TypedChoiceField(
        coerce=int, choices=[], initial=current_year, empty_value=None)

    class Meta:
        model = Angkatan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'angkatan_update', kwargs={'pk': self.instance.pk})
        # Range from 10 years before current year to 10 years after current year
        self.fields['year'].choices = [(i, i) for i in range(
            current_year() - 10, current_year() + 11)]
