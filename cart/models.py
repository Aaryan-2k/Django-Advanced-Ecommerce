from django.db import models
from store.models import Product,Variation

# Create your models here.
class Cart(models.Model):
    cart_id=models.CharField(max_length=100,blank=True)

class CartItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity=models.IntegerField()
    variation=models.ManyToManyField(Variation, blank=True)
    def subtotal(self):
        return self.quantity*self.product.price
