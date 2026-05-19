"""Admin panel template context (pending counts for sidebar badges)."""


def admin_panel_context(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    from products.models import Product

    pending_products = Product.objects.filter(
        approval_status=Product.ApprovalStatus.PENDING,
        merchant__isnull=False,
    ).count()
    return {'admin_pending_product_count': pending_products}
