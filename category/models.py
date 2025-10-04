from django.db import models

# Create your models here.
class Category(models.Model):
    category_name=models.CharField(max_length=50, unique=True);
    slug=models.SlugField(max_length=100, unique=True); # willl be used to uniquely identify
    description=models.CharField(max_length=255)
    cat_image=models.ImageField(upload_to='photos/category', blank=True) # blank =Truue mean it is optional

    def __str__(self):
        return self.category_name
