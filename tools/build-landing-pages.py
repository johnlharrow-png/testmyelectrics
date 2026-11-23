# Builds the Google Ads landing pages from book-online.html, one per kind of search:
#   landlord-eicr.html, electrical-safety-certificate.html and eicr-<town>.html
# Each page is /book-online with its own title, headline, intro, a short section about the search
# and (for towns) the postcodes covered. Everything else (booking box, logos, prices, FAQ, tracking)
# comes straight from book-online.html, so after changing that page run:
#     python tools/build-landing-pages.py
# and commit the pages it writes. Don't edit the generated pages by hand: the next run overwrites them.
# Before adding a town, check its postcodes on the booking app (POST /api/public/postcode).
import html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(ROOT, 'book-online.html'), encoding='utf-8').read()
PRICE = '<span class="hl"><span data-price="EICR_DOM.studio">£79</span>&nbsp;+&nbsp;VAT</span>'
TICK = '<svg class="icon"><use href="#i-check"/></svg>'
EMAIL = ('<a href="mailto:bookings@testmyelectrics.com" data-email-link>'
         '<span data-email>bookings@testmyelectrics.com</span></a>')


def swap(page, old, new, count=1):
    assert page.count(old) >= 1, f'not found in book-online.html: {old[:70]}'
    return page.replace(old, new, count)


def ticks(items):
    return '<ul class="bo-ticks">' + ''.join(f'<li>{TICK}<span>{i}</span></li>' for i in items) + '</ul>'


def build(slug, title, description, h1, line, local_id, local_h2, local_body, areas=None, placeholder=None,
          drop_homebuyer=False):
    p = SRC
    p = swap(p, '<title>Book an EICR from £79 + VAT | Essex &amp; East London | testmyelectrics.com</title>',
             f'<title>{html.escape(title, quote=False)}</title>')
    p = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{html.escape(description)}">', p, count=1)
    p = swap(p, '<link rel="canonical" href="https://www.testmyelectrics.com/book-online">',
             f'<link rel="canonical" href="https://www.testmyelectrics.com/{slug}">')
    p = swap(p, f'<h1>EICR certificates from {PRICE}</h1>', f'<h1>{h1} from {PRICE}</h1>')
    p = re.sub(r'<p class="bo-line">.*?</p>', f'<p class="bo-line">{line}</p>', p, count=1, flags=re.S)
    if placeholder:
        p = swap(p, 'placeholder="e.g. CM1 1AB"', f'placeholder="e.g. {placeholder}"')
    local = (f'    <section class="bo-section bo-local" aria-labelledby="{local_id}">\n'
             f'      <div class="container">\n        <h2 id="{local_id}">{local_h2}</h2>\n'
             f'        {local_body}\n      </div>\n    </section>\n\n')
    p = swap(p, '    <!-- 3. Prices', local + '    <!-- 3. Prices')
    if drop_homebuyer:
        p = re.sub(r'\s*<article class="price-card bo-homebuyer".*?</article>', '', p, count=1, flags=re.S)
    if areas:
        p = re.sub(r'(<h2 id="bo-areas">)[^<]*(</h2>\s*)<p>.*?</p>', r'\g<1>' + areas[0] + r'\g<2>' + f'<p>{areas[1]}</p>',
                   p, count=1, flags=re.S)
    p = p.replace('<!-- Ad landing page:', f'<!-- Generated from book-online.html by tools/build-landing-pages.py. Ad landing page:', 1)
    with open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(p)
    return slug


pages = []

pages.append(build(
    'landlord-eicr',
    'Landlord EICR from £79 + VAT | Electrical safety certificate | Essex & East London',
    'Landlord EICRs (electrical safety certificates) from £79 + VAT across Essex and East London. '
    'NAPIT-registered electricians, book online, certificate in your online account.',
    'Landlord EICRs',
    'Your landlord electrical safety certificate, from NAPIT-registered electricians across Essex &amp; East London. '
    'Pick a slot and pay online.',
    'bo-landlord', 'What landlords need to do',
    '<p>The Electrical Safety Standards in the Private Rented Sector (England) Regulations 2020 say every rented home '
    'needs an Electrical Installation Condition Report (EICR):</p>'
    + ticks([
        'A new EICR at least every 5 years, or sooner if the last report says so.',
        'A copy to existing tenants within 28 days, to new tenants before they move in, and to the council within 7 days if they ask.',
        'Any C1, C2 or FI items put right within 28 days, or sooner if the report says so. We quote for the work and do nothing without your approval.',
        'Tenant at home? Add their details when you book and we arrange access with them, or with your letting agent.',
    ])
    + f'<p>Several properties? Email {EMAIL} for a portfolio price. Letting agent? '
      '<a href="/letting-agents">Open an agent account</a>.</p>',
))

