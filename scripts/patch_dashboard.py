from pathlib import Path

p = Path('templates/admin/dashboard.html')
t = p.read_text(encoding='utf-8')

old = """        <motion class=\"stat-icon blog\">"""
# fix - read file
if '<motion' in t:
    t = t.replace('<motion ', '<div ').replace('</motion>', '</div>')

old_block = """        <div class="stat-card">
            <motion class=\"stat-icon blog\">"""

# simpler marker
start = t.find('<h3>{{ total_posts }}</h3>')
if start == -1:
    print('marker not found')
    exit(1)

# find start of stat-card before total_posts
card_start = t.rfind('<div class="stat-card">', 0, start)
card_end = t.find('</motion>', start)
if card_end == -1:
    card_end = t.find('</div>', start) + len('</motion>')
    # find closing of stat-card - third closing div after total_posts
    pos = start
    for _ in range(4):
        card_end = t.find('</motion>', card_end + 1) if '</motion>' in t else t.find('</motion>', card_end + 1)
else:
    card_end = t.find('</motion>', card_end) + 6

# brute: replace blog posts stat card
import re
pattern = r'        <div class="stat-card">\s*<div class="stat-icon blog">.*?</div>\s*</motion>\s*'
replacement = '''        <a href="{% url 'admin_panel:product_approvals' %}" class="stat-card" style="text-decoration:none;color:inherit;">
            <div class="stat-icon blog">
                <i class="fas fa-clipboard-check"></i>
            </div>
            <div class="stat-content">
                <h3>{{ pending_product_count }}</h3>
                <p>Pending Approvals</p>
                {% if pending_product_count %}
                <span class="stat-change neutral">Needs review</span>
                {% else %}
                <span class="stat-change positive">All clear</span>
                {% endif %}
            </div>
        </a>
'''
new_t, n = re.subn(
    r'        <div class="stat-card">\s*<div class="stat-icon blog">[\s\S]*?<span class="stat-change neutral">\+5% from last month</span>\s*</div>\s*</div>',
    replacement.strip() + '\n',
    t,
    count=1,
)
if n:
    t = new_t
    print('replaced stat card')
else:
    print('stat card pattern failed')

insert_marker = '    <!-- Recent Activity -->'
pending_block = '''
    {% if pending_product_count %}
    <div class="activity-card" style="margin-bottom:24px;">
        <div class="card-header">
            <h3><i class="fas fa-hourglass-half me-2"></i>Product approval requests</h3>
            <a href="{% url 'admin_panel:product_approvals' %}" class="view-all">Review all ({{ pending_product_count }})</a>
        </div>
        <div class="card-content">
            {% for product in pending_products %}
            <div class="order-item">
                <div class="order-info" style="flex-direction:row;align-items:center;gap:12px;">
                    {% with img=product.images.first %}
                    {% if img %}<img src="{{ img.image.url }}" alt="" style="width:48px;height:48px;object-fit:cover;border-radius:8px;">{% endif %}
                    {% endwith %}
                    <div>
                        <span class="order-id">{{ product.name }}</span>
                        <span class="order-user">{{ product.merchant.business_name }} · ₹{{ product.price }}</span>
                    </div>
                </div>
                <div style="display:flex;gap:8px;">
                    <a href="{% url 'admin_panel:product_review' product.id %}" class="btn btn-sm btn-secondary">Review</a>
                    <button type="button" class="btn btn-sm btn-success dash-approve" data-id="{{ product.id }}">Approve</button>
                </div>
            </div>
            {% endfor %}
        </motion>
    </div>
    {% endif %}

'''
if insert_marker in t and 'pending_products' not in t:
    t = t.replace(insert_marker, pending_block + insert_marker)
    print('inserted pending block')

t = t.replace('<motion ', '<div ').replace('</motion>', '</motion>')
while '</motion>' in t:
    t = t.replace('</motion>', '</div>')

# dashboard js
if 'dash-approve' not in t and '{% endblock %}' in t:
    js = """
<script>
document.querySelectorAll('.dash-approve').forEach(function(btn) {
    btn.addEventListener('click', function() {
        if (!confirm('Approve this product?')) return;
        var fd = new FormData();
        fd.append('action', 'approve');
        fetch('/admin-panel/products/' + btn.dataset.id + '/approve/', {
            method: 'POST',
            headers: {'X-CSRFToken': '{{ csrf_token }}'},
            body: fd
        }).then(function(r) { return r.json(); }).then(function(d) {
            if (d.success) location.reload();
            else alert('Failed');
        });
    });
});
</script>
"""
    # append before last endblock in file - find extra_js block or add at end of content
    idx = t.rfind('{% endblock %}')
    if idx > 0:
        t = t[:idx] + js + '\n' + t[idx:]
        print('added js')

p.write_text(t, encoding='utf-8')
print('done')
