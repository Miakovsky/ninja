from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Category(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='images/')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        ordering = ('title',)
        indexes = [models.Index(fields=['id', 'slug'])]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'id':self.id, 'slug':self.slug})
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name = 'lists', on_delete = models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete = models.CASCADE, null=True)
    quantity = models.PositiveBigIntegerField(default = 1)

    class Meta:
        verbose_name = 'Вишлист'
        verbose_name_plural = 'Вишлисты'
        constraints = [models.UniqueConstraint(fields = ['user', 'product'], name = 'user_product')] 

    def __str__(self):
        return self.user.username + '-' + self.product.name


class Status(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, related_name = 'orders', on_delete = models.CASCADE)
    status = models.ForeignKey(Status, on_delete = models.CASCADE)
    total = models.DecimalField(max_digits = 10, decimal_places = 2)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ('created_at', )
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name = 'order_items', on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    cost = models.DecimalField(max_digits = 10, decimal_places = 2)
    quantity = models.PositiveBigIntegerField(default = 1)

    class Meta:
        verbose_name = 'Заказано'

    def get_total_price(self):
        return self.product.price * self.quantity