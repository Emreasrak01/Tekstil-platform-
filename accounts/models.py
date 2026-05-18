from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('factory', 'Fabrika'),
        ('store', 'Mağaza'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)

    class Meta:
        db_table = 'users'


class FactoryProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='factory_profile')
    company_name = models.CharField(max_length=200, verbose_name='Şirket Adı')
    tax_number = models.CharField(max_length=20, unique=True, verbose_name='Vergi Numarası')
    tax_office = models.CharField(max_length=100, verbose_name='Vergi Dairesi')
    tax_certificate = models.FileField(upload_to='tax_certificates/', verbose_name='Vergi Levhası')
    address = models.TextField(verbose_name='Adres')
    city = models.CharField(max_length=50, verbose_name='Şehir')
    is_verified = models.BooleanField(default=False, verbose_name='Onaylandı')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fabrika Profili'
        verbose_name_plural = 'Fabrika Profilleri'

    def __str__(self):
        return self.company_name


class StoreProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store_profile')
    store_name = models.CharField(max_length=200, verbose_name='Mağaza Adı', blank=True)
    address = models.TextField(verbose_name='Teslimat Adresi', blank=True)
    city = models.CharField(max_length=50, verbose_name='Şehir', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mağaza Profili'
        verbose_name_plural = 'Mağaza Profilleri'

    def __str__(self):
        return self.store_name or self.user.username
