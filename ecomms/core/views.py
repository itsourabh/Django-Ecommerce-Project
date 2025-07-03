from http import client
from itertools import product
from django.http import HttpResponse
from django.shortcuts import render,redirect
from core.forms import *
from core.forms import ProductForm
from django.contrib import messages
from core.models import *
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from core.models import Product
from core.models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
import io
# from core.forms import CheckoutForm  # Make sure your form is named CheckoutForm
from core.models import Checkout 
# Create your views here.
def index(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(is_active=True)
    else:
        products = Product.objects.all()
    return render(request, 'core/index.html', {'products': products, 'query': query})



def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            print('True')
            form.save()
            print("Data Saved Successfully")
            messages.success(request, "Product is saved successfully")
            return redirect('/')
            # return redirect('/')
        else:
            print("Not Working")
            messages.info(request,"Product is not saved, Try Again")
        
    else:
        form = ProductForm()
    return render(request, 'core/add_product.html', {'form':form})

def product_desc(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'core/pro/product_desc.html', {'product': product})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    order_item, created = OrderItem.objects.get_or_create(
        product=product, user=request.user, ordered=False)
    
    # Get QuerySet of the user's order
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item is already in your cart.")
            return redirect("core:product_desc", pk=pk)
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart.")
        return redirect("core:product_desc", pk=pk)
        
        
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart.")
    return redirect("core:product_desc", pk=pk)
    return redirect('/')
    return render(request, 'core/pro/add_to_cart.html')
        
        
        
@login_required
def orderlist(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    if order:
        items = order.items.all()
        total_price = order.get_total_price()
        return render(request, 'core/Orderlist.html', {
            'order': order,
            'order_items': items,
            'total_price': total_price
        })
    return render(request, 'core/Orderlist.html', {'order_items': [], 'message': 'Your cart is empty.'})

@login_required
def add_item(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        product=product, user=request.user, ordered=False)
    
    # Get QuerySet of the user's order
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            if order_item.quantity < product.product_available_count:    
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "This item is already in your cart.")
                return redirect("core:orderlist")
            else:
                messages.info(request, "You cannot add more than available stock.")
                return redirect("core:orderlist")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart.")
            return redirect("core:orderlist")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart.")
        return redirect("core:orderlist")
    
def remove_item(request, pk):
    # remove_item = Order.objects.get(pk=pk)
    order_item = get_object_or_404(OrderItem, product__pk=pk, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item = OrderItem.objects.filter(product__pk=pk, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "This item quantity has been updated.")
                return redirect("core:orderlist")
            else:
                order.items.remove(order_item)
                order_item.delete()
                messages.info(request, "This item has been removed from your cart.")
                return redirect("core:orderlist")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:orderlist")
@login_required
def checkout(request):
    # Get the user's current order (cart)
    order = Order.objects.filter(user=request.user, ordered=False).first()
    cart_items = order.items.all() if order else []
    total_Item_price = order.get_total_price() if order else 0

    if Checkout.objects.filter(user=request.user).exists():
        return render(request, 'core/checkout.html', {
            'payment_allow': "allow",
            'cart_items': cart_items,
            'total_Item_price': total_Item_price,
        })
    if request.method == 'POST':
        form = Checkout(request.POST)
        try:
            if form.is_valid():
                # ... your existing save logic ...
                return render(request, 'core/checkout.html', {
                    'payment_allow': "allow",
                    'cart_items': cart_items,
                    'total_Item_price': total_Item_price,
                })
        except Exception as e:
            messages.error(request, "Checkout data could not be saved. Please try again.")
            return redirect('core:checkout')
    else:
        form = Checkout()
        return render(request, 'core/checkout.html', {
            'form': form,
            'payment_allow': "not_allow",
            'cart_items': cart_items,
            'total_Item_price': total_Item_price,
        })

def razorpay_payment(request):
    try:
        order = Order.objects.filter(user=request.user, ordered=False).first()
        address = Checkout.objects.filter(user=request.user).first()
        order_amount = order.get_total_price() if order else 0
        order_currency = 'INR'
        order_receipt = order.order_id if order else 'Order Receipt'
        notes = {
            'address': address.address if address else 'No Address Provided',
            'country': address.country if address else 'No Country Provided',
            'zip_code': address.zip_code if address else 'No Zip Code Provided'
        }
        if not order:
            messages.error(request, "No active order found.")
            return redirect('core:orderlist')
        
        
        razorpay_order = client.order.create({
            'amount': int(order.get_total_price() * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': order.order_id,
            'payment_capture': '1'
        })
        
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        return render(request, "core/razorpay_payment.html", 
            {
                'order': order,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': "rzp_test_8b0d1f2c3e4f5g6h7i8j9k0l",
                'order_id': razorpay_order['id'],
                'amount': order_amount,
                'currency': order_currency,
                'receipt': order_receipt,
                'notes': notes
            },
        )
        
    except Exception as e:
        messages.error(request, f"Payment initialization failed: {e}")
        return HttpResponse("404 Not Found")
        return redirect('core:orderlist')
    
    
@csrf_exempt
def handlerrequest(request):
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id', "")
            order_id = request.POST.get('razorpay_order_id', "")
            signature = request.POST.get('razorpay_signature', "")
            print(payment_id, order_id, signature)
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
                print("Order found in database")
            except Order.DoesNotExist:
                print("Order not found in database")
                return HttpResponse("404 Not Found", status=404)
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()
            print("working..........")
            try:
                result = razorpay_client.utility.verify_payment_signature(params_dict)
            except Exception as e:
                print("Signature verification failed:", e)
                order_db.ordered = False
                order_db.save()
                return render(request, "payment_failed.html")
            if result is None:
                print("Working Final Fine.......")
                amount = order_db.get_total_price()
                amount = int(amount * 100)
                try:
                    payment_status = razorpay_client.payment.capture(payment_id, amount)
                except Exception as e:
                    print("Payment capture failed:", e)
                    order_db.ordered = False
                    order_db.order_status = "Failed"
                    order_db.save()
                    request.session["order_failed"] = "Your order could not be placed. Please try again later."
                    return redirect("/")
                if payment_status is not None:
                    order_db.ordered = True
                    order_db.order_status = "Completed"
                    order_db.save()
                    request.session["order_complete"] = "Your order has been placed successfully. Thank you for shopping with us."
                    return render(request, "invoice/invoice.html", {"order": order_db, "payment_status": payment_status})
                else:
                    print("Payment failed")
                    order_db.ordered = False
                    order_db.order_status = "Failed"
                    order_db.save()
                    request.session["order_failed"] = "Your order could not be placed. Please try again later."
                    return redirect("/")
            else:
                order_db.ordered = False
                order_db.save()
                return render(request, "payment_failed.html")
        except Exception as e:
            print("Exception in handlerrequest:", e)
            return HttpResponse("404 Not Found", status=404)
    else:
        return HttpResponse("Invalid request method.", status=405)

@login_required
def invoice(request):
    # Get the latest completed order for the user
    order = Order.objects.filter(user=request.user, ordered=True).last()
    # If you have a separate address model, get it; else, use order.billing_address or similar
    address = Checkout.objects.filter(user=request.user).last()  # or order.billing_address

    # Calculate shipping and VAT
    shipping = 15  # or get from order/address if dynamic
    subtotal = order.get_total_price() if order else 0
    vat = subtotal * 0.05
    total = subtotal + vat + shipping

    context = {
        'order': order,
        'address': address,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'core/invoice.html', context)



@login_required
def render_pdf_view(request):
    # Get the latest completed order for the user
    order = Order.objects.filter(user=request.user, ordered=True).last()
    address = Checkout.objects.filter(user=request.user).last()
    shipping = 15
    subtotal = order.get_total_price() if order else 0
    vat = subtotal * 0.05
    total = subtotal + vat + shipping

    context = {
        'order': order,
        'address': address,
        'shipping': shipping,
        'total': total,
    }

    template_path = 'core/invoice.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    pisa_status = pisa.CreatePDF(
        io.BytesIO(html.encode('UTF-8')), dest=response, encoding='UTF-8'
    )

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


import razorpay
razorpay_client = razorpay.Client(auth=("rzp_test_8b0d1f2c3e4f5g6h7i8j9k0l", "rzp_test_1a2b3c4d5e6f7g8h9i0j1k2l"))
@login_required
def payment_summary(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    if not order:
        messages.error(request, "No active order found.")
        return redirect('core:orderlist')

    razorpay_order = razorpay_client.order.create({
    'amount': int(order.get_total_price() * 100),
    'currency': 'INR',
    'receipt': order.order_id,
    'payment_capture': '1'
    })
    print("Razorpay order response:", razorpay_order)
    order.razorpay_order_id = razorpay_order['id']
    order.save()

    context = {
        'order': order,
        'razorpay_key_id': "rzp_test_8b0d1f2c3e4f5g6h7i8j9k0l",
        'razorpay_order_id': razorpay_order['id'],
        'user': request.user,
    }
    return render(request, 'core/paymentsummary.html', context)


