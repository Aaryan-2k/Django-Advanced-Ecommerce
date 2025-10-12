from .views import get_cart
from .models import CartItem,Cart

def cart_counter(request):
    count=0
    if request.user.is_authenticated:
        cart=Cart.objects.get(user=request.user)
    else:
        cart=get_cart(request)

    items=CartItem.objects.filter(cart=cart)
    for i in items:
        count+=i.quantity
    return dict(cart_counter=count)


