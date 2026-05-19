# Merchant Products Feature - Implementation Guide

## Feature Overview

Merchants can upload and sell products. Once approved by admins, these products are visible to all users and available for purchase. Merchants can then manage orders and track payments.

---

## Complete Workflow

### Phase 1: Merchant Registration & Activation

1. **Create Merchant Account** (Django Admin)

   ```
   Admin Panel → Merchants → Add Merchant
   ```

   Fields to set:
   - `business_name`, `owner_name`, `email`, `phone`
   - `franchise_type` (franchise/partner/flagship)
   - `territory` (if applicable)
   - `commission_rate` (platform commission %)

2. **Set Merchant Status to ACTIVE** (Critical!)

   ```
   Admin Panel → Merchants → Select Merchant → Change Status to "Active"
   ```

   - Default status: `pending` (products won't show)
   - Must be changed to: `active` (enables product visibility)

3. **Verify Merchant Account** (Critical!)
   ```
   Admin Panel → Merchants → Select Merchant → Change Verification Status to "Verified"
   ```

   - Default status: `pending` (blocks product visibility)
   - Must be changed to: `verified` (enables product visibility)

---

### Phase 2: Merchant Uploads Products

1. **Merchant Login** → Navigate to Merchant Portal

   ```
   /merchants/portal/dashboard/
   ```

2. **Add Product**

   ```
   Merchant Portal → Products → Add Product
   ```

   Fields:
   - Product name, description, price
   - Category, brand, target group, gender
   - Variants (sizes available)
   - Images

3. **Submit for Approval**
   - Product status becomes: `PENDING`
   - System creates notification for admins
   - Merchant receives confirmation email

---

### Phase 3: Admin Reviews & Approves

1. **Admin Reviews Product**

   ```
   Admin Panel → Product Approvals → Review Product
   ```

   - View product details, images, variants
   - Check for quality/policy compliance

2. **Approve or Reject**
   - **Approve**: Sets `approval_status = "approved"` and `is_available = True`
   - **Reject**: Sets status to "rejected" with reason
   - Merchant is notified either way

---

### Phase 4: Users See & Purchase Products

1. **Products Appear on Storefront**
   - Approved merchant products visible to all users
   - Can be filtered by price, category, brand, etc.
   - Displayed in:
     - `/` (home - if featured)
     - `/products/` (product list)
     - `/store/<merchant-slug>/` (merchant store)
     - Search results

2. **Users Add to Cart & Purchase**
   - Same process as HQ products
   - Orders automatically route to correct merchant
   - Support for COD and online payments

---

### Phase 5: Merchant Manages Orders

1. **View Orders**

   ```
   Merchant Portal → Orders
   /merchants/portal/orders/
   ```

   - See all orders containing their products
   - Filter by fulfillment status (pending, accepted, packed, shipped, delivered)

2. **Update Fulfillment Status**
   - Accept order
   - Mark as packed
   - Mark as shipped
   - Mark as delivered (triggers payment to merchant)

3. **Track Commission & Payments**
   ```
   Merchant Portal → Wallet
   ```

   - View transaction history
   - Platform commission deducted automatically
   - Payout requests

---

## Database Fields Reference

### Product Model

```python
approval_status  # 'draft', 'pending', 'approved', 'rejected', 'archived'
is_available     # True = publicly visible (if other conditions met)
merchant         # ForeignKey to Merchant (NULL = HQ product)
```

### Merchant Model

```python
status                # 'pending', 'active', 'suspended', 'inactive'
verification_status   # 'pending', 'verified', 'rejected'
commission_rate       # Platform commission %
```

### OrderItem Model

```python
merchant             # Links order item to merchant
fulfillment_status   # 'pending', 'accepted', 'packed', 'shipped', 'delivered', etc.
fulfillment_type     # 'merchant' or 'hq'
```

---

## Product Visibility Logic

Products are visible to public if ALL conditions are met:

```python
# public_product_queryset() in merchants/services.py
is_available=True AND
approval_status='approved' AND
(
    merchant is NULL  # HQ product, always visible if approved
    OR
    (merchant.status='active' AND merchant.verification_status='verified')  # Merchant must be active+verified
)
```

---

## URLs Routing

### Customer Views

- `/` - Home with featured products
- `/products/` - All products listing
- `/products/<slug>/` - Product detail
- `/store/<merchant-slug>/` - Merchant store
- `/store/<merchant-slug>/products/` - Merchant products

### Merchant Portal

- `/merchants/portal/dashboard/` - Merchant dashboard
- `/merchants/portal/products/` - Merchant's product list
- `/merchants/portal/products/add/` - Upload product
- `/merchants/portal/products/<id>/edit/` - Edit product
- `/merchants/portal/orders/` - Manage orders
- `/merchants/portal/wallet/` - Commission & payments

### Admin Panel

- `/admin/merchants/merchant/` - Manage merchants
- `/admin/products/` - View all products
- `/admin/product-approvals/` - Approve/reject merchant products

---

## Troubleshooting

### Products not visible to users after approval

1. Check merchant `status` = `active` ✓
2. Check merchant `verification_status` = `verified` ✓
3. Check product `approval_status` = `approved` ✓
4. Check product `is_available` = `True` ✓
5. Check merchant is not suspended

### Merchants can't see their orders

1. Verify order items have correct `merchant` FK set
2. Check OrderItem.merchant matches product.merchant
3. Verify user role is set to "merchant"

### Commission not calculated

1. Ensure `fulfillment_status` updated to "delivered"
2. Check merchant has wallet (auto-created on first order)
3. Verify commission_rate in Merchant model

---

## API Endpoints for Frontend

### Get approved merchant products

```
GET /api/public/products/<id>/
GET /store/<slug>/products/?search=...&sort=...
```

### Create order

```
POST /orders/create/
```

### Submit payment (Razorpay)

```
POST /orders/create-razorpay-order/
```

---

## Quick Reference: Admin Commands

```bash
# Set merchant to active+verified (can also use admin panel)
python manage.py shell
>>> from merchants.models import Merchant
>>> m = Merchant.objects.get(merchant_id='EQ-M-00001')
>>> m.status = 'active'
>>> m.verification_status = 'verified'
>>> m.save()
```
