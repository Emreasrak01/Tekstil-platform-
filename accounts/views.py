from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from products.models import Category, Product
from .forms import FactoryRegistrationForm, StoreRegistrationForm


def home(request):
    products = Product.objects.filter(is_active=True).select_related(
        'category', 'factory'
    )[:8]
    categories = Category.objects.all()[:8]
    favorite_ids = set()

    if request.user.is_authenticated and request.user.user_type == 'store':
        from store.models import Favorite
        favorite_ids = set(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'favorite_ids': favorite_ids,
    })


def register_choice(request):
    return render(request, 'accounts/register_choice.html')


def factory_register(request):
    if request.method == 'POST':
        form = FactoryRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Fabrika kaydınız oluşturuldu. Admin onayı bekleniyor.')
            login(request, user)
            return redirect('factory_dashboard')
    else:
        form = FactoryRegistrationForm()

    return render(request, 'accounts/factory_register.html', {'form': form})


def store_register(request):
    if request.method == 'POST':
        form = StoreRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Kayıt başarılı. Hoş geldiniz.')
            login(request, user)
            return redirect('store_dashboard')
    else:
        form = StoreRegistrationForm()

    return render(request, 'accounts/store_register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.user_type == 'factory':
                return redirect('factory_dashboard')
            return redirect('store_dashboard')

        messages.error(request, 'Kullanıcı adı veya şifre hatalı.')

    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('home')
