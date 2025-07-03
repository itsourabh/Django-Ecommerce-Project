from django.contrib import admin
from core.models import *
# from core.templatetags.cart_template_tag import cart_item_count

# Register your models here.
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Checkout)
# admin.site.register(cart_item_count)