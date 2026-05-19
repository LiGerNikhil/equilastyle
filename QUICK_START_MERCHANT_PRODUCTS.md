# Quick Start: Get Merchant Products Working in 5 Minutes

## The Feature is Already Built! ✅

Your codebase has a fully functional multi-merchant platform with:

- ✅ Merchant product upload system
- ✅ Admin approval workflow
- ✅ Product visibility to all customers
- ✅ Shopping cart & order system
- ✅ Merchant order management dashboard
- ✅ Commission & payment tracking

**The only thing needed:** Activate a merchant account and approve products!

---

## Step 1: Activate a Test Merchant (2 minutes)

### Option A: Using Django Admin Panel

```
1. Go to: /admin/
2. Click: Merchants → Select a merchant (or create one)
3. Change: Status = "Active"
4. Change: Verification Status = "Verified"
5. Save
```

### Option B: Using Django Shell

```bash
python manage.py shell
```

```python
from merchants.models import Merchant

# Find or create test merchant
merchant, created = Merchant.objects.get_or_create(
    business_name="Test Store",
    defaults={
        'owner_name': 'John Merchant',
        'email': 'merchant@test.com',
        'phone': '9876543210',
        'address': '123 Main St',
        'city': 'Delhi',
        'state': 'Delhi',
        'pincode': '110001',
        'slug': 'test-store',
        'status': 'active',
        'verification_status': 'verified',
    }
)

if not created:
    merchant.status = 'active'
    merchant.verification_status = 'verified'
    merchant.save()

print(f"✅ Merchant activated: {merchant.business_name}")
```

---

## Step 2: Create a Test User & Link as Merchant Owner (Optional)

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from merchants.models import Merchant

User = get_user_model()

# Create merchant user
user = User.objects.create_user(
    email='merchant@example.com',
    password='password123',
    role='merchant'
)

# Link to merchant
merchant = Merchant.objects.first()
merchant.owner_user = user
merchant.save()

print(f"✅ User created: {user.email}")
print(f"   Role: merchant")
print(f"   Password: password123")
```

**Merchant Login URL:** `/merchants/portal/dashboard/`

---

## Step 3: Add Products (As Merchant or Admin)

### Option A: Merchant Portal

```
1. Login as merchant: /merchants/portal/dashboard/
2. Click: Products → Add Product
3. Fill in product details:
   - Name: "Test T-Shirt"
   - Price: 499
   - Category: Select one
   - Description: "Great quality t-shirt"
   - Add Variants (sizes): S, M, L, XL
   - Upload Images
4. Click: Submit for Approval
5. Status changes to "PENDING"
```

### Option B: Admin Create (Faster Testing)

```bash
python manage.py shell
```

```python
from products.models import Product, Category, ProductImage, ProductVariant
from merchants.models import Merchant
from django.contrib.auth import get_user_model

User = get_user_model()
merchant = Merchant.objects.first()
category = Category.objects.first() or Category.objects.create(
    name='Clothing',
    slug='clothing',
    gender='U'
)

product = Product.objects.create(
    name='Premium T-Shirt',
    slug='premium-tshirt',
    description='High quality cotton t-shirt',
    price=499,
    category=category,
    merchant=merchant,
    approval_status='approved',  # Direct approval for testing
    is_available=True,
    published_by=User.objects.filter(is_staff=True).first(),
)

# Add variant
ProductVariant.objects.create(
    product=product,
    size='M',
    quantity=100
)

