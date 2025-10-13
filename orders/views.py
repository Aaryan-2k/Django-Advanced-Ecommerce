from django.shortcuts import render
from .forms import OrderForm
from .models import Order
from cart.models import CartItem
from cart.views import get_cart
from django.http import HttpResponse
import datetime

# Create your views here.

def place_order(request):
    current_user=request.user
    cart=get_cart(request)
    items=CartItem.objects.filter(cart=cart)
    if items.count()<1:
        messages.warning(request, 'Cart is empty')
        return redirect('checkout_route')
    total=0
    tax=0
    for item in items:
        total+=item.product.price*item.quantity
    tax=(2*total)/100 # 2% tax

    if request.method=="POST":
        form=OrderForm(request.POST)
        if form.is_valid():
            data=Order()
            data.user=current_user
            data.order_id=str(total)+str(tax)+str(current_user.id)+str(datetime.datetime.now())
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.city=form.cleaned_data['city']
            data.state=form.cleaned_data['state']
            data.country=form.cleaned_data['country']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.ip=request.META.get('REMOTE_ADDR')
            data.order_total=total+tax
            data.order_tax=tax
            data.save()
            return render(request,'order/payments.html',{'order':data,'items':items})
        else:
            messages.warning(request, 'Please fill valid entries in the form')
            return render(request,'store/checkout.html')
    return render(request, 'order/')

def payment(request):
    return render(request,'order/payments.html')