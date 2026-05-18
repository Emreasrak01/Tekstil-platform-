from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Category, Product


def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related(
        'category', 'factory'
    ).order_by('-created_at')
    category_filter = request.GET.get('category', '')

    if category_filter:
        products = products.filter(category_id=category_filter)

    products = products[:20]
    favorite_ids = set()

    if request.user.is_authenticated and request.user.user_type == 'store':
        from store.models import Favorite
        favorite_ids = set(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'products/home.html', {
        'categories': categories,
        'products': products,
        'category_filter': category_filter,
        'favorite_ids': favorite_ids,
    })


@login_required
def add_product(request):
    if request.user.user_type != 'factory':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.factory = request.user
            product.save()
            messages.success(request, 'Ürün başarıyla eklendi.')
            return redirect('factory_dashboard')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


@login_required
def product_list(request):
    if request.user.user_type != 'factory':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('home')

    products = Product.objects.filter(factory=request.user).select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_filter:
        products = products.filter(category_id=category_filter)

    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
    })


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, factory=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla güncellendi.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, factory=request.user)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Ürün başarıyla silindi.')
        return redirect('product_list')

    return render(request, 'products/delete_confirm.html', {'product': product})


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'factory'),
        slug=slug,
        is_active=True,
    )
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
    ).select_related('category', 'factory').exclude(id=product.id)[:4]
    is_favorite = False

    if request.user.is_authenticated and request.user.user_type == 'store':
        from store.models import Favorite
        favorite_ids = set(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
        is_favorite = product.id in favorite_ids
    else:
        favorite_ids = set()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'is_favorite': is_favorite,
        'favorite_ids': favorite_ids,
    })
