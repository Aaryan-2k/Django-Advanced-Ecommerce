from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
from .models import Order
from cart.models import CartItem
from cart.views import get_cart
from django.http import HttpResponse
import datetime

#stripe payments
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# palpal integration
import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})


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
        payment=request.POST['payment_method']
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
            if payment=='paypal':
                return render(request,'order/paypal.html',{'order':data,'items':items})
            elif payment=='stripe':
                return render(request,'order/stripe.html',{'order':data,'items':items})
            else:
                return render(request,'order/razor.html',{'order':data,'items':items})
        else:
            messages.warning(request, 'Please fill valid entries in the form')
            return render(request,'store/checkout.html')
    return render(request, 'order/')

def payment(request):
    return render(request,'order/payments.html')

@login_required
def stripe_payment(request):
    cart=get_cart(request)
    products_incart=CartItem.objects.filter(cart=cart)

    # inserting the details about all the cart items in the list
    all_the_items=[]
    for item in products_incart:
        all_the_items.append({
                  'price_data': {
                    'currency': 'usd',
                    'unit_amount': item.product.price * 100, #we need to pass the amount in cents in stripe
                    'product_data': {
                        'name': item.product.product_name,
                        'images': [item.product.image]
                    },
                },
                'quantity': item.quantity,
            })

    # Stripe Configurtion
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=all_the_items,
        metadata = {
            'user_email': request.user.email,
            'cart_id': cart.id,
        },
        mode='payment',
        success_url='https://legendary-pancake-q7qx44q5v4xxcx6qw.github.dev/order/success', # if payment is succesfull redirects to this link
        cancel_url='https://legendary-pancake-q7qx44q5v4xxcx6qw.github.dev/order/failed', # else this link
    )
    return redirect(checkout_session.url)

def paypal_payment(request):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('execute_payment_route')),
            "cancel_url": request.build_absolute_uri(reverse('payment_failed')),
        },
        "transactions": [
            {
                "amount": {
                    "total": "10.00",  # Total amount in USD
                    "currency": "USD",
                },
                "description": "Payment for Product/Service",
            }
        ],
    })

    if payment.create():
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    else:
        return render(request, 'order/failed.html')

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return render(request, 'order/success.html')
    else:
        return render(request, 'order/failed.html')
    
def payment_complete(request):
    return render(request,'order/success.html')

def payment_failed(request):
    return render(request, 'order/failed.html')

