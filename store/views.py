from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from .models import Product
from cart.models import CartItem
from category.models import Category
from cart.views import get_cart
from django.core.paginator import Paginator
from django.db.models import Q

def Store(request, slug=None):
    if slug!=None:
        category=get_object_or_404(Category, slug=slug)
        products=Product.objects.filter(category=category)
    else:
        products=Product.objects.all()

    paginator=Paginator(products,6) #6 is the number of products per page
    page=request.GET.get('page')
    paged_products=paginator.get_page(page)

    return render(request,'store/store.html', {"products":paged_products})


def product_detail(request,slug,product_slug):
    product=get_object_or_404(Product, slug=product_slug)
    cart=get_cart(request)
    in_cart=False
    try:
        in_cart=CartItem.objects.filter(cart=cart,product=product).exists()
    except CartItem.DoesNotExist as e:
        print(e)

    return render(request,'store/product_detail.html', {'product':product,'in_cart':in_cart})


def search(request):
    keyword=''
    if 'searchkey' in request.GET:
        keyword=request.GET.get('searchkey')
    products=Product.objects.filter(Q(product_name__icontains=keyword)|Q(description__icontains=keyword))

    #pagination
    paginator=Paginator(products,6)
    page=request.GET.get('page')
    paged_products=paginator.get_page(page)
    return render(request,'store/store.html', {'products':paged_products})
