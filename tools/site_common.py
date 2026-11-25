# Shared by the guide builders (build-eicr-guide.py, build-guides.py).
# A guide page is book-online.html with its own <main>, title, description, canonical and FAQ JSON-LD,
# so it keeps the same head (fonts, styles, tracking), header, footer, cookie banner and scripts.
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(ROOT, 'book-online.html'), encoding='utf-8').read()
SITE = 'https://www.testmyelectrics.com'

# Prices: site.js fills every data-price from assets/config.js, which must match the back office.
# The figures written into the HTML (and the FAQ answers, which are plain text) are read from
# config.js here, so rerun the builders after changing a price there.
_CFG = open(os.path.join(ROOT, 'assets', 'config.js'), encoding='utf-8').read()


def _prices(service):
    body = re.search(r'\n\s*' + service + r':\s*\{([^}]*)\}', _CFG).group(1)
    return {k: float(v) for k, v in re.findall(r'(\w+):\s*([\d.]+)', body)}


PRICES = {s: _prices(s) for s in ('EICR_DOM', 'HOMEBUYER', 'PAT', 'FIRE')}


def gbp(n):
    return f'£{int(n):,}' if float(n).is_integer() else f'£{n:,.2f}'


def price(path):
    """'EICR_DOM.studio' -> '£79' (ex VAT), for plain text such as FAQ answers."""
    service, key = path.split('.')
    return gbp(PRICES[service][key])


def pspan(path):
    """A price that site.js keeps in step with config.js. Ex VAT: add ' + VAT' after it."""
    return f'<span data-price="{path}">{price(path)}</span>'


def cfg(path):
    """A number from config.pricing (e.g. the circuits included), kept in step by site.js."""
    service, key = path.split('.')
    v = PRICES[service][key]
    return f'<span data-cfg="pricing.{path}">{int(v) if v.is_integer() else v}</span>'


EICR_FROM = f'{pspan("EICR_DOM.studio")} + VAT'

EMAIL = ('<a href="mailto:bookings@testmyelectrics.com" data-email-link>'
         '<span data-email>bookings@testmyelectrics.com</span></a>')

# The guides, for the "More guides" links at the foot of each one
GUIDES = [
    ('eicr-explained', 'What is an EICR? The codes explained', 'file'),
    ('eicr-cost', 'How much does an EICR cost?', 'key'),
    ('landlord-electrical-safety', 'Landlord electrical safety: the rules', 'home'),
    ('smoke-co-alarm-rules', 'Smoke and CO alarm rules for landlords', 'alarm'),
    ('eicr-selling-a-house', 'Do you need an EICR to sell a house?', 'pin'),
]


def swap(page, old, new):
    assert page.count(old) == 1, f'not found once in book-online.html: {old[:70]}'
    return page.replace(old, new)


def icon(name):
    return f'<svg class="icon" aria-hidden="true"><use href="#i-{name}"/></svg>'


def faq_html(faq):
    # Answers are plain text, escaped, so the JSON-LD and the page say exactly the same thing
    out = []
    for q, a in faq:
        out.append(
            '          <details>\n'
            f'            <summary>{html.escape(q)}<span class="plus">{icon("plus")}</span></summary>\n'
            f'            <div class="faq-a"><p>{html.escape(a)}</p></div>\n'
            '          </details>')
    return '\n'.join(out)


def faq_schema(faq):
    data = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


def faq_section(faq, h2='Questions', sec_id='eg-faq'):
    return f'''    <section class="bo-section bo-faq" id="faq" aria-labelledby="{sec_id}">
      <div class="container">
        <h2 id="{sec_id}">{h2}</h2>
        <div class="faq">
{faq_html(faq)}
          <p class="faq-more">Can't find your answer? Email {EMAIL}</p>
        </div>
      </div>
    </section>
'''


def check(ic, title, text):
    return f'<li class="eg-check"><span class="eg-ic">{icon(ic)}</span><h3>{title}</h3><p>{text}</p></li>'


def rules(items):
    return '<ol class="eg-rules">' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'


def more_guides(current):
    links = ''.join(
        f'<li><a href="/{slug}"><span class="eg-ic">{icon(ic)}</span><span>{html.escape(name)}</span>{icon("arrow")}</a></li>'
        for slug, name, ic in GUIDES if slug != current)
    return f'''    <section class="bo-section eg-alt eg-guides-wrap" aria-labelledby="eg-guides">
      <div class="container">
        <h2 id="eg-guides">More guides</h2>
        <ul class="eg-guides">{links}</ul>
      </div>
    </section>
'''


def cta(h2, text, src=''):
    src = f'\n        <p class="eg-src">{src}</p>' if src else ''
    return f'''    <section class="bo-section eg-cta" aria-labelledby="eg-book">
      <div class="container">
        <h2 id="eg-book">{h2}</h2>
        <p>{text}</p>
        <a class="btn btn-volt" href="/book-online">Check dates &amp; prices</a>{src}
      </div>
    </section>
'''


def build_page(slug, title, description, main, faq, note):
    """Write <slug>.html: book-online.html with this page's title, description, canonical, FAQ schema and <main>."""
    p = SRC
    p = swap(p, '<title>Book an EICR from £79 + VAT | Essex &amp; East London | testmyelectrics.com</title>',
             f'<title>{html.escape(title, quote=False)}</title>')
    p = re.sub(r'<meta name="description" content="[^"]*">',
               lambda m: f'<meta name="description" content="{html.escape(description)}">', p, count=1)
    p = swap(p, '  <!-- Ad landing page, open to search engines. The town pages generated from it point their canonical here. -->\n',
             f'  <!-- {note} Edit the script, not this file. -->\n')
    p = swap(p, f'<link rel="canonical" href="{SITE}/book-online">', f'<link rel="canonical" href="{SITE}/{slug}">')
    # no hero photo on a guide page, so don't preload it
    p = re.sub(r'  <link rel="preload" as="image"[^\n]*\n', '', p, count=1)
    p = swap(p, '</head>', f'  {faq_schema(faq)}\n</head>')
    start, end = p.index('  <main id="main">'), p.index('  </main>') + len('  </main>\n')
    # the header menu jumps to sections of /book-online; a guide page doesn't have them, so link to that page
    top = p[:start]
    for anchor in ('#pricing', '#how', '#faq', '#areas'):
        top = top.replace(f'href="{anchor}"', f'href="/book-online{anchor}"')
    p = top + main + p[end:]
    with open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(p)
    return slug


def inline_css():
    """Put each page's own styles inside it (tools/inline-css.mjs), so the first screen draws without
    waiting for styles.css. Needs `npm install` once in the repo."""
    import subprocess
    if not os.path.isdir(os.path.join(ROOT, 'node_modules', 'beasties')):
        print('NOTE: critical CSS not rebuilt. Run `npm install`, then `npm run inline-css`.')
        return
    subprocess.run(['node', os.path.join(ROOT, 'tools', 'inline-css.mjs')], check=True, stdout=subprocess.DEVNULL)
    print('critical CSS rebuilt on every page')
