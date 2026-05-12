from .models import Cart


def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {
            'cart': cart,
            'cart_total_items': cart.get_total_items(),
            'cart_total_price': cart.get_total_price(),
        }
    return {
        'cart': None,
        'cart_total_items': 0,
        'cart_total_price': 0,
    }
