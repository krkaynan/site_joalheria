from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.decorators import login_required
from store.models import Product, Variation
from .models import Cart, CartItem
from decimal import Decimal, ROUND_HALF_UP
import math 
import requests

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id): 
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # Se user for logado
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product = product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
            
        is_cart_item_exists = CartItem.objects.filter(product = product, user = current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product, user = current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_Variation = item.variations.all()
                ex_var_list.append(list(existing_Variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                # aumentar a quantidade de itens no carrinho
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product = product, id = item_id )
                item.quantily += 1
                item.save()
            else:
                # criar novo item no carrinho
                item = CartItem.objects.create(product = product, quantily = 1, user = current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantily = 1,
                user = current_user
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    
    # Se não for logado
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product = product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
                
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
                )
        cart.save()
        
        is_cart_item_exists = CartItem.objects.filter(product = product, cart = cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_Variation = item.variations.all()
                ex_var_list.append(list(existing_Variation))
                id.append(item.id)
            print(ex_var_list)
            
            if product_variation in ex_var_list:
                # aumentar a quantidade de itens no carrinho
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product = product, id = item_id )
                item.quantily += 1
                item.save()
            else:
                # criar novo item no carrinho
                item = CartItem.objects.create(product = product, quantily = 1, cart = cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantily = 1,
                cart = cart
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect ('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request)) 
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantily > 1:
            cart_item.quantily -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remover_cart_item(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantily=0, cart_items=None):
    try:
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantily)
            quantily += cart_item.quantily
        grand_total = total 
    except Cart.DoesNotExist:
        pass
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total': total,
        'quantily': quantily,
        'cart_items': cart_items,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

def cep_normalizado(cep: str):
    return ''.join(filter(str.isdigit, str(cep) or ''))

def buscar_viacep(cep: str):
    cep = cep_normalizado(cep)
    if len(cep) != 8:
        return None
    try:
        r = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=6)
        if r.status_code == 200:
            data = r.json()
            if data.get('erro'):
                return None
            return data
    except requests.RequestException:
        return None
    return None

def geocode_por_viacep_data(viacep_data):
    parts = []
    if viacep_data.get('logradouro'):
        parts.append(viacep_data['logradouro'])
    if viacep_data.get('bairro'):
        parts.append(viacep_data['bairro'])
    if viacep_data.get('localidade'):
        parts.append(viacep_data['localidade'])
    if viacep_data.get('uf'):
        parts.append(viacep_data['uf'])
    q = ', '.join(parts) + ', Brasil'

    params = {'q': q, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'MinhaLojaExemplo/1.0 (seu-email@dominio.com)'}  # substitua seu contato
    try:
        r = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers, timeout=8)
        if r.status_code == 200:
            arr = r.json()
            if arr:
                lat = float(arr[0]['lat'])
                lon = float(arr[0]['lon'])
                return lat, lon
    except requests.RequestException:
        return None
    return None

def distancia_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c  

def calcular_frete(request):
    shipping_price = None
    distance_km = None
    error = None

    total = Decimal('0.00')
    cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request))

    for item in cart_items:
        qty = getattr(item, 'quantily', None) or getattr(item, 'quantity', 1)
        price = getattr(item.product, 'price', 0)
        line_total = Decimal(str(price)) * Decimal(str(qty))
        total += line_total

    if request.method == 'POST':
        dest_cep = request.POST.get('cep', '').strip()
        if not dest_cep:
            error = "Informe o CEP de destino."
        else:
            origin_cep = getattr(settings, 'ORIGIN_CEP', None)
            if not origin_cep:
                error = "CEP de origem não configurado (settings.ORIGIN_CEP)."
            else:
                origin_viacep = buscar_viacep(origin_cep)
                dest_viacep = buscar_viacep(dest_cep)

                if not origin_viacep or not dest_viacep:
                    error = "Não foi possível consultar o CEP. Verifique o CEP e tente novamente."
                else:
                    origin_coords = geocode_por_viacep_data(origin_viacep)
                    dest_coords = geocode_por_viacep_data(dest_viacep)

                    if not origin_coords or not dest_coords:
                        error = "Não foi possível obter coordenadas para o CEP. Tente outro CEP."
                    else:
                        dist = Decimal(str(distancia_haversine(origin_coords[0], origin_coords[1],
                                                              dest_coords[0], dest_coords[1])))
                        distance_km = dist.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                        # Fórmula de frete somente por distância 
                        base_fee = Decimal('8.00')     # taxa fixa
                        per_km = Decimal('0.50')       # por km
                        shipping_price = (base_fee + (per_km * distance_km)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    grand_total = (total + (shipping_price or Decimal('0.01'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    context = {
        'cart_items': cart_items,
        'total': total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'shipping_price': shipping_price,
        'grand_total': grand_total,
        'distance_km': distance_km,
        'error': error,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantily=0, cart_items=None):
    try:
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active = True)
            
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantily)
            quantily += cart_item.quantily
        grand_total = total
    except Cart.DoesNotExist:
        pass
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total': total,
        'quantily': quantily,
        'cart_items': cart_items,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)