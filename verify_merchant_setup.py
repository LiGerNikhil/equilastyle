"""
Verification Script for Merchant Products Feature
Run this in Django shell to verify setup: python manage.py shell < verify_merchant_setup.py
"""

from merchants.models import Merchant
from products.models import Product
from orders.models import Order, OrderItem
from django.db.models import Count, Q

print("\n" + "="*70)
print("MERCHANT PRODUCTS FEATURE - VERIFICATION REPORT")
print("="*70)

# 1. Check Merchants
print("\n[1] MERCHANTS STATUS")
print("-" * 70)

merchants = Merchant.objects.all()
print(f"Total Merchants: {merchants.count()}")

if merchants.count() == 0:
    print("⚠️  WARNING: No merchants created yet. Create one to get started.")
else:
    for merchant in merchants[:5]:  # Show first 5
        status_ok = merchant.status == 'active' and merchant.verification_status == 'verified'
        status_indicator = "✅" if status_ok else "❌"
        print(f"\n{status_indicator} {merchant.business_name} (ID: {merchant.merchant_id})")
        print(f"   Status: {merchant.status} | Verification: {merchant.verification_status}")
        print(f"   Commission Rate: {merchant.commission_rate}%")
        print(f"   Products Count: {merchant.products.count()}")

# 2. Check Products
print("\n\n[2] PRODUCTS STATUS")
print("-" * 70)

all_products = Product.objects.all()
approved = all_products.filter(approval_status='approved', is_available=True)
pending = all_products.filter(approval_status='pending')
draft = all_products.filter(approval_status='draft')

print(f"Total Products: {all_products.count()}")
print(f"  ✅ Approved & Available: {approved.count()}")
print(f"  ⏳ Pending Approval: {pending.count()}")
print(f"  📝 Draft: {draft.count()}")

merchant_products = all_products.filter(merchant__isnull=False)
hq_products = all_products.filter(merchant__isnull=True)

print(f"\nBy Source:")
print(f"  👤 Merchant Products: {merchant_products.count()}")
print(f"  🏢 HQ Products: {hq_products.count()}")

# 3. Check Product Visibility
print("\n\n[3] PRODUCT VISIBILITY CHECK")
print("-" * 70)

from merchants.services import public_product_queryset

public = public_product_queryset()
print(f"Products visible to customers: {public.count()}")

if public.count() == 0:
    print("\n⚠️  WARNING: No products visible to customers!")
    print("Check:")
    print("  1. Is merchant status = 'active'?")
    print("  2. Is merchant verification_status = 'verified'?")
    print("  3. Is product approval_status = 'approved'?")
    print("  4. Is product is_available = True?")

visible_by_merchant = public.filter(merchant__isnull=False).values('merchant__business_name').annotate(count=Count('id'))
for item in visible_by_merchant:
    print(f"\n  📦 {item['merchant__business_name']}: {item['count']} products")

# 4. Check Orders
print("\n\n[4] ORDERS & REVENUE STATUS")
print("-" * 70)

all_orders = Order.objects.all()
delivered = OrderItem.objects.filter(fulfillment_status='delivered')

print(f"Total Orders: {all_orders.count()}")
print(f"Delivered Order Items: {delivered.count()}")

if all_orders.count() > 0:
    recent_order = all_orders.latest('created_at')
    print(f"\nLatest Order: {recent_order.order_number} ({recent_order.status})")
    items = recent_order.items.all()
    print(f"  Items: {items.count()}")
    for item in items:
        print(f"    - {item.product.name} ({item.product.merchant.business_name if item.product.merchant else 'HQ'})")

# 5. Check Merchant Revenue
print("\n\n[5] MERCHANT REVENUE & PAYOUTS")
print("-" * 70)

from merchants.models import MerchantTransaction, MerchantWallet

transactions = MerchantTransaction.objects.all()
wallets = MerchantWallet.objects.all()

print(f"Total Transactions: {transactions.count()}")
print(f"Merchants with Wallets: {wallets.count()}")

for wallet in wallets[:5]:
    print(f"\n  💰 {wallet.merchant.business_name}")
    print(f"     Balance: ₹{wallet.balance}")
    sales = transactions.filter(merchant=wallet.merchant, transaction_type='sale_credit')
    commissions = transactions.filter(merchant=wallet.merchant, transaction_type='commission_debit')
    print(f"     Sales: {sales.count()} | Commissions Deducted: {commissions.count()}")

# 6. Summary & Recommendations
print("\n\n[6] SETUP SUMMARY & RECOMMENDATIONS")
print("-" * 70)

checklist = []

# Check 1: At least one active+verified merchant
active_merchants = merchants.filter(status='active', verification_status='verified')
if active_merchants.count() > 0:
    checklist.append(("✅", f"Active Merchants", f"{active_merchants.count()} merchant(s) ready to sell"))
else:
    checklist.append(("❌", f"No Active Merchants", "Go to Admin Panel → Merchants → Set status=active & verified"))

# Check 2: Approved products
if approved.count() > 0:
    checklist.append(("✅", f"Approved Products", f"{approved.count()} products visible to customers"))
else:
    checklist.append(("⚠️ ", f"No Approved Products", "Admin must approve merchant products in Product Approvals"))

# Check 3: Public visible products
if public.count() > 0:
    checklist.append(("✅", f"Publicly Visible", f"{public.count()} products visible in storefront"))
else:
    checklist.append(("❌", f"Visibility Issue", "Check merchant activation & product approval above"))

# Check 4: Orders exist
if all_orders.count() > 0:
    checklist.append(("✅", f"Order Flow Working", f"{all_orders.count()} orders created"))
else:
    checklist.append(("⏳", f"No Orders Yet", "Feature ready - waiting for customers"))

for indicator, title, details in checklist:
    print(f"\n{indicator} {title}")
    print(f"   {details}")

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("""
1. CREATE MERCHANT (if not exists)
   → Admin Panel → Merchants → Add Merchant

2. ACTIVATE MERCHANT
   → Admin Panel → Merchants → Select Merchant
   → Set Status = 'active'
   → Set Verification Status = 'verified'
   → Save

3. MERCHANT UPLOADS PRODUCTS
   → Merchant logs in → Portal → Products → Add Product
   → Fill details (name, price, category, images, variants)
   → Click "Submit for Approval"

4. ADMIN APPROVES PRODUCTS
   → Admin Panel → Product Approvals
   → Review product details
   → Click "Approve" button
   → Product automatically goes live

5. CUSTOMERS SEE & PURCHASE
   → Home page, product listing, or merchant store
   → Add to cart → Checkout → Order created
   → Order automatically routes to merchant

6. MERCHANT MANAGES ORDERS
   → Merchant Portal → Orders
   → Update fulfillment status (accepted, packed, shipped, delivered)
   → When marked delivered → Payment credited to merchant wallet
   → Commission automatically deducted

7. MERCHANT TRACKS PAYOUTS
   → Merchant Portal → Wallet
   → View transaction history
   → Request payout
""")

print("="*70 + "\n")
