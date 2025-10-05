from .views import get_cart
from .models import CartItem

def cart_counter(request):
    count=0
    items=CartItem.objects.filter(cart=get_cart(request))
    for i in items:
        count+=i.quantity
    return dict(cart_counter=count)


