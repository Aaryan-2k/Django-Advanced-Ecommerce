from django.shortcuts import render,get_object_or_404, redirect
from .models import Cart,CartItem
from store.models import Product

# Create your views here.
def get_cart(request):
    session_id=request.session.session_key
    if not session_id:
        session_id=request.session.create()
    try:
        cart=Cart.objects.get(cart_id=session_id)
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=session_id)
    return cart

def add_cart(request,product_id):
    product_to_add=get_object_or_404(Product,id=product_id)
    cart=get_cart(request)
    
    try:
        cart_item=CartItem.objects.get(cart=cart, product=product_to_add)
        cart_item.quantity+=1
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(product=product_to_add, cart=cart, quantity=1)

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
    print(items)
    for i in items:
        total_price+=(i.quantity*i.product.price)
    
    tax=(2*total_price)/100
    grand_total=tax+total_price
    return render(request, 'store/cart.html', {'items':items,'grand_total':grand_total, 'total_price':total_price,'tax':tax})

def remove_cart(request,product_id):
    cart=get_cart(request)
    product=get_object_or_404(Product, id=product_id)
    item=CartItem.objects.get(product=product, cart=cart)
    item.delete()
    return redirect('/cart')

def quantity_decrease(request,product_id):
    cart=get_cart(request)
    product=get_object_or_404(Product, id=product_id)
    item=CartItem.objects.get(product=product, cart=cart)
    if item.quantity>1:
        item.quantity-=1  
        item.save()
    else:
        item.delete()
    return redirect('/cart')
