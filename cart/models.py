from django.db import models
from store.models import Product,Variation
from accounts.models import Account

# Create your models here.
class Cart(models.Model):
    cart_id=models.CharField(max_length=100,blank=True)
    user=models.OneToOneField(Account, on_delete=models.CASCADE, null=True)

class CartItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity=models.IntegerField()
    variation=models.ManyToManyField(Variation, blank=True)
    def subtotal(self):
        return self.quantity*self.product.price
