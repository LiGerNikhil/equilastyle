import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.models import Cart, CartItem

import razorpay


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def order_create(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total_price()

            # Set payment method and status
            payment_method = form.cleaned_data.get('payment_method', 'cod')
            order.payment_method = payment_method
            if payment_method == 'cod':
                order.payment_status = 'pending'
                order.status = 'confirmed'
            else:
                order.payment_status = 'pending'
                order.status = 'pending'

            order.save()

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.get_price()
                )

            # Clear cart for COD orders
            if payment_method == 'cod':
                cart_items.delete()
                messages.success(request, 'Your order has been placed successfully!')
                return redirect('orders:order_detail', order.id)
            else:
                # For online payment, cart will be cleared after successful payment
                messages.info(request, 'Please complete the payment to confirm your order.')
                return redirect('orders:order_detail', order.id)

    else:
        default_address = request.user.addresses.filter(is_default=True).first()
        initial_data = {
            'email': request.user.email,
            'phone_number': getattr(request.user, 'phone', '') or (default_address.phone_number if default_address else ''),
        }
        if default_address:
            initial_data.update({
                'shipping_address': default_address.get_full_address(),
                'billing_address': default_address.get_full_address(),
            })
        form = OrderCreateForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'orders/order_create.html', context)


@login_required
def create_razorpay_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'})

    try:
        data = json.loads(request.body)
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()

        if not cart_items:
            return JsonResponse({'success': False, 'message': 'Cart is empty'})

        total_amount = float(cart.get_total_price()) * 100  # Convert to paise/cents

        # Create Razorpay order
        client = get_razorpay_client()
        razorpay_order = client.order.create({
            'amount': int(total_amount),
            'currency': settings.RAZORPAY_CURRENCY,
            'receipt': f'order_{request.user.id}_{int(total_amount)}',
            'payment_capture': 1
        })

        # Create Django order in pending state
        order = Order.objects.create(
            user=request.user,
            total_price=cart.get_total_price(),
            shipping_address=data.get('shipping_address', ''),
            billing_address=data.get('billing_address', ''),
            phone_number=data.get('phone_number', ''),
            email=data.get('email', request.user.email),
            notes=data.get('notes', ''),
            payment_method='online',
            payment_status='pending',
            status='pending',
            razorpay_order_id=razorpay_order['id']
        )

        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.get_price()
            )

        return JsonResponse({
            'success': True,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': int(total_amount),
            'currency': settings.RAZORPAY_CURRENCY,
            'razorpay_order_id': razorpay_order['id'],
            'order_id': order.id,
            'email': order.email,
            'phone': order.phone_number
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
@login_required
def verify_payment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'})

    try:
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        order_id = data.get('order_id')

        # Verify signature
        client = get_razorpay_client()
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            signature_valid = True
        except razorpay.errors.SignatureVerificationError:
            signature_valid = False

        order = get_object_or_404(Order, id=order_id, user=request.user)

        if signature_valid:
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save()

            # Clear cart after successful payment
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart.items.all().delete()

            messages.success(request, 'Payment successful! Your order has been confirmed.')
            return JsonResponse({
                'success': True,
                'redirect_url': f'/orders/{order.id}/'
            })
        else:
            order.payment_status = 'failed'
            order.save()
            return JsonResponse({
                'success': False,
                'message': 'Payment verification failed. Please contact support.'
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
