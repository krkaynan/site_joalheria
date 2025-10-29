from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render

def guia(request):
    context = {
        'title': 'Guia de Produtos',
    }
    return render(request, 'store/guia.html', context)

def store(request, category_slug = None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available = True)
        paginator = Paginator(products, 6) # Quantidade de produtos por categoria
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        # calcula a parcela (10x sem juros) para cada produto da página
        for p in paged_products:
            try:
                # converte para Decimal com segurança (caso price seja float/str/Decimal)
                price = Decimal(str(p.price))
                p.installment = (price / Decimal(10)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except Exception:
                p.installment = None
        product_count = products.count()
    else: 
        products = Product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products, 9) # Quantidade de produtos por pagina
        page = request.GET.get('page')
        paged_products = paginator.get_page(page) 
        # calcula a parcela (10x sem juros) para cada produto da página
        for p in paged_products:
            try:
                # converte para Decimal com segurança (caso price seja float/str/Decimal)
                price = Decimal(str(p.price))
                p.installment = (price / Decimal(10)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except Exception:
                p.installment = None

        product_count = products.count()
    
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
    except Exception as e:
        raise e
    
    try:
        price = Decimal(str(single_product.price))
        installment = (price / Decimal(10)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # valor bruto (Decimal) e string formatada para exibição em PT-BR (troca . por ,)
        single_product.installment = installment
        single_product.installment_display = f"R$ {format(installment, '0.2f')}".replace('.', ',')
    except Exception:
        single_product.installment = None
        single_product.installment_display = None
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(  product_name__icontains=keyword))
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    } 
    return render(request, 'store/store.html', context)