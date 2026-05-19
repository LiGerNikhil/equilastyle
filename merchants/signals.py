from django.db.models.signals import post_save
from django.dispatch import receiver

from merchants.models import Merchant, MerchantWallet


@receiver(post_save, sender=Merchant)
def create_merchant_wallet(sender, instance, created, **kwargs):
    if created:
        MerchantWallet.objects.get_or_create(merchant=instance)