print(f"✅ Product created: {product.name}")
print(f"   Status: {product.approval_status}")
print(f"   Visible to customers: {product in Product.objects.filter(approval_status='approved', is_available=True)}")
```

---

## Step 4: Approve Products (Admin Only)

### Visit Product Approvals Page

```
Admin Panel → Product Approvals
OR
Direct URL: /admin/product-approvals/
```

**For each pending product:**

1. Click product name to review
2. Check images, description, variants
3. Click "Approve" to make it live
4. Product now visible to all customers

---

## Step 5: See Products on Storefront

### As Customer

1. **Home page:** `/`
2. **Products listing:** `/products/`
3. **Merchant store:** `/store/<merchant-slug>/`
4. **Search:** `/products/search/?q=shirt`

**Products will show only if:**

- ✅ `approval_status = 'approved'`
- ✅ `is_available = True`
- ✅ Merchant `status = 'active'`
- ✅ Merchant `verification_status = 'verified'`

---

## Step 6: Create Test Order

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from products.models import Product

User = get_user_model()

# Get or create customer
customer = User.objects.filter(role='customer').first()
if not customer:
    customer = User.objects.create_user(
        email='customer@example.com',
        password='password123',
        role='customer'
    )

# Add product to cart
product = Product.objects.filter(approval_status='approved').first()
cart, _ = Cart.objects.get_or_create(user=customer)
CartItem.objects.create(cart=cart, product=product, quantity=1)

# Create order
order = Order.objects.create(
    user=customer,
    total_price=product.price,
    shipping_address='123 Customer St, Delhi',
    billing_address='123 Customer St, Delhi',
    phone_number='9876543210',
    email=customer.email,
    payment_method='cod',
    status='confirmed'
)

# Create order item (merchant routing automatic)
OrderItem.objects.create(
    order=order,
    product=product,
    quantity=1,
    price=product.price,
    merchant=product.merchant,
    fulfillment_type='merchant' if product.merchant else 'hq'
)

# Clear cart
cart.items.all().delete()

print(f"✅ Order created: {order.order_number}")
print(f"   Status: {order.status}")
print(f"   Merchant: {product.merchant.business_name if product.merchant else 'HQ'}")
```

---

## Step 7: Merchant Manages Order

### Merchant Portal

```
1. Login as merchant: /merchants/portal/dashboard/
2. Click: Orders
3. See order in the list
4. Update Status:
   - Pending → Accepted
   - Accepted → Packed
   - Packed → Shipped
   - Shipped → Delivered
5. When marked "Delivered":
   ✅ Commission automatically calculated
   ✅ Amount credited to merchant wallet
   ✅ Merchant can request payout
```

### Check Wallet

```
Merchant Portal → Wallet → View balance & transaction history
```

---

## Testing Checklist

- [ ] **Merchant activated** (status=active, verification=verified)
- [ ] **Product created** (uploaded or admin-created)
- [ ] **Product approved** (approval_status=approved, is_available=true)
- [ ] **Product visible** (appears on /products/ or merchant store)
- [ ] **Can add to cart** (Add to Cart button works)
- [ ] **Can checkout** (Order creation successful)
- [ ] **Order routed to merchant** (Merchant Portal → Orders shows it)
- [ ] **Can update status** (Fulfillment status can be changed)
- [ ] **Wallet updated** (After marking delivered, balance updated)

---

## Troubleshooting

### Products not showing on storefront?

```
✓ Merchant status = 'active'?
✓ Merchant verification = 'verified'?
✓ Product approval_status = 'approved'?
✓ Product is_available = 'True'?
✓ Try: /products/ page
✓ Or: /store/<merchant-slug>/
```

### Merchant can't see orders?

```
✓ Product.merchant field set correctly?
✓ Order items linked to merchant?
✓ User role = 'merchant'?
✓ Check: /merchants/portal/orders/
```

### Commission not calculated?

```
✓ Order item fulfillment_status = 'delivered'?
✓ Merchant wallet exists?
✓ Check: Merchant.transactions.all()
```

---

## Key URLs

| Purpose           | URL                          |
| ----------------- | ---------------------------- |
| Admin Panel       | /admin/                      |
| Approve Products  | /admin/product-approvals/    |
| Manage Merchants  | /admin/merchants/merchant/   |
| Customer Home     | /                            |
| Product List      | /products/                   |
| Merchant Store    | /store/<slug>/               |
| Merchant Portal   | /merchants/portal/dashboard/ |
| Merchant Products | /merchants/portal/products/  |
| Merchant Orders   | /merchants/portal/orders/    |

---

## That's It! 🎉

The feature is fully functional. Just activate a merchant, approve products, and it works!

For detailed documentation, see: `MERCHANT_PRODUCTS_IMPLEMENTATION.md`
