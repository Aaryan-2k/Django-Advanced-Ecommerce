from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
from cart.models import CartItem
from cart.views import get_cart
import datetime
import json

# stripe payments
from django.conf import settings
import stripe

stripe.api_key=settings.STRIPE_SECRET_KEY
from django.urls import reverse

def get_cart_total(cart):
    items=CartItem.objects.filter(cart=cart)
    total=0
    for item in items:
        total+=item.product.price * item.quantity
    tax=(2*total)/100  # 2% tax
    return total,tax,items

def place_order(request):
    current_user=request.user
    cart = get_cart(request)
    items = CartItem.objects.filter(cart=cart)
    
    if items.count()<1:
        messages.warning(request, 'Cart is empty')
        return redirect('checkout_route')
    
    total, tax,items=get_cart_total(cart)
    
    if request.method=="POST":
        payment_method = request.POST.get('payment_method', 'paypal')
        form = OrderForm(request.POST)
        
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.order_id = str(total) + str(tax) + str(current_user.id) + str(datetime.datetime.now())
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.ip = request.META.get('REMOTE_ADDR')
            data.order_total = total + tax
            data.order_tax = tax
            data.save()
            
            if payment_method == 'paypal':
                return render(request, 'order/paypal.html',{'order': data,'items': items,'subtotal': total,'tax': tax,'grand_total': total + tax,})
            elif payment_method == 'stripe':
                return render(request, 'order/stripe.html',{'order': data,'items': items,'subtotal': total,'tax': tax,'grand_total': total + tax})
            else:
                return render(request, 'order/razor.html',{'order': data,'items': items,'subtotal': total,'tax': tax,'grand_total': total + tax})
        else:
            messages.warning(request, 'Please fill valid entries in the form')
            return render(request, 'store/checkout.html')
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
        success_url='http://localhost:8000/order/success', # if payment is succesfull redirects to this link
        cancel_url='http://localhost:8000/order/failed', # else this link
    )
    return redirect(checkout_session.url)

def paypal_payment(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data sent from the frontend
            data=json.loads(request.body)
            payment_id=data.get('id')

            cart = get_cart(request)
            items = CartItem.objects.filter(cart=cart)
            
            if not items.exists():
                return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)
            
            total,tax,_= get_cart_total(cart)
            grand_total=total +tax
    
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                payment_id=payment_id,
                payment_method='paypal',
                amount=str(grand_total),
                status='completed'
            )
            
            order = Order.objects.filter(user=request.user).latest('created_at')
            order.payment = payment
            order.is_ordered = True
            order.save()
            
            # Move cart items to ordered items
            
            for item in items:
                ordered_items=OrderProduct()
                ordered_items.user=request.user
                ordered_items.product=item.product
                ordered_items.payment=payment
                ordered_items.order=order
                ordered_items.quantity=item.quantity
                ordered_items.product_price=item.product.price
                ordered_items.ordered=True
                items_variation= item.variation.all()
                ordered_items.save()
                if items_variation.exists():
                    ordered_items.variation.set(items_variation)
                ordered_items.save()

                # update stock
                product_ordered=Product.objects.get(id=item.product.id)
                product_ordered.stock-=item.quantity
                product_ordered.save()

            CartItem.objects.filter(cart=cart).delete()
            

            return JsonResponse({
                'status': 'success',
                'message': 'Payment successful',
                'redirect_url': reverse('payment_complete'),
                'order_id': order.order_id,
                'transaction_id': payment.payment_id,
            })
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"PayPal Payment Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
def payment_complete(request):
    order_id=request.GET.get('order_id')
    transaction_id=request.GET.get('transaction_id')
    return render(request, 'order/success.html', {'order_id': order_id, 'transaction_id': transaction_id})

def payment_failed(request):
    return render(request, 'order/failed.html')
