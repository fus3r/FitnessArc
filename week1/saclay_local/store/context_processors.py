def cart_context(request):
    cart = request.session.get('cart', {})
    cart_total_items = sum(item['quantity'] for item in cart.values())
    return {
        'cart_total_items': cart_total_items
    }