pages.append(build(
    'electrical-safety-certificate',
    'Electrical safety certificate (EICR) from £79 + VAT | Essex & East London',
    'Electrical safety certificates (EICRs) from £79 + VAT across Essex and East London. A full inspection of your '
    'home by NAPIT-registered electricians. Book online.',
    'Electrical safety certificates',
    'A full electrical safety inspection of your home by NAPIT-registered electricians across Essex &amp; East London. '
    'Pick a slot and pay online.',
    'bo-esc', 'What is an electrical safety certificate?',
    '<p>Its proper name is an Electrical Installation Condition Report (EICR). Our electrician inspects and tests your '
    'wiring, fuse board, sockets and fittings, and the report shows whether the installation is safe. It\'s worth '
    'having one when you:</p>'
    + ticks([
        'Let a property: landlords need one at least every 5 years.',
        'Buy or sell a home: our homebuyer\'s report adds repair prices to help you negotiate.',
        'Haven\'t had the wiring checked for 10 years, or notice scorch marks, tripping or flickering lights.',
    ]),
))

# Town pages. Postcodes checked on the booking app on 23 Nov 2026.
TOWNS = [
    ('chelmsford', 'Chelmsford', ['CM1', 'CM2', 'CM3'], 'CM2 6AB',
     'Springfield, Great Baddow, Writtle, Broomfield and South Woodham Ferrers'),
    ('colchester', 'Colchester', ['CO1', 'CO2', 'CO3', 'CO4', 'CO5', 'CO6', 'CO7'], 'CO3 3AB',
     'Stanway, Wivenhoe, Tiptree, West Mersea and Highwoods'),
    ('southend', 'Southend', ['SS0', 'SS1', 'SS2', 'SS3', 'SS9'], 'SS1 2AB',
     'Westcliff-on-Sea, Leigh-on-Sea, Shoeburyness, Thorpe Bay and Prittlewell'),
    ('basildon', 'Basildon', ['SS13', 'SS14', 'SS15', 'SS16'], 'SS14 1AB',
     'Pitsea, Laindon, Vange and Langdon Hills'),
    ('benfleet', 'Benfleet', ['SS7'], 'SS7 1AB',
     'South Benfleet, Thundersley and Hadleigh'),
    ('billericay', 'Billericay', ['CM11', 'CM12'], 'CM12 9AB',
     'Great Burstead, Little Burstead and Ramsden Heath'),
    ('brentwood', 'Brentwood', ['CM13', 'CM14', 'CM15'], 'CM14 4AB',
     'Shenfield, Hutton, Warley and Pilgrims Hatch'),
    ('harlow', 'Harlow', ['CM17', 'CM18', 'CM19', 'CM20'], 'CM20 1AB',
     'Old Harlow, Church Langley, Potter Street and Great Parndon'),
    ('leigh-on-sea', 'Leigh-on-Sea', ['SS9'], 'SS9 1AB',
     'Old Leigh, Eastwood and Belfairs'),
    ('romford', 'Romford', ['RM1', 'RM2', 'RM3', 'RM4', 'RM5', 'RM6', 'RM7'], 'RM1 3AB',
     'Gidea Park, Harold Wood, Harold Hill, Collier Row and Chadwell Heath'),
    ('east-london', 'East London', ['E4', 'IG1', 'IG2', 'IG3', 'IG4', 'IG5', 'IG6', 'IG7', 'IG8', 'IG11',
                                    'RM8', 'RM9', 'RM10', 'RM11', 'RM12', 'RM13', 'RM14'], 'IG1 1AB',
     'Chingford, Ilford, Woodford, Barking, Dagenham, Hornchurch and Upminster'),
]


def join(items):
    return ', '.join(items[:-1]) + ' and ' + items[-1] if len(items) > 1 else items[0]


for slug, town, districts, example, nearby in TOWNS:
    pcs = join(districts)
    extra = (' For homes in East London we cover E4 and the IG and RM postcodes listed; other E postcodes '
             'are outside our area.' if slug == 'east-london' else '')
    pages.append(build(
        f'eicr-{slug}',
        f'EICR in {town} from £79 + VAT | testmyelectrics.com',
        f'Book an EICR in {town} from £79 + VAT. NAPIT-registered electricians covering {pcs}. '
        f'Your certificate is emailed and saved in your online account.',
        f'EICR in {town}',
        f'NAPIT-registered electricians covering {town} ({pcs}). Pick a slot and pay online.',
        'bo-town', f'EICRs in {town}',
        f'<p>We test homes and rented properties across {town} and nearby, including {nearby}. '
        f'Postcodes covered: <span class="bo-postcodes">{pcs}</span>.{extra}</p>'
        + ticks([
            f'The same fixed prices across {town}: you see the full price before you pay.',
            'Choose a morning or afternoon slot that suits you, with free rescheduling up to 24 hours before.',
            'Your EICR certificate is emailed and saved in your online account.',
        ]),
        areas=('We also cover', 'Chelmsford, Southend, Basildon, Colchester, Brentwood, Billericay, Harlow, Romford, '
               'Ilford and surrounding areas: postcodes <span data-coverage-areas>CM, SS, CO, RM, IG, E4, EN9, CB10 and CB11</span>.'),
        placeholder=example,
    ))

print('wrote', len(pages), 'pages:', ', '.join(pages))
