from django import forms
from django.utils.text import slugify

from .models import Category, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'stock', 'image', 'is_active']
        labels = {
            'category': 'Kategori',
            'name': 'Ürün Adı',
            'description': 'Açıklama',
            'price': 'Fiyat (₺)',
            'stock': 'Stok Adedi',
            'image': 'Ürün Görseli',
            'is_active': 'Aktif',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: Pamuklu tişört',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Malzeme, kullanım alanı, beden/renk bilgisi...',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = 'Kategori seçin'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name, allow_unicode=True)
            original_slug = instance.slug
            counter = 1
            while Product.objects.filter(slug=instance.slug).exists():
                instance.slug = f'{original_slug}-{counter}'
                counter += 1

        if commit:
            instance.save()
        return instance
