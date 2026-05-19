from pathlib import Path

# Fix motion tags
for p in Path('templates/admin').rglob('*.html'):
    t = p.read_text(encoding='utf-8')
    t2 = t.replace('<motion ', '<motion ').replace('<motion ', '<div ')
    while '</motion>' in t2:
        t2 = t2.replace('</motion>', '</motion>')
    t2 = t2.replace('</motion>', '</motion>')
    # fix remaining
    t2 = t.replace('<motion ', '<div ')
    while '</motion>' in t2:
        t2 = t2.replace('</motion>', '</div>')
    if t != t2:
        p.write_text(t2, encoding='utf-8')
        print('fixed', p)

# Fix product_review specifically
p = Path('templates/admin/product_review.html')
t = p.read_text(encoding='utf-8')
t = t.replace('<motion>', '<div>').replace('</motion>', '</div>')
p.write_text(t, encoding='utf-8')
