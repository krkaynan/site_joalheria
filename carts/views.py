from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
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
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try: 
        cart_item = CartItem.objects.get(product = product, cart=cart, id=cart_item_id)
        if cart_item.quantily > 1:
            cart_item.quantily -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remover_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantily=0, cart_items=None):
    grand_total = 0
    try:
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