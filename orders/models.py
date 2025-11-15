from django.db import models
from accounts.models import Account
from store.models import Product, Variation

# Create your models here.

class Payment(models.Model):
    user=models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=100)
    payment_method=models.CharField(max_length=100)
    amount=models.CharField(max_length=100)
    status=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

class Order(models.Model):
    Order_Status=(
        ('New','New'),
        ('Accepted','Accepted'),
        ('Cancelled','Cancelled'),
        ('Completed','Completed'),
    )
    user=models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    order_id=models.CharField(max_length=100, unique=True)
    order_status=models.CharField(max_length=100, choices=Order_Status, default='New')
    payment=models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    phone=models.CharField(max_length=100)
    address_line_1=models.CharField(max_length=250)
    address_line_2=models.CharField(max_length=250, blank=True)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    country=models.CharField(max_length=100)
    ip=models.CharField(max_length=100, blank=True)
    order_total=models.FloatField()
    order_tax=models.FloatField()    
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.first_name

class OrderProduct(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment, on_delete=models.CASCADE)
    user=models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    variation=models.ManyToManyField(Variation, blank=True)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.product.product_name