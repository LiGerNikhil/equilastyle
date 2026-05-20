from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_order_confirmation_email(order):
    subject = f'Order Confirmed — #{order.order_number} — EQUILA STYLE'
    to_email = order.email

    html_content = render_to_string('orders/order_confirmation_email.html', {'order': order})

    msg = EmailMultiAlternatives(
        subject=subject,
        body=f'Thank you for your order #{order.order_number}. View your order details on the EQUILA STYLE website.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
