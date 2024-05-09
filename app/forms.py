from django.forms import ModelForm, CharField, EmailField, ChoiceField, PasswordInput
from crispy_forms.layout import Layout, Submit
from .models import ProfilAdmin, ProfilSiswa, ProfilGuru, Angkatan, Jadwal, Absensi
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.urls import reverse_lazy
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from django.forms import ModelForm, TypedChoiceField

from django import forms
from django.contrib.auth.models import User, Group

from .signals import thread_data


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class UserBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))


class UserCreateForm(UserBaseForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'groups']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save cleaned data to thread-local storage
        thread_data.cleaned_data = self.cleaned_data

        # Call the super save method to save the user object
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()  # Save the many-to-many relationships (groups)
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('dashboard')


class UserUpdateForm(UserBaseForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'groups']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_groups(self):
        # Ensure groups can't be updated
        instance = getattr(self, 'instance', None)
        # If instance exists (updating), and has a primary key
        if instance and instance.pk:
            original_instance = User.objects.get(pk=instance.pk)
            original_groups = original_instance.groups.all()
            new_groups = self.cleaned_data.get('groups')
            if new_groups and not original_groups == new_groups:
                raise forms.ValidationError("Cannot update user groups.")
        return self.cleaned_data['groups']

    def save(self, commit=True):
        # Save cleaned data to thread-local storage
        thread_data.cleaned_data = self.cleaned_data

        # Call the super save method to save the user object
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()  # Save the many-to-many relationships (groups)
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'dashboard', kwargs={'pk': self.instance.pk})


class ProfilBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))


class ProfilAdminCreateForm(ProfilBaseForm):
    class Meta:
        model = ProfilAdmin
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('profil_admin')


class ProfilAdminUpdateForm(ProfilBaseForm):
    class Meta:
        model = ProfilAdmin
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'dashboard', kwargs={'pk': self.instance.pk})


class ProfilSiswaCreateForm(ProfilBaseForm):
    class Meta:
        model = ProfilSiswa
        fields = '__all__'
        exclude = ['hash',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('profil_siswa')


class ProfilSiswaUpdateForm(ProfilBaseForm):
    class Meta:
        model = ProfilSiswa
        fields = '__all__'
        exclude = ['hash',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'dashboard', kwargs={'pk': self.instance.pk})


class ProfilGuruUpdateForm(ProfilBaseForm):
    class Meta:
        model = ProfilGuru
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'dashboard', kwargs={'pk': self.instance.pk})


class ProfilGuruCreateForm(ProfilBaseForm):
    class Meta:
        model = ProfilGuru
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('profil_guru')


class AngkatanBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))


class AngkatanCreateForm(AngkatanBaseForm):
    tahun_ajaran = forms.TypedChoiceField(
        coerce=int, choices=[], initial=current_year, empty_value=None)

    class Meta:
        model = Angkatan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('dashboard')

        existing_years = Angkatan.objects.values_list(
            'tahun_ajaran', flat=True)
        year_choices = [("", "Pilih Tahun Ajaran")]
        year_choices += [(year, year) for year in range(
            1984, current_year() + 1) if year not in existing_years]
        self.fields['tahun_ajaran'].choices = year_choices


class AngkatanUpdateForm(AngkatanBaseForm):
    tahun_ajaran = forms.TypedChoiceField(
        coerce=int, choices=[], initial=current_year, empty_value=None)

    class Meta:
        model = Angkatan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'dashboard', kwargs={'pk': self.instance.pk})

        existing_years = Angkatan.objects.values_list(
            'tahun_ajaran', flat=True)
        year_choices = [("", "Pilih Tahun Ajaran")]
        year_choices += [(year, year) for year in range(
            # Check if the update need the year of exist
            1984, current_year() + 1) if year not in existing_years]
        self.fields['tahun_ajaran'].choices = year_choices


class JadwalBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))


class JadwalCreateForm(JadwalBaseForm):
    pass


class JadwalUpdateForm(JadwalBaseForm):
    waktu = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Jadwal
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'dashboard', kwargs={'pk': self.instance.pk})


class AbsensiBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))


class AbsensiCreateForm(AbsensiBaseForm):
    waktu = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Absensi
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('dashboard')


class AbsensiUpdateForm(AbsensiBaseForm):
    waktu = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Absensi
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.helper.form_action = reverse_lazy(
                'dashboard', kwargs={'pk': self.instance.pk})
