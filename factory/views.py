from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from products.models import Product


def _factory_required(request):
    if request.user.user_type != 'factory':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return False
    return True


@login_required
def factory_dashboard(request):
    if not _factory_required(request):
        return redirect('home')

    products = Product.objects.filter(factory=request.user).select_related('category')
    total_products = products.count()
    active_products = products.filter(is_active=True).count()
    low_stock_products = products.filter(stock__lt=10, stock__gt=0).count()
    out_of_stock_products = products.filter(stock=0).count()

    return render(request, 'factory/dashboard.html', {
        'products': products[:10],
        'factory_profile': request.user.factory_profile,
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
    })


@login_required
def factory_orders(request):
    if not _factory_required(request):
        return redirect('home')

    return render(request, 'factory/orders.html', {
        'factory_profile': request.user.factory_profile,
    })


@login_required
def factory_reports(request):
    if not _factory_required(request):
        return redirect('home')

    products = Product.objects.filter(factory=request.user).select_related('category')

    return render(request, 'factory/reports.html', {
        'factory_profile': request.user.factory_profile,
        'products': products,
    })


@login_required
def factory_settings(request):
    if not _factory_required(request):
        return redirect('home')

    if request.method == 'POST':
        profile = request.user.factory_profile
        request.user.email = request.POST.get('email', request.user.email)
        request.user.phone = request.POST.get('phone', request.user.phone)
        request.user.save(update_fields=['email', 'phone'])

        profile.company_name = request.POST.get('company_name', profile.company_name)
        profile.tax_office = request.POST.get('tax_office', profile.tax_office)
        profile.city = request.POST.get('city', profile.city)
        profile.address = request.POST.get('address', profile.address)
        profile.save(update_fields=['company_name', 'tax_office', 'city', 'address'])

        messages.success(request, 'Ayarlar başarıyla güncellendi.')
        return redirect('factory_settings')

    return render(request, 'factory/settings.html', {
        'factory_profile': request.user.factory_profile,
    })
