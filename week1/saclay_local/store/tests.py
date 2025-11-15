from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from .models import Producer, Product


class ProducerModelTest(TestCase):
    
    def setUp(self):
        self.producer = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
    
    def test_producer_creation(self):
        self.assertEqual(self.producer.name, "Ferme de Viltain")
        self.assertEqual(self.producer.email, "contact@ferme-viltain.fr")
    
    def test_producer_str(self):
        self.assertEqual(str(self.producer), "Ferme de Viltain")
    
    def test_producer_unique_name(self):
        with self.assertRaises(Exception):
            Producer.objects.create(
                name="Ferme de Viltain",
                email="autre@email.fr"
            )


class ProductModelTest(TestCase):
    
    def setUp(self):
        self.producer = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
        self.product = Product.objects.create(
            name="Yaourt Vanille",
            price=Decimal("2.50"),
            stock_quantity=20,
            producer=self.producer
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Yaourt Vanille")
        self.assertEqual(self.product.price, Decimal("2.50"))
        self.assertEqual(self.product.stock_quantity, 20)
        self.assertEqual(self.product.producer, self.producer)
    
    def test_product_str(self):
        self.assertEqual(str(self.product), "Yaourt Vanille (Ferme de Viltain)")
    
    def test_product_unique_together(self):
        with self.assertRaises(Exception):
            Product.objects.create(
                name="Yaourt Vanille",
                price=Decimal("3.00"),
                stock_quantity=10,
                producer=self.producer
            )


class HomePageTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.producer = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
        self.product1 = Product.objects.create(
            name="Yaourt Vanille",
            price=Decimal("2.50"),
            stock_quantity=20,
            producer=self.producer
        )
        self.product2 = Product.objects.create(
            name="Jus de Pomme",
            price=Decimal("3.50"),
            stock_quantity=15,
            producer=self.producer
        )
    
    def test_home_page_status_code(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_page_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'store/index.html')
        self.assertTemplateUsed(response, 'store/base.html')
    
    def test_home_page_contains_products(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Yaourt Vanille")
        self.assertContains(response, "Jus de Pomme")


class ProductListTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.producer = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
        self.product = Product.objects.create(
            name="Yaourt Vanille",
            price=Decimal("2.50"),
            stock_quantity=20,
            producer=self.producer
        )
    
    def test_products_list_status_code(self):
        response = self.client.get(reverse('products_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_products_list_template(self):
        response = self.client.get(reverse('products_list'))
        self.assertTemplateUsed(response, 'store/products_list.html')
    
    def test_products_list_contains_product(self):
        response = self.client.get(reverse('products_list'))
        self.assertContains(response, "Yaourt Vanille")
        self.assertContains(response, "2,50")


class ProductDetailTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.producer = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
        self.product = Product.objects.create(
            name="Yaourt Vanille",
            price=Decimal("2.50"),
            stock_quantity=20,
            producer=self.producer
        )
    
    def test_product_detail_status_code(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_product_detail_template(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertTemplateUsed(response, 'store/product_detail.html')
    
    def test_product_detail_contains_info(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertContains(response, "Yaourt Vanille")
        self.assertContains(response, "2,50")
        self.assertContains(response, "Ferme de Viltain")
        self.assertContains(response, "20 unités en stock")
    
    def test_product_detail_not_found(self):
        response = self.client.get(reverse('product_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class ProducerListTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.producer1 = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
        self.producer2 = Producer.objects.create(
            name="Les Vergers du Plateau",
            email="contact@vergers-plateau.fr"
        )
    
    def test_producers_list_status_code(self):
        response = self.client.get(reverse('producers_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_producers_list_template(self):
        response = self.client.get(reverse('producers_list'))
        self.assertTemplateUsed(response, 'store/producers_list.html')
    
    def test_producers_list_contains_producers(self):
        response = self.client.get(reverse('producers_list'))
        self.assertContains(response, "Ferme de Viltain")
        self.assertContains(response, "Les Vergers du Plateau")


class ProducerDetailTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.producer = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
        self.product1 = Product.objects.create(
            name="Yaourt Vanille",
            price=Decimal("2.50"),
            stock_quantity=20,
            producer=self.producer
        )
        self.product2 = Product.objects.create(
            name="Yaourt Fraise",
            price=Decimal("2.50"),
            stock_quantity=15,
            producer=self.producer
        )
    
    def test_producer_detail_status_code(self):
        response = self.client.get(reverse('producer_detail', args=[self.producer.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_producer_detail_template(self):
        response = self.client.get(reverse('producer_detail', args=[self.producer.id]))
        self.assertTemplateUsed(response, 'store/producer_detail.html')
    
    def test_producer_detail_contains_info(self):
        response = self.client.get(reverse('producer_detail', args=[self.producer.id]))
        self.assertContains(response, "Ferme de Viltain")
        self.assertContains(response, "contact@ferme-viltain.fr")
    
    def test_producer_detail_contains_products(self):
        response = self.client.get(reverse('producer_detail', args=[self.producer.id]))
        self.assertContains(response, "Yaourt Vanille")
        self.assertContains(response, "Yaourt Fraise")


class CartTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.producer = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
        self.product = Product.objects.create(
            name="Yaourt Vanille",
            price=Decimal("2.50"),
            stock_quantity=20,
            producer=self.producer
        )
    
    def test_view_empty_cart(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/cart.html')
        self.assertContains(response, "Votre panier est vide")
    
    def test_add_to_cart(self):
        response = self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        
        session = self.client.session
        self.assertIn(str(self.product.id), session.get('cart', {}))
    
    def test_view_cart_with_items(self):
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        
        response = self.client.get(reverse('cart'))
        self.assertContains(response, "Yaourt Vanille")
        self.assertContains(response, "2,50")
    
    def test_update_cart_quantity(self):
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        
        response = self.client.post(
            reverse('update_cart', args=[self.product.id]),
            {'quantity': 3}
        )
        self.assertEqual(response.status_code, 302)
        
        session = self.client.session
        cart = session.get('cart', {})
        self.assertEqual(cart[str(self.product.id)]['quantity'], 3)
    
    def test_remove_from_cart(self):
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        
        response = self.client.get(reverse('remove_from_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        
        session = self.client.session
        cart = session.get('cart', {})
        self.assertNotIn(str(self.product.id), cart)
    
    def test_clear_cart(self):
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        
        response = self.client.get(reverse('clear_cart'))
        self.assertEqual(response.status_code, 302)
        
        session = self.client.session
        cart = session.get('cart', {})
        self.assertEqual(len(cart), 0)
    
    def test_cannot_add_more_than_stock(self):
        for i in range(self.product.stock_quantity):
            self.client.get(reverse('add_to_cart', args=[self.product.id]))
        
        response = self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        
        session = self.client.session
        cart = session.get('cart', {})
        self.assertEqual(cart[str(self.product.id)]['quantity'], self.product.stock_quantity)
    
    def test_cannot_update_cart_beyond_stock(self):
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        
        response = self.client.post(
            reverse('update_cart', args=[self.product.id]),
            {'quantity': self.product.stock_quantity + 10}
        )
        self.assertEqual(response.status_code, 302)
        
        session = self.client.session
        cart = session.get('cart', {})
        self.assertEqual(cart[str(self.product.id)]['quantity'], 1)
    
    def test_can_add_up_to_stock_limit(self):
        self.client.get(reverse('add_to_cart', args=[self.product.id]))
        
        response = self.client.post(
            reverse('update_cart', args=[self.product.id]),
            {'quantity': self.product.stock_quantity}
        )
        
        session = self.client.session
        cart = session.get('cart', {})
        self.assertEqual(cart[str(self.product.id)]['quantity'], self.product.stock_quantity)


class AboutPageTest(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_about_page_status_code(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
    
    def test_about_page_template(self):
        response = self.client.get(reverse('about'))
        self.assertTemplateUsed(response, 'store/about.html')
    
    def test_about_page_contains_info(self):
        response = self.client.get(reverse('about'))
        self.assertContains(response, "Notre Mission")
        self.assertContains(response, "Nos Valeurs")


class SearchTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.producer = Producer.objects.create(
            name="Ferme de Viltain",
            email="contact@ferme-viltain.fr"
        )
        self.producer2 = Producer.objects.create(
            name="Ferme de Vilgénis",
            email="contact@ferme-vilgenis.fr"
        )
        self.product = Product.objects.create(
            name="Yaourt Vanille",
            price=Decimal("2.50"),
            stock_quantity=20,
            producer=self.producer
        )
        self.product2 = Product.objects.create(
            name="Yaourt Fraise",
            price=Decimal("2.50"),
            stock_quantity=15,
            producer=self.producer
        )
    
    def test_search_product_found_exact_match_redirects(self):
        response = self.client.get(
            reverse('search'),
            {'query': 'Yaourt Vanille', 'scope': 'product'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product_detail', args=[self.product.id]))
    
    def test_search_product_partial_match_shows_results(self):
        response = self.client.get(
            reverse('search'),
            {'query': 'Yaourt', 'scope': 'product'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/search_results.html')
        self.assertContains(response, "Yaourt Vanille")
    
    def test_search_product_not_found(self):
        response = self.client.get(
            reverse('search'),
            {'query': 'Produit Inexistant', 'scope': 'product'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/search_results.html')
        self.assertContains(response, "Aucun produit trouvé")
    
    def test_search_producer_found_exact_match_redirects(self):
        response = self.client.get(
            reverse('search'),
            {'query': 'Ferme de Viltain', 'scope': 'producer'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('producer_detail', args=[self.producer.id]))
    
    def test_search_producer_partial_match_shows_results(self):
        response = self.client.get(
            reverse('search'),
            {'query': 'Ferme', 'scope': 'producer'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/search_results.html')
        self.assertContains(response, "Ferme de Viltain")
        self.assertContains(response, "Ferme de Vilgénis")