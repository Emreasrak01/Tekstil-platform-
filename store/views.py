from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import StoreProfile
from products.models import Category, Product
from .models import CartItem, Favorite


def _store_required(request):
    if request.user.user_type != 'store':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return False
    return True


@login_required
def store_dashboard(request):
    if not _store_required(request):
        return redirect('home')

    products = Product.objects.filter(is_active=True).select_related(
        'category', 'factory'
    ).order_by('-created_at')
    categories = Category.objects.all()
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '')
    sort = request.GET.get('sort', 'newest')

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_filter:
        products = products.filter(category_id=category_filter)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    favorite_ids = set(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    cart_count = CartItem.objects.filter(user=request.user).count()

    return render(request, 'store/dashboard.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'sort': sort,
        'favorite_ids': favorite_ids,
        'cart_count': cart_count,
    })


@login_required
def store_cart(request):
    if not _store_required(request):
        return redirect('home')

    cart_items = CartItem.objects.filter(user=request.user).select_related(
        'product', 'product__factory', 'product__category'
    )
    total_price = sum((item.line_total for item in cart_items), Decimal('0'))

    return render(request, 'store/store_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


@login_required
def store_orders(request):
    if not _store_required(request):
        return redirect('home')

    return render(request, 'store/orders.html', {
        'store_profile': request.user.store_profile,
        'orders': [],
    })


@login_required
def store_favorites(request):
    if not _store_required(request):
        return redirect('home')

    favorite_products = Product.objects.filter(
        favorited_by__user=request.user,
        is_active=True,
    ).select_related('category', 'factory').order_by('-favorited_by__created_at')

    return render(request, 'store/favorites.html', {
        'store_profile': request.user.store_profile,
        'favorite_products': favorite_products,
        'favorite_ids': set(favorite_products.values_list('id', flat=True)),
    })


@login_required
def store_settings(request):
    if not _store_required(request):
        return redirect('home')

    store_profile, _ = StoreProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.email = request.POST.get('email', request.user.email)
        request.user.phone = request.POST.get('phone', request.user.phone)
        request.user.save(update_fields=['email', 'phone'])

        store_profile.store_name = request.POST.get('store_name', store_profile.store_name)
        store_profile.city = request.POST.get('city', store_profile.city)
        store_profile.address = request.POST.get('address', store_profile.address)
        store_profile.save(update_fields=['store_name', 'city', 'address'])

        messages.success(request, 'Ayarlar başarıyla güncellendi.')
        return redirect('store_settings')

    return render(request, 'store/settings.html', {
        'store_profile': store_profile,
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    if not _store_required(request):
        return redirect('login')

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    quantity = max(1, int(request.POST.get('quantity', 1)))

    if product.stock <= 0:
        messages.error(request, 'Bu ürün şu anda stokta yok.')
        return redirect(request.POST.get('next') or 'store_dashboard')

    quantity = min(quantity, product.stock)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity},
    )

    if not created:
        cart_item.quantity = min(cart_item.quantity + quantity, product.stock)
        cart_item.save(update_fields=['quantity'])

    messages.success(request, 'Ürün sepete eklendi.')
    return redirect(request.POST.get('next') or 'store_cart')


@login_required
@require_POST
def update_cart_qty(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        item.delete()
        messages.success(request, 'Ürün sepetten kaldırıldı.')
        return redirect('store_cart')

    item.quantity = min(quantity, item.product.stock)
    item.save(update_fields=['quantity'])
    messages.success(request, 'Sepet güncellendi.')
    return redirect('store_cart')


@login_required
@require_POST
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    item.delete()
    messages.success(request, 'Ürün sepetten kaldırıldı.')
    return redirect('store_cart')


@login_required
@require_POST
def toggle_favorite(request, product_id):
    if not _store_required(request):
        return redirect('login')

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, 'Ürün favorilere eklendi.')
    else:
        favorite.delete()
        messages.success(request, 'Ürün favorilerden çıkarıldı.')

    return redirect(request.POST.get('next') or 'store_dashboard')


@login_required
@require_POST
def remove_favorite(request, product_id):
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, 'Ürün favorilerden çıkarıldı.')
    return redirect('store_favorites')
