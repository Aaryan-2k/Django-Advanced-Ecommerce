from django.shortcuts import render,get_object_or_404, redirect
from .models import Cart,CartItem
from store.models import Product,Variation

# Create your views here.
def get_cart(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    try:
        cart=Cart.objects.get(cart_id=session_id)
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=session_id)
    return cart

def add_cart(request,product_id):
    product_to_add=get_object_or_404(Product,id=product_id)
    cart=get_cart(request)

    product_variantion=[]
    for key in request.POST:
        value=request.POST.get(key)
        try:
            variant=Variation.objects.get(product=product_to_add, category__iexact=key,category_value__iexact=value)
            product_variantion.append(variant)
        except Variation.DoesNotExist:
            pass

    product_in_cart=CartItem.objects.filter(product=product_to_add,cart=cart).exists()
    if product_in_cart:
        product_in_cart=CartItem.objects.filter(product=product_to_add,cart=cart)
        added_to_cart=False
        for i in product_in_cart:
            if set(product_variantion)==set(i.variation.all()):
                i.quantity+=1
                i.save()
                added_to_cart=True
                break
        if added_to_cart==False:
            item=CartItem.objects.create(product=product_to_add, cart=cart, quantity=1)
            item.variation.add(*product_variantion)
    else:
        item=CartItem.objects.create(product=product_to_add, cart=cart, quantity=1)
        item.variation.add(*product_variantion)
    return redirect('/cart')

def cart(request):
    tax=0
    total_price=0
    cart=get_cart(request)
    try:
        items=CartItem.objects.filter(cart=cart)
    except CartItem.DoesNotExist as e:
        print(e)
        items={}
    for i in items:
        total_price+=(i.quantity*i.product.price)
    
    tax=(2*total_price)/100
    grand_total=tax+total_price
    return render(request, 'store/cart.html', {'items':items,'grand_total':grand_total, 'total_price':total_price,'tax':tax})

def remove_cart(request,item_id):
    try:
        item_to_remove=CartItem.objects.get(id=item_id)
    except:
        pass
    item_to_remove.delete()
    return redirect('/cart')

def quantity_increase(request,item_id):
    try:
        item_to_increase=CartItem.objects.get(id=item_id)
        item_to_increase.quantity+=1
        item_to_increase.save()
    except:
        pass
    return redirect('/cart')

def quantity_decrease(request,item_id):
    try:
        item_to_decrease=CartItem.objects.get(id=item_id)
    except:
        pass

    if item_to_decrease.quantity>1:
        item_to_decrease.quantity-=1  
        item_to_decrease.save()
    else:
        item_to_decrease.delete()
    return redirect('/cart')
