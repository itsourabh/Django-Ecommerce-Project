from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE)
    # Extra fields for customer
    phone_field = models.CharField(max_length=12, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    category_name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_available_count = models.IntegerField(default=0)
    img = models.ImageField(upload_to='image/')
    desc = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
    def get_total_item_price(self):
        return self.quantity * self.product.price
    
    def get_final_price(self):
        return self.get_total_item_price()
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True, blank=True)
    ordered = models.BooleanField(default=False)
    order_id = models.CharField(max_length=20, unique=True,default=None,blank=True, null=True)
    datetime_ofpayment = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, default='Pending')
    order_delivered = models.BooleanField(default=False)
    order_received = models.BooleanField(default=False)
    
    
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=100, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.order_id is None and self.datetime_ofpayment and self.id:
            self.order_id = self.datetime_ofpayment.strftime('PAY2ME%Y%m%dODR') + str(self.id)
            
        
        return super().save(*args, **kwargs)
        
    def __str__(self):
        return self.user.username
        
    def get_total_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_final_price()
        return total
    
    def get_total_count(self):
        order = Order.objects.get(pk=self.pk)
        return order.items.count()

class Checkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=12, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    
    def __str__(self):
        return f"Checkout for {self.user.username} - Order ID: {self.order.order_id}"