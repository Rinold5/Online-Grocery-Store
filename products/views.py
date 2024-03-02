from django.shortcuts import render, redirect, get_object_or_404
from .models import OrderItem, Product, Offer, Order, Categorie
from django.contrib import messages
from products.models import Order
from django.db import transaction
from django.contrib import messages

def index(request):
    cart = request.session.get('cart')

    if not cart:
        request.session['cart'] = {}

    categories = Categorie.objects.all()
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        if categorie_id == "10":
            products = Product.objects.all()
        else:
            products = Product.get_all_products_by_categorieid(categorie_id)
    else:
        products = Product.objects.all()
    
    data = {'products': products, 'categories': categories}
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        product = Product.objects.get(pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if product.stock < quantity:
            messages.error(request, f"{product.name} is out of stock.")
            print("Message added successfully:", f"{product.name} is out of stock.")
        else:
            if cart.get(product_id):
                if request.POST.get('remove'):
                    cart[product_id] -= 1  # Reduce quantity by 1
                    if cart[product_id] <= 0:
                        cart.pop(product_id)
                else:
                    cart[product_id] += quantity
            else:
                cart[product_id] = quantity
        
        request.session['cart'] = cart
        
        # Ensure to include messages in the context
        data['messages'] = messages.get_messages(request)
        print("Context data:", data)
    
    return render(request, 'index.html', data)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Offer

def cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        requested_quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, pk=product_id)

        # DEBUGGING: Print product details
        print(f"Product: {product.name}, Requested Quantity: {requested_quantity}, Stock: {product.stock}")

        # Ensure requested quantity doesn't exceed available stock
        if requested_quantity > product.stock:
            requested_quantity = product.stock  # Adjust requested quantity to available stock

        cart = request.session.get('cart', {})
        current_quantity = cart.get(product_id, 0)
        # Update cart with the adjusted quantity or add the product with the adjusted quantity
        cart[product_id] = max(current_quantity, requested_quantity)
        request.session['cart'] = cart
        return redirect('cart')  # Redirect back to the cart page after adding the product

    else:
        codes = request.POST.get('getcode')
        offers = Offer.objects.all()
        ids = list(request.session.get('cart', {}).keys())
        products = Product.get_products_by_id(ids)
        return render(request, 'cart.html', {'products': products, 'offers': offers, 'codes': codes})

def track_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(id=order_id)
            order_items = OrderItem.objects.filter(order=order)  # Fetch associated OrderItems
            return render(request, 'track_order.html', {'order': order, 'order_items': order_items})
        except Order.DoesNotExist:
            error_message = 'Order not found. Please check your order ID.'
            return render(request, 'track_order.html', {'error_message': error_message})
    else:
        # Handle GET request (render the form)
        return render(request, 'track_order.html', {'show_form': True})

from django.db.models import F, Sum
from .models import Product, Order, OrderItem
from django.db import transaction

@transaction.atomic
def thank_you(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        user_id = request.session.get('user_id')
        
        # Check if user_id is available in the session
        if user_id is None:
            # Redirect to the home page or login page
            return redirect('/')
        
        carts = request.session.get('cart')
        products = Product.get_products_by_id(list(carts.keys()))
        
        if len(phone) == 10 and phone[0] in "7896":
            # Reduce stock for each product and calculate total price and quantity
            total_price = 0
            total_quantity = 0
            for product in products:
                quantity = carts.get(str(product.id))
                if quantity:
                    # Check if stock is sufficient
                    if product.stock > 0:
                        # Adjust quantity if it exceeds available stock
                        if quantity > product.stock:
                            quantity = product.stock
                    else:
                        quantity = 0
                    # Reduce stock by the adjusted quantity
                    product.stock -= quantity
                    product.save()
                    total_price += product.price * quantity
                    total_quantity += quantity
            
            # Create a single order for all products in the cart
            order = Order.objects.create(user_id=user_id, address=address, phone=phone, quantity=total_quantity, price=total_price)
            
            # Add each product to the order as an order item
            for product in products:
                quantity = carts.get(str(product.id))
                if quantity:
                    OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
                
            # Clear the cart after placing the order
            request.session['cart'] = {}
            
            # Get the ID of the latest order
            order_id = order.id
            
            return render(request, 'thank_you.html', {'order_id': order_id})
        else:
            # Handle invalid phone number
            messages.warning(request, 'Please enter a valid phone number.')
            # Reset the phone number
            phone = ''
            return render(request, 'cart.html', {'phone': phone})  # Rep
    else:
        # Redirect to home page if the request method is not POST
        return redirect('/')

def order_details(request):
    # Your view logic here
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        shipping_charge = order.shipping_charge  # Get the shipping charge from the order
        return render(request, 'order_details.html', {'order': order, 'shipping_charge': shipping_charge})
    else:
        return render(request, 'order_details.html')
    