from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.urls import reverse
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'image_preview', 'product_count', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'image_preview_large']
    ordering = ['name']
    
    fieldsets = (
        ('Kategori Bilgileri', {
            'fields': ('name', 'slug')
        }),
        ('Görsel', {
            'fields': ('image', 'image_preview_large')
        }),
        ('Diğer', {
            'fields': ('created_at',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "Görsel yok"
    image_preview.short_description = 'Görsel'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: contain;" />',
                obj.image.url
            )
        return "Görsel yüklenmemiş"
    image_preview_large.short_description = 'Görsel Önizleme'
    
    def product_count(self, obj):
        count = obj.products.count()
        url = reverse('admin:products_product_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} ürün</a>', url, count)
    product_count.short_description = 'Ürün Sayısı'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']
    fields = ['image', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return ""
    image_preview.short_description = 'Önizleme'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'get_factory', 'category', 'price_display', 
                    'stock_badge', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at', 'factory__factory_profile__is_verified']
    search_fields = ['name', 'factory__username', 'factory__factory_profile__company_name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    list_editable = ['is_active']
    actions = ['activate_products', 'deactivate_products', 'add_stock']
    inlines = [ProductImageInline]
    ordering = ['-created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'factory', 'category')
        }),
        ('Ürün Detayları', {
            'fields': ('description', 'price', 'stock')
        }),
        ('Görseller', {
            'fields': ('image', 'image_preview_large')
        }),
        ('Durum', {
            'fields': ('is_active',),
            'classes': ('wide',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "Görsel yok"
    image_preview.short_description = 'Görsel'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; object-fit: contain; border-radius: 8px;" />',
                obj.image.url
            )
        return "Görsel yüklenmemiş"
    image_preview_large.short_description = 'Ürün Görseli Önizleme'
    
    def get_factory(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.factory.id])
        factory_name = obj.factory.factory_profile.company_name if hasattr(obj.factory, 'factory_profile') else obj.factory.username
        return format_html('<a href="{}">{}</a>', url, factory_name)
    get_factory.short_description = 'Fabrika'
    
    def price_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">{:.2f} ₺</span>',
            obj.price
        )
    price_display.short_description = 'Fiyat'
    
    def stock_badge(self, obj):
        if obj.stock == 0:
            color = '#dc3545'
            text = 'Stokta Yok'
        elif obj.stock < 10:
            color = '#ffc107'
            text = f'{obj.stock} adet'
        else:
            color = '#28a745'
            text = f'{obj.stock} adet'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, text
        )
    stock_badge.short_description = 'Stok'
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">✓ Aktif</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">✗ Pasif</span>'
        )
    status_badge.short_description = 'Durum'
    status_badge.admin_order_field = 'is_active'
    
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} ürün aktif hale getirildi.')
    activate_products.short_description = "Seçili ürünleri aktif et"
    
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} ürün pasif hale getirildi.')
    deactivate_products.short_description = "Seçili ürünleri pasif et"
    
    def add_stock(self, request, queryset):
        for product in queryset:
            product.stock += 10
            product.save()
        self.message_user(request, f'{queryset.count()} ürüne 10 adet stok eklendi.')
    add_stock.short_description = "Seçili ürünlere +10 stok ekle"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'get_product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at', 'image_preview_large']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "Görsel yok"
    image_preview.short_description = 'Önizleme'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 500px; max-height: 500px; object-fit: contain;" />',
                obj.image.url
            )
        return "Görsel yüklenmemiş"
    image_preview_large.short_description = 'Görsel Önizleme'
    
    def get_product(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    get_product.short_description = 'Ürün'