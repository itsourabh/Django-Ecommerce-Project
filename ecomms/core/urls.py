from django.urls import path, include
from django.conf import settings
from core import views
app_name = "core"

urlpatterns = [
    path('', views.index, name='index'),
    path('add_product', views.add_product, name='add_product'),
    path('product_desc/<pk>', views.product_desc, name='product_desc'),
    path('add_to_cart/<pk>', views.add_to_cart, name='add_to_cart'),
    path('orderlist', views.orderlist, name='orderlist'),
    path('add_item/<int:pk>', views.add_item, name='add_item'),
    path('remove_item/<int:pk>', views.remove_item, name='remove_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('razorpaypayment/', views.razorpay_payment, name='razorpay_payment'),
    path('handlerrequest/', views.handlerrequest, name='handlerrequest'),
    path("invoice/",views.invoice, name="invoice"),
    path('invoice/pdf/', views.render_pdf_view, name='invoice_pdf'),
    path('paymentsummary/', views.payment_summary, name='payment_summary'),

]
