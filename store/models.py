from django.db import models
from category.models import Category
# Create your models here.

class Product(models.Model):
    product_name=models.CharField(max_length=100, unique=True)
    slug=models.SlugField(max_length=100, unique=True)
    description=models.TextField(max_length=500)
    image=models.ImageField(upload_to='photos/products')
    price=models.IntegerField()
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name



class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(category='color')

    def sizes(self):
        return super(VariationManager,self).filter(category='size')

variation_category_choices=(
    ('color','color'),
    ('size','size'),
)
class Variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    category=models.CharField(max_length=100,choices=variation_category_choices)
    category_value=models.CharField(max_length=100);
    created_at=models.DateTimeField(auto_now_add=True)

    objects=VariationManager()