from django.db import models
from django.contrib.auth.models import User, auth
from django.db.models import Sum
from decimal import Decimal

# Create your models here.

class Categorie(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    orderid = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    # since url are of 2083 max characters
    image_url = models.ImageField(upload_to='Images/')

    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products_by_categorieid(categorie_id):
        if categorie_id:
            return Product.objects.filter(category=categorie_id)
        else:
            return Product.objects.all()
    
    def __str__(self):
        return self.name

class Offer(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    discount = models.FloatField()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=250, default='')
    phone = models.CharField(max_length=13, default='')
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    STATUS_CHOICES = [
        ('Order_Placed', 'Order Placed'),
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Order_Placed')

    def calculate_total_cost(self):
        shipping_charge_decimal = Decimal(str(self.shipping_charge))
        price_decimal = Decimal(str(self.price))
        # Calculate total price of items in the order
        total_price = self.orderitem_set.aggregate(total_price=Sum('price'))['total_price'] or Decimal('0.00')
        # Add shipping charge to total price
        total_price += shipping_charge_decimal
        # Add order price to total price
        total_price += price_decimal
        # Update the total cost field
        self.total_cost = total_price

    def place_order(self):
        self.save()

    def __str__(self):
        return f"Order {self.id}"
    
    def save(self, *args, **kwargs):
        # Calculate total cost before saving the order
        self.calculate_total_cost()
        super().save(*args, **kwargs)
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Define price as Decimal field

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
