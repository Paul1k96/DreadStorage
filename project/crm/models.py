from django.db import models
from django.urls import reverse
from pytils.translit import slugify

from .utils2 import OverwriteStorage

class ProdInfo(models.Model):
    """Model contains information about each product unit from the Product model."""

    title = models.ForeignKey('Product', on_delete=models.CASCADE)
    account = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', null=True, on_delete=models.SET_NULL)
    shop = models.ForeignKey('Shop', null=True, on_delete=models.SET_NULL)
    cost = models.FloatField(default=0)
    weight = models.FloatField()
    time_create = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('edit_prodinfo', kwargs={'prodinfo_id': self.pk})


class Company(models.Model):
    """Model containing unique manufacturing companies"""

    company = models.CharField(max_length=150, unique=True, db_index=True,
                               error_messages={'unique': 'Такая компания уже существует'})
    slug = models.SlugField(max_length=150, unique=True, db_index=True, verbose_name='URL')

    def __str__(self):
        return self.company

    def save(self, *args, **kwargs):
        """Function to create a slug from the name, which is used to build the route url"""

        self.slug = slugify(self.company)
        super(Company, self).save(*args, **kwargs)


class Shop(models.Model):
    """Model containing unique shops"""

    shop = models.CharField(max_length=150, unique=True, db_index=True,
                            error_messages={'unique': 'Такой магазин уже существует.'})
    slug = models.SlugField(max_length=150, unique=True, db_index=True, verbose_name='URL')

    def __str__(self):
        return self.shop

    def save(self, *args, **kwargs):
        """Function to create a slug from the name, which is used to build the route url"""

        self.slug = slugify(self.shop)
        super(Shop, self).save(*args, **kwargs)


class Product(models.Model):
    """Model containing unique products"""

    title = models.CharField(max_length=150, unique=True, db_index=True,
                             error_messages={'unique': 'Такой товар уже существует'})
    slug = models.SlugField(max_length=150, unique=True, db_index=True, verbose_name='URL')
    company = models.ForeignKey('Company', null=True, on_delete=models.SET_NULL)
    ref_weight = models.FloatField()
    photo = models.ImageField(storage=OverwriteStorage(), upload_to="images/", blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Function to create a slug from the name, which is used to build the route url"""

        self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail', kwargs={'product_slug': self.slug})

    class Meta:
        ordering = ['title']

