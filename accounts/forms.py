from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import FactoryProfile, StoreProfile, User


class FactoryRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='E-posta')
    phone = forms.CharField(max_length=15, required=True, label='Telefon')
    company_name = forms.CharField(max_length=200, label='Şirket Adı')
    tax_number = forms.CharField(max_length=20, label='Vergi Numarası')
    tax_office = forms.CharField(max_length=100, label='Vergi Dairesi')
    tax_certificate = forms.FileField(label='Vergi Levhası (PDF/JPG)')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Adres')
    city = forms.CharField(max_length=50, label='Şehir')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'Kullanıcı adı',
            'email': 'ornek@firma.com',
            'phone': '05XX XXX XX XX',
            'company_name': 'Şirket adı',
            'tax_number': 'Vergi numarası',
            'tax_office': 'Vergi dairesi',
            'address': 'Açık adres',
            'city': 'Şehir',
        }
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs.setdefault('placeholder', placeholders.get(field_name, ''))
            if field_name == 'tax_certificate':
                field.widget.attrs['accept'] = '.pdf,.jpg,.jpeg,.png'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'factory'
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']

        if commit:
            user.save()
            FactoryProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                tax_number=self.cleaned_data['tax_number'],
                tax_office=self.cleaned_data['tax_office'],
                tax_certificate=self.cleaned_data['tax_certificate'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
            )
        return user


class StoreRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='E-posta')
    phone = forms.CharField(max_length=15, required=False, label='Telefon')
    store_name = forms.CharField(max_length=200, required=False, label='Mağaza Adı (Opsiyonel)')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'Kullanıcı adı',
            'email': 'ornek@magaza.com',
            'phone': '05XX XXX XX XX',
            'store_name': 'Mağaza adı',
        }
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs.setdefault('placeholder', placeholders.get(field_name, ''))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'store'
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')

        if commit:
            user.save()
            StoreProfile.objects.create(
                user=user,
                store_name=self.cleaned_data.get('store_name', ''),
            )
        return user
