from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from .models import *

def index(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', {'products': products})

def index_v1(request):
    products = Product.objects.all()
    formatted_products = ["<li>{}</li>".format(product.name) for product in products]
    message = """<ul>{}</ul>""".format("\n".join(formatted_products))
    return HttpResponse(message)

def index_v0(request):
    produits_list = '\n'.join([f"- {product['name'].replace('_', ' ')}" for product in PRODUCTS])
    return HttpResponse(produits_list, content_type="text/plain")

def info_product(request,product_id):
    product = Product.objects.get(pk=product_id)
    info_msg = f'Le nom du produit est {product.name}.\
    \nIl a été produit par : {product.producer}.\
    \nPrix : {product.price} EUR \
    \nStock disponible : {product.stock_quantity} unités.'
    return HttpResponse(info_msg, content_type="text/plain; charset=utf-8")

def info_product_v0(request,product_id):
    product_name = PRODUCTS[product_id]["name"].replace("_", " ")
    producer_names = [x['name'].replace("_", " ") for x in PRODUCTS[product_id]["producers"]]
    info_msg = f'Le nom du produit est {product_name}. Il a été produit par {', '.join(producer_names)}.'
    return HttpResponse(info_msg, content_type="text/plain; charset=utf-8")

def search_products(request, query):
    product = Product.objects.filter(name=query)
    if product:
        return info_product(request, product.first().id)
    error_msg = f'Erreur : Le produit "{query}" n\'existe pas dans notre catalogue.'
    return HttpResponse(error_msg, content_type="text/plain; charset=utf-8", status=404)

def search_products_v0(request, query):
    for idx, product in enumerate(PRODUCTS):
        if query == product['name']:
            return info_product(request, idx)
    
    error_msg = f'Erreur : Le produit "{query}" n\'existe pas dans notre catalogue.'
    return HttpResponse(error_msg, content_type="text/plain; charset=utf-8", status=404)

def search_producers(request, query):
    producer = Producer.objects.filter(name=query)
    if producer:
        producer_products = Product.objects.filter(producer=producer.first())
        if producer_products.exists():
            response = f"Produits de {producer.first().name}:\n"
            response += '\n'.join([f"- {product.name}" for product in producer_products])
            return HttpResponse(response, content_type="text/plain; charset=utf-8")
        else:
            return HttpResponse(
                f"Le producteur {producer.first().name} n'a pas de produits listés.",
                content_type="text/plain; charset=utf-8"
            )
    error_msg = f'Erreur : Le producteur "{query}" n\'existe pas dans notre base.'
    return HttpResponse(error_msg, content_type="text/plain; charset=utf-8", status=404)

def search_producers_v0(request, query):
    for producer_id, producer_info in PRODUCERS.items():
        if query == producer_info['name']:
            producer_products = [
                product['name'].replace('_', ' ')
                for product in PRODUCTS
                if any(p['name'] == producer_info['name'] for p in product['producers'])
            ]
            
            if producer_products:
                response = f"Produits de {producer_info['name'].replace('_', ' ')}:\n"
                response += '\n'.join([f"- {product}" for product in producer_products])
                return HttpResponse(response, content_type="text/plain; charset=utf-8")
            else:
                return HttpResponse(
                    f"Le producteur {producer_info['name'].replace('_', ' ')} n'a pas de produits listés.",
                    content_type="text/plain; charset=utf-8"
                )
    
    error_msg = f'Erreur : Le producteur "{query}" n\'existe pas dans notre base.'
    return HttpResponse(error_msg, content_type="text/plain; charset=utf-8", status=404)
    pass

def search(request):
    query = request.GET.get('query', '')
    """scope = (request.GET.get("scope") or "all").lower()
    scope = scope if scope in {"products", "producers", "all"} else "all"
    
    if scope in {"products", "all"}:
        return search_products(request, query)
    if scope in {"producers", "all"}:
        return search_producers(request, query)
    """

    scope = request.GET.get("scope").lower()
    
    if scope == 'product':
        return search_products(request, query)
    if scope == "producer":
        return search_producers(request, query)
    else:
        return HttpResponse("Erreur : Paramètre de scope manquant ou invalide", content_type="text/plain; charset=utf-8", status=400)
    return HttpResponse("Erreur: Scope de recherche invalide", content_type="text/plain; charset=utf-8", status=400)
def products_list(request):
    products = Product.objects.all()
    return render(request, 'store/products_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def producers_list(request):
    producers = Producer.objects.all()
    return render(request, 'store/producers_list.html', {'producers': producers})

def producer_detail(request, producer_id):
    producer = get_object_or_404(Producer, pk=producer_id)
    products = Product.objects.filter(producer=producer)
    return render(request, 'store/producer_detail.html', {'producer': producer, 'products': products})

def about(request):
    return render(request, 'store/about.html')

def get_cart(request):
    cart = request.session.get('cart', {})
    return cart

def get_cart_total(request):
    cart = get_cart(request)
    total_items = sum(item['quantity'] for item in cart.values())
    total_price = sum(item['quantity'] * float(item['price']) for item in cart.values())
    return total_items, total_price

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    current_quantity = cart.get(product_id_str, {}).get('quantity', 0)
    new_quantity = current_quantity + 1
    
    if new_quantity > product.stock_quantity:
        from django.contrib import messages
        messages.error(request, f'Stock insuffisant pour {product.name}. Disponible : {product.stock_quantity} unités.')
        return redirect(request.META.get('HTTP_REFERER', 'cart'))
    
    if product_id_str in cart:
        cart[product_id_str]['quantity'] = new_quantity
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'producer': product.producer.name
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    from django.contrib import messages
    messages.success(request, f'{product.name} a été ajouté au panier !')
    
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def view_cart(request):
    cart = get_cart(request)
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        item_total = float(item['price']) * item['quantity']
        cart_items.append({
            'id': product_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'producer': item['producer'],
            'total': item_total
        })
        total_price += item_total
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': sum(item['quantity'] for item in cart.values())
    }
    
    return render(request, 'store/cart.html', context)

def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if quantity > 0 and product_id_str in cart:
            product = get_object_or_404(Product, pk=product_id)
            
            if quantity > product.stock_quantity:
                from django.contrib import messages
                messages.error(request, f'Stock insuffisant pour {product.name}. Disponible : {product.stock_quantity} unités.')
                return redirect('cart')
            
            cart[product_id_str]['quantity'] = quantity
            request.session['cart'] = cart
            request.session.modified = True
        
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
        
        from django.contrib import messages
        messages.success(request, 'Produit retiré du panier.')
    
    return redirect('cart')

def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    
    from django.contrib import messages
    messages.success(request, 'Panier vidé.')
    
    return redirect('cart')