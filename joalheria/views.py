from django.shortcuts import render
from store.models import Product
from decimal import Decimal, ROUND_HALF_UP

# Criando os links das paginas html
def home(request):
    products = Product.objects.all().filter(is_available = True)
    
    # calcula a parcela (10x sem juros) para cada produto
    for p in products:
        try:
            price = Decimal(str(p.price))
            p.installment = (price / Decimal('10')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            p.installment = None
    
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)