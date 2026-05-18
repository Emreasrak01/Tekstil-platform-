from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, FactoryProfile, StoreProfile

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type_badge', 'phone', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Kullanıcı Tipi', {'fields': ('user_type',)}),
        ('İzinler', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Önemli Tarihler', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'phone', 'password1', 'password2'),
        }),
    )
    
    def user_type_badge(self, obj):
        colors = {
            'factory': '#28a745',
            'store': '#007bff'
        }
        labels = {
            'factory': 'Fabrika',
            'store': 'Mağaza'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.user_type, '#6c757d'),
            labels.get(obj.user_type, obj.user_type)
        )
    user_type_badge.short_description = 'Kullanıcı Tipi'


@admin.register(FactoryProfile)
class FactoryProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'get_username', 'tax_number', 'city', 'verification_badge', 'created_at']
    list_filter = ['is_verified', 'city', 'created_at']
    search_fields = ['company_name', 'tax_number', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'tax_certificate_preview']
    actions = ['approve_factories', 'reject_factories']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Kullanıcı Bilgisi', {
            'fields': ('user',)
        }),
        ('Şirket Bilgileri', {
            'fields': ('company_name', 'tax_number', 'tax_office', 'tax_certificate', 'tax_certificate_preview')
        }),
        ('Adres Bilgileri', {
            'fields': ('address', 'city')
        }),
        ('Onay Durumu', {
            'fields': ('is_verified', 'created_at'),
            'classes': ('wide',)
        }),
    )
    
    def get_username(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    get_username.short_description = 'Kullanıcı Adı'
    
    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">✓ Onaylı</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">✗ Bekliyor</span>'
        )
    verification_badge.short_description = 'Onay Durumu'
    
    def tax_certificate_preview(self, obj):
        if obj.tax_certificate:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 200px; max-width: 300px;" /></a>',
                obj.tax_certificate.url,
                obj.tax_certificate.url
            )
        return "Dosya yüklenmemiş"
    tax_certificate_preview.short_description = 'Vergi Levhası Önizleme'
    
    def approve_factories(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} fabrika onaylandı.')
    approve_factories.short_description = "Seçili fabrikaları onayla"
    
    def reject_factories(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} fabrikanın onayı kaldırıldı.')
    reject_factories.short_description = "Seçili fabrikaların onayını kaldır"


@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ['get_store_name', 'get_username', 'city', 'created_at']
    list_filter = ['city', 'created_at']
    search_fields = ['store_name', 'user__username', 'user__email', 'city']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Kullanıcı Bilgisi', {
            'fields': ('user',)
        }),
        ('Mağaza Bilgileri', {
            'fields': ('store_name', 'address', 'city')
        }),
        ('Kayıt Tarihi', {
            'fields': ('created_at',)
        }),
    )
    
    def get_username(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    get_username.short_description = 'Kullanıcı Adı'
    
    def get_store_name(self, obj):
        return obj.store_name or '-'
    get_store_name.short_description = 'Mağaza Adı'