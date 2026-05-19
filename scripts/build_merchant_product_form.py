import re
from pathlib import Path

src = Path('templates/admin/product_form.html').read_text(encoding='utf-8')
src = src.replace("{% extends 'admin/base.html' %}", "{% extends 'merchants/portal_base.html' %}")
src = src.replace('Admin Panel - EQUILA Fashion', '{{ merchant.business_name }}')
src = src.replace("{% url 'admin_panel:products' %}", "{% url 'merchants:products' %}")
src = src.replace('admin_panel:product_size_options', 'merchants:product_size_options')

src = re.sub(
    r'\s*<motion class="col-md-6">\s*<label class="form-label">Availability</label>.*?</div>',
    '',
    src,
    flags=re.S,
)
src = re.sub(
    r'\s*<div class="col-md-6">\s*<label class="form-label">Availability</label>.*?</motion>',
    '',
    src,
    flags=re.S,
)

src = src.replace(
    '<div class="col-md-4">\n                            <label class="form-label">Price</label>\n                            {{ form.price }}',
    '<motion class="col-md-4">\n                            <label class="form-label">Price (₹)</label>\n                            {{ form.price }}\n                        </div>\n                        <div class="col-md-4">\n                            <label class="form-label">Original price (optional)</label>\n                            {{ form.original_price }}',
)

src = src.replace(
    '''<div class="form-actions-top">
            <a href="{% url 'merchants:products' %}" class="btn btn-secondary">
                <i class="fas fa-arrow-left"></i>
                Back
            </a>
            <button type="submit" class="btn btn-primary">
                <i class="fas fa-save"></i>
                Save Product
            </button>
        </div>''',
    '''<motion class="info-banner mb-3"><i class="fas fa-info-circle me-2"></i>Submit for approval to publish on the main shop. Drafts are only visible to you.</div>
        <div class="form-actions-top">
            <a href="{% url 'merchants:products' %}" class="btn btn-secondary"><i class="fas fa-arrow-left"></i> Back</a>
            <div class="d-flex gap-2">
                <button type="submit" name="action" value="draft" class="btn btn-secondary"><i class="fas fa-file"></i> Save draft</button>
                <button type="submit" name="action" value="submit" class="btn btn-primary"><i class="fas fa-paper-plane"></i> Submit for approval</button>
            </div>
        </div>
        {% if product.rejection_reason %}
        <div class="alert alert-warning">Rejected: {{ product.rejection_reason }}</motion>
        {% endif %}''',
)

src = src.replace(
    '''<div class="form-actions-bottom">
            <a href="{% url 'merchants:products' %}" class="btn btn-secondary">Cancel</a>
            <button type="submit" class="btn btn-primary">
                <i class="fas fa-save"></i>
                Save Product
            </button>
        </div>''',
    '''<div class="form-actions-bottom">
            <a href="{% url 'merchants:products' %}" class="btn btn-secondary">Cancel</a>
            <button type="submit" name="action" value="draft" class="btn btn-secondary">Save draft</button>
            <button type="submit" name="action" value="submit" class="btn btn-primary"><i class="fas fa-paper-plane"></i> Submit for approval</button>
        </div>''',
)

src = src.replace('<motion ', '<div ').replace('</motion>', '</div>')
Path('templates/merchants/product_form.html').write_text(src, encoding='utf-8')
print('OK')
