from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
PRODUCERS = {
  'ferme_viltain': {'name': 'Ferme_de_Viltain'},
}


PRODUCTS = [
  {'name': 'yaourth_vanille', 'producers': [PRODUCERS['ferme_viltain']]},
  {'name': 'yaourth_marron', 'producers': [PRODUCERS['ferme_viltain']]},
  {'name': 'jus_de_pomme', 'producers': [PRODUCERS['ferme_viltain']]}
]

class Producer(models.Model):
    name = models.CharField(max_length=120, unique=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    producer = models.ForeignKey(
        Producer, on_delete=models.CASCADE, related_name='products'
    )

    class Meta:
        unique_together = ('name', 'producer')

    def __str__(self):
        return f"{self.name} ({self.producer})"

class Client(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

class Basket(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='baskets'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    products = models.ManyToManyField('Product', through='BasketItem')

    def __str__(self):
        return f"Basket #{self.pk} - {self.client}"

class BasketItem(models.Model):
    basket = models.ForeignKey(
        Basket, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='basket_items'
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('basket', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product} in {self.basket}"