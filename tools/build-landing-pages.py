# Builds the Google Ads landing pages from book-online.html, one per kind of search:
#   landlord-eicr.html, electrical-safety-certificate.html and eicr-<town>.html
# Each page is /book-online with its own title, headline, intro, a short section about the search
# and (for towns) the postcodes covered. Everything else (booking box, logos, prices, FAQ, tracking)
# comes straight from book-online.html, so after changing that page run:
#     python tools/build-landing-pages.py
# and commit the pages it writes. It also rebuilds each page's critical CSS (tools/inline-css.mjs; `npm install` once). Don't edit the generated pages by hand: the next run overwrites them.
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
          drop_homebuyer=False, own_canonical=True, extra=None, price=PRICE, post=None):
    p = SRC
    # /book-online's own "on the day" section is only for that page; each built page gets its own content instead
    p = re.sub(r'\s*<!-- book-online only: start.*?<!-- book-online only: end -->', '', p, count=1, flags=re.S)
    p = swap(p, '<title>Book an EICR from £79 + VAT | Essex &amp; East London | testmyelectrics.com</title>',
             f'<title>{html.escape(title, quote=False)}</title>')
    p = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{html.escape(description)}">', p, count=1)
    # Town pages share most of their text with /book-online, so they point their canonical there:
    # Google treats a set of near-identical city pages as doorway pages. Give a town its own
    # canonical (own_canonical=True) once its page has enough text of its own.
    if own_canonical:
        p = swap(p, '<link rel="canonical" href="https://www.testmyelectrics.com/book-online">',
                 f'<link rel="canonical" href="https://www.testmyelectrics.com/{slug}">')
    p = swap(p, f'<h1>EICR certificates from {PRICE}</h1>', f'<h1>{h1} from {price}</h1>')
    p = re.sub(r'<p class="bo-line">.*?</p>', f'<p class="bo-line">{line}</p>', p, count=1, flags=re.S)
    if placeholder:
        p = swap(p, 'placeholder="e.g. CM1 1AB"', f'placeholder="e.g. {placeholder}"')
    local = (f'    <section class="bo-section bo-local" aria-labelledby="{local_id}">\n'
             f'      <div class="container">\n        <h2 id="{local_id}">{local_h2}</h2>\n'
             f'        {local_body}\n      </div>\n    </section>\n\n')
    p = swap(p, '    <!-- 3. Prices', local + '    <!-- 3. Prices')
    # A longer section of the page's own (25 Nov 2026), after How it works, so the prices stay high on the page
    if extra:
        p = swap(p, '    <!-- 5. Reviews', extra + '\n\n    <!-- 5. Reviews')
    if drop_homebuyer:
        p = re.sub(r'\s*<article class="price-card bo-homebuyer".*?</article>', '', p, count=1, flags=re.S)
    if areas:
        p = re.sub(r'(<h2 id="bo-areas">)[^<]*(</h2>\s*)<p>.*?</p>', r'\g<1>' + areas[0] + r'\g<2>' + f'<p>{areas[1]}</p>',
                   p, count=1, flags=re.S)
    p = p.replace('<!-- Ad landing page:', f'<!-- Generated from book-online.html by tools/build-landing-pages.py. Ad landing page:', 1)
    if post:
        p = post(p)
    with open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(p)
    return slug


# ---------------------------------------------------------------------------------------------------------------
# Each ad page's own longer section (25 Nov 2026, Wayne: landing page experience "Average" isn't good enough).
# Google's landing page guidance rewards original, useful content; these pages were 90% /book-online.
# Facts match terms.html and the landlord guide (landlord-electrical-safety.html); keep them in step.
# ---------------------------------------------------------------------------------------------------------------
def section(sid, h2, body, cls=''):
    return (f'    <section class="bo-section bo-more {cls}" aria-labelledby="{sid}">\n      <div class="container">\n'
            f'        <h2 id="{sid}">{h2}</h2>\n        {body}\n      </div>\n    </section>')


def shot(name, alt, w, h, caption):
    return (f'<figure class="bo-sample"><img src="/assets/img/sample/{name}-1000.webp" '
            f'srcset="/assets/img/sample/{name}-600.webp 600w, /assets/img/sample/{name}-1000.webp 1000w" '
            f'sizes="(max-width: 760px) 100vw, 860px" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">'
            f'<figcaption>{caption}</figcaption></figure>')


CODES_DL = ('<dl class="bo-codes">'
         '<div><dt><span class="code c1">C1</span> Danger present</dt><dd>A risk of injury now. With your permission we make '
         'it safe on the day, for example by isolating the circuit.</dd></div>'
         '<div><dt><span class="code c2">C2</span> Potentially dangerous</dt><dd>Needs putting right urgently. For landlords, '
         'within 28 days.</dd></div>'
         '<div><dt><span class="code c3">C3</span> Improvement recommended</dt><dd>Worth planning for, but it doesn\'t fail '
         'the report.</dd></div>'
         '<div><dt><span class="code fi">FI</span> Further investigation</dt><dd>Something the electrician couldn\'t fully '
         'check on the day, with a note of what\'s advised.</dd></div>'
         '</dl>'
         '<p>Only a C1 or C2 makes a report <strong>Unsatisfactory</strong>. A report with only C3 items, or none at all, '
         'is <strong>Satisfactory</strong>.</p>')

CERT_EXTRA = section('bo-sample', 'What an EICR certificate looks like', (
    '<p>This is a sample of the report you get, filled in with made-up details. Yours uses the same layout: the IET '
    'model form for the current wiring regulations, BS 7671:2018+A4:2026, produced by our booking system and signed '
    'off by the electrician who did your inspection.</p>'
    + shot('eicr-summary', 'Page 1 of a sample EICR: the person ordering it, the property, what was inspected and the '
           'overall result, Unsatisfactory', 1000, 844,
           'Page 1: who it\'s for, the property, what was and wasn\'t inspected, and the overall result.')
    + shot('eicr-observations', 'The observations section of a sample EICR: one C2 item (no bonding to the gas pipe) '
           'and one C3 item (lighting circuit without RCD protection)', 1000, 426,
           'The observations: each one coded, with where it is and what to do about it.')
    + '<p class="bo-sample-link"><a href="/assets/sample-eicr.pdf" target="_blank" rel="noopener">See the full 8-page '
      'sample (PDF)</a></p>'
    '<h3>What the report covers</h3>'
    + ticks([
        'Who ordered it, the property, and what the inspection covered, including anything that couldn\'t be checked, '
        'such as cables buried in walls.',
        'The overall result, Satisfactory or Unsatisfactory, and the date your next inspection is due.',
        'The supply and earthing: the type of supply, earthing and bonding conductors, and the main switch.',
        'A schedule of inspection: every item on the IET checklist marked as acceptable, coded, or not applicable.',
        'Test results for every circuit: continuity, insulation resistance, polarity, earth fault loop impedance and '
        'RCD trip times.',
        'Guidance notes explaining the report, as the IET form requires.',
    ])
    + '<h3>What the codes mean</h3>' + CODES_DL
    + '<h3>How long is an EICR valid?</h3>'
    '<p>The report gives the date of the next inspection. For a rented home it\'s at least every 5 years, or sooner if '
    'the report says so. For a home you live in, every 10 years is recommended, and whenever you buy or move into a '
    'property. We email you before the next one is due.</p>'
    '<h3>If the report is Unsatisfactory</h3>'
    '<p>We send you a quote for the work, with photos of each item, and nothing is done without your approval. Once the '
    'work is done you get a certificate for it, which landlords should keep with the report and send to their tenants. '
    '<a href="/eicr-explained">More about the codes</a>.</p>'
), 'bo-sample-wrap')

LANDLORD_EXTRA = section('bo-ll-steps', 'Your landlord duties, and how we take care of them', (
    '<ol class="bo-steps">'
    '<li><strong>An EICR at least every 5 years.</strong> Your online account shows each property\'s status and due '
    'date, and we email you before the next one is due.</li>'
    '<li><strong>A copy for your tenants within 28 days, and for new tenants before they move in.</strong> The report '
    'is emailed to you as a PDF within 48 hours of the visit, ready to forward.</li>'
    '<li><strong>A copy for the council within 7 days, if it asks in writing.</strong> Every report stays in your '
    'account, so you can download it at any time.</li>'
    '<li><strong>C1 and C2 items put right within 28 days, or sooner if the report says so.</strong> We send a quote '
    'with photos of each item. You approve it online and we book the work in. Nothing is done without your say-so.</li>'
    '<li><strong>Written confirmation for your tenants and the council within 28 days of the work.</strong> When the '
    'work is done you get a completion certificate to send them with the report.</li>'
    '</ol>'
    '<h3>Access and your tenants</h3>'
    '<p>Add your tenant\'s or letting agent\'s details when you book and we arrange access with them. Someone aged 18 or '
    'over needs to be there, or a key safe. If a tenant keeps refusing access, keep a record of what you tried: '
    'the rules say you\'re not in breach if you took all reasonable steps.</p>'
    '<h3>If the rules aren\'t followed</h3>'
    '<p>The council can serve a remedial notice giving you 28 days to do the work, and can fine you up to £40,000. '
    'The rules apply to houses in multiple occupation too, and most HMO licence applications ask for a current EICR. '
    'Lodgers who share your home aren\'t covered.</p>'
    '<h3>What the codes mean</h3>' + CODES_DL
    + '<p><a href="/landlord-electrical-safety">The full landlord guide</a> covers the rules in more detail, '
      'including Wales and Scotland.</p>'
))

ESC_EXTRA = section('bo-which-cert', 'Which electrical certificate do you need?', (
    '<p>"Electrical safety certificate" can mean a few different documents. Here\'s which one fits what you\'re '
    'doing.</p>'
    '<dl class="bo-defs">'
    '<div><dt>Renting out a home</dt><dd><strong>An EICR</strong> (electrical installation condition report), at least '
    'every 5 years. This is the one landlords mean by an electrical safety certificate.</dd></div>'
    '<div><dt>Buying or selling a home</dt><dd><strong>An EICR</strong>, or our <strong>homebuyer\'s report</strong>, '
    'which adds a price for each repair so you can negotiate.</dd></div>'
    '<div><dt>New wiring, a new circuit or a new fuse board</dt><dd><strong>An Electrical Installation Certificate '
    '(EIC)</strong> from the electrician who did the work. Some work, such as a new fuse board or a new circuit, also '
    'has to be notified to building control, and you then get a building regulations compliance certificate.</dd></div>'
    '<div><dt>A small job, like an extra socket or light</dt><dd><strong>A Minor Electrical Installation Works '
    'Certificate</strong> from the electrician who did it.</dd></div>'
    '<div><dt>Plug-in appliances you supply to tenants or staff</dt><dd><strong>PAT testing</strong> (portable '
    'appliance testing). It isn\'t part of an EICR, which covers the fixed wiring.</dd></div>'
    '<div><dt>Smoke and carbon monoxide alarms</dt><dd>Landlords must have them, test them on the day a tenancy '
    'starts, and repair or replace them if a tenant reports a fault. <a href="/smoke-co-alarm-rules">The alarm rules '
    'explained</a>.</dd></div>'
    '<div><dt>Gas appliances</dt><dd>A gas safety record (often called a CP12) from a Gas Safe registered engineer. '
    'That\'s not an electrical certificate, and it isn\'t something we do.</dd></div>'
    '</dl>'
    '<h3>What an EICR checks</h3>'
    '<p>An EICR is a full inspection and test of the fixed electrical installation: the fuse board, wiring, sockets, '
    'switches, light fittings and the earthing and bonding. It doesn\'t cover plug-in appliances or gas. '
    '<a href="/eicr-certificate#bo-sample">See a sample EICR</a>.</p>'
))

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
        'Any C1 or C2 items put right within 28 days, or sooner if the report says so. We quote for the work and do nothing without your approval.',
        'Tenant at home? Add their details when you book and we arrange access with them, or with your letting agent.',
    ])
    + f'<p>Several properties? Email {EMAIL} for a portfolio price. Letting agent? '
      '<a href="/letting-agents">Open an agent account</a>.</p>',
    extra=LANDLORD_EXTRA,
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
    extra=ESC_EXTRA,
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


# Each town's own text: what the local council asks of landlords. Every licensing point was checked on the
# council's own website on 23 Nov 2026 (URLs beside each entry). Schemes start and end, so recheck these
# before the dates given, and when a council announces a new scheme. Leave a point out rather than guess.
HMO = ('A house shared by 5 or more people from 2 or more households needs a mandatory HMO licence')
LANDLORD_RULES = ('Every rented home also needs an EICR at least every 5 years, with a copy for your tenants within '
                  '28 days. <a href="/landlord-electrical-safety">The rules for landlords</a>.')
LOCAL = {
    # https://www.chelmsford.gov.uk/business/licensing/licensing-a-house-in-multiple-occupation/
    'chelmsford': [
        'Chelmsford City Council says it has no additional or selective licensing schemes, so most rented homes in the '
        f'city don\'t need a council licence. {HMO}. With the application, the council asks for a current EICR, a gas '
        'safety certificate, a fire risk assessment, a floor plan and a copy of the tenancy agreement.',
        LANDLORD_RULES,
        'Live in your home? A test every 10 years is recommended, and when you move in. Buying in Chelmsford? Our '
        '<a href="/eicr-selling-a-house">homebuyer\'s report</a> prices any repairs before you exchange.',
    ],
    # https://www.new.colchester.gov.uk/licensing/other-licences/house-multiple-occupation-licensing
    # https://www.new.colchester.gov.uk/housing/private-sector-housing/gas-safety-electrical-safety-fire-safety-and-carbon-monoxide-2
    # https://www.new.colchester.gov.uk/news/2026/council-takes-action-help-keep-rented-homes-safe
    'colchester': [
        'Colchester City Council doesn\'t run additional or selective licensing, so most rented homes don\'t need a '
        f'council licence. {HMO}. The council asks for the EICR as part of a valid application, and every mandatory '
        'HMO licence has a condition to send it in when asked.',
        'The council says it will ask landlords for a copy of their latest EICR within 7 days. In September 2026 it '
        'reported fining a housing association £13,600 for not providing one when asked. Your report from us is saved '
        'in your online account, ready to send.',
        LANDLORD_RULES,
    ],
    # https://www.southend.gov.uk/private-housing/selective-licensing-scheme (and /3, /7)
    # https://www.southend.gov.uk/news/article/3608/have-your-say-on-plans-to-renew-and-expand-landlord-licensing-in-southend
    # https://www.southend.gov.uk/HMOlicence
    # Recheck after 30 Nov 2026 (scheme ends) and when the consultation on a new scheme closes.
    'southend': [
        'Southend-on-Sea City Council\'s selective licensing scheme covers parts of Milton, Kursaal, Victoria and '
        'Chalkwell wards. Its licences expire on 30 November 2026. The council is consulting on a new scheme that '
        'could start from 1 April 2027, and says there will be a gap between the two. Current licences don\'t need '
        'renewing: if a new scheme is approved, the council will contact the landlords affected. Its licence '
        'application asks for a valid EICR.',
        f'{HMO}, and the council asks for up-to-date electrical certificates with the application.',
        LANDLORD_RULES,
    ],
    # National rules only: basildon.gov.uk couldn't be read to check local licensing, so none is stated here.
    'basildon': [
        'Basildon Borough Council deals with private renting in Basildon, Pitsea, Laindon and Billericay. '
        f'{HMO} from the council. Check its website for anything else that applies before you let a home.',
        LANDLORD_RULES,
        'Live in your home? A test every 10 years is recommended, and when you move in. If you notice scorch marks, '
        'a fuse board that keeps tripping or lights that flicker, don\'t wait: book a test. If we find a danger, we make '
        'it safe before we leave, with your agreement.',
    ],
    # https://castlepoint.gov.uk/about-the-council
    # https://www.castlepoint.gov.uk/documents/d/guest/houses-in-multiple-occupation-hmo-policy-15-july-2026
    # https://www.castlepoint.gov.uk/w/housing-disrepair
    'benfleet': [
        'Benfleet is in Castle Point, with Thundersley, Hadleigh and Canvey Island, so Castle Point Borough Council '
        f'deals with private renting here. {HMO}. The council\'s HMO policy, adopted in July 2026, asks for a current '
        'satisfactory EICR and a PAT certificate when you apply.',
        'The council\'s housing disrepair page also explains the national electrical safety rules for landlords. If you '
        'live in your home rather than let it, a test every 10 years is recommended, and when you move in.',
        LANDLORD_RULES,
    ],
    # National rules only, as for Basildon.
    'billericay': [
        'Billericay is in Basildon borough, so Basildon Borough Council deals with private renting here. '
        f'{HMO} from the council. Check its website for anything else that applies before you let a home.',
        LANDLORD_RULES,
        'Selling a home in Billericay? An EICR isn\'t a legal requirement, but buyers often ask, and a recent report '
        'answers their questions early. Buying? Our homebuyer\'s report adds a price for each repair. '
        '<a href="/eicr-selling-a-house">EICRs when you buy or sell</a>.',
    ],
    # https://brentwood.gov.uk/houses-in-multiple-occupation-hmos
    # https://www.brentwood.gov.uk/renters-rights-act-2025
    'brentwood': [
        'Brentwood Borough Council deals with private renting in Brentwood, Shenfield, Hutton and the villages around. '
        f'{HMO} from the council, and the council\'s HMO page lists its licence fees.',
        'The council\'s guide to the Renters\' Rights Act 2025 lists the EICR among the documents to have ready for '
        'the new Private Rented Sector database. Ours is saved in your online account, so it\'s easy to find when you '
        'need it, along with the date the next one is due.',
        LANDLORD_RULES,
    ],
    # https://www.harlow.gov.uk/business/licensing/apply-hmo-licence
    # https://www.harlow.gov.uk/policies/corporate-policy-building-harlows-future
    # https://www.harlow.gov.uk/sites/default/files/documents/Harlow%20Local%20Development%20Plan.pdf (new town, 1947)
    'harlow': [
        f'Harlow Council deals with private renting in the town. {HMO}, and the council asks for an EICR that is not '
        'more than 5 years old with the application.',
        'The council\'s corporate plan for 2026 to 2027 includes introducing a selective licensing scheme for private '
        'rented homes across Harlow. It isn\'t in place yet, so check the council\'s website for news.',
        'Harlow was designated a new town in 1947 and built as a series of neighbourhoods. Whatever the age of your '
        'home, if the wiring hasn\'t been checked for 10 years, it\'s worth a test.',
        LANDLORD_RULES,
    ],
    # https://www.southend.gov.uk/private-housing/selective-licensing-scheme (wards), Leigh is a parish of Southend
    'leigh-on-sea': [
        'Leigh-on-Sea is part of Southend-on-Sea, so Southend-on-Sea City Council deals with private renting here. '
        'Its selective licensing scheme covers parts of Milton, Kursaal, Victoria and Chalkwell wards, not the Leigh '
        'wards. Its licences expire on 30 November 2026, and the council is consulting on a new scheme: check its '
        'map if your property is near Chalkwell.',
        f'{HMO}, and the council asks for up-to-date electrical certificates with the application.',
        LANDLORD_RULES + ' Selling in Leigh? <a href="/eicr-selling-a-house">Do you need an EICR to sell?</a>',
    ],
    # https://www.havering.gov.uk/information-landlords/private-rented-property-licensing (and /2)
    # https://www.havering.gov.uk/downloads/file/1675/landlord-private-rented-property-licence-guide
    'romford': [
        'Romford is in the London Borough of Havering. From 18 March 2026 to 17 March 2031, Havering runs selective '
        'licensing in 7 wards: Beam Park, Harold Wood, Rainham and Wennington, Rush Green and Crowlands, Squirrels '
        'Heath, St Albans and St Edwards. Additional licensing covers smaller HMOs across the whole borough, and '
        'larger HMOs need a mandatory licence.',
        'Havering asks licence applicants for an electrical safety certificate within 28 days of asking for it, and '
        'its licence conditions require you to follow the national rules. Parts of RM6 and RM7 are in Redbridge or '
        'Barking and Dagenham, which run their own schemes.',
        LANDLORD_RULES,
    ],
    # https://www.redbridge.gov.uk/housing/landlords/selective-licensing/
    # https://www.lbbd.gov.uk/private-sector-housing/property-licensing/do-i-need-licence (and /application-process)
    # https://www.walthamforest.gov.uk/housing/private-sector-housing/private-rented-property-licensing-prpl/property-licensing-schemes
    # https://www.havering.gov.uk/information-landlords/private-rented-property-licensing
    'east-london': [
        'Each London borough runs its own landlord licensing. All four we cover license some ordinary rented homes, '
        'not just HMOs:',
        '<ul class="bo-boroughs">'
        '<li><strong>Redbridge</strong> (Ilford, Woodford): selective licensing in 17 of its 22 wards (not Bridge, '
        'Clayhall, Fullwell, Monkhams or Wanstead Park). The application asks for an EICR.</li>'
        '<li><strong>Barking and Dagenham</strong>: selective licensing covering most privately rented homes. An EICR '
        'is one of the documents to upload.</li>'
        '<li><strong>Waltham Forest</strong> (Chingford): selective licensing in 20 of its 22 wards until 30 April '
        '2030. Endlebury, and Hatch Lane and Highams Park North, are left out.</li>'
        '<li><strong>Havering</strong> (Hornchurch, Upminster, Rainham): selective licensing in 7 wards, including '
        'Rainham and Wennington, until 17 March 2031.</li>'
        '</ul>',
        'Redbridge, Waltham Forest and Havering also license smaller HMOs across the whole borough, and Barking and '
        'Dagenham has additional HMO licensing too.',
        'Chigwell (IG7) is in Epping Forest District, which licenses larger HMOs and asks for an EICR with the '
        'application. Check your council\'s map before you let. ' + LANDLORD_RULES,
    ],
}


def join(items):
    return ', '.join(items[:-1]) + ' and ' + items[-1] if len(items) > 1 else items[0]


for slug, town, districts, example, nearby in TOWNS:
    pcs = join(districts)
    extra = (' For homes in East London we cover E4 and the IG and RM postcodes listed; other E postcodes '
             'are outside our area.' if slug == 'east-london' else '')
    local = ''.join(para if para.startswith('<ul') else f'<p>{para}</p>' for para in LOCAL[slug])
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
            'Choose a morning or afternoon slot, with free rescheduling up to 24 hours before.',
        ])
        + f'<h3 class="bo-local-h3">Renting out a home in {town}?</h3>' + local,
        areas=('We also cover', 'Chelmsford, Southend, Basildon, Colchester, Brentwood, Billericay, Harlow, Romford, '
               'Ilford and surrounding areas: postcodes <span data-coverage-areas>CM, SS, CO, RM, IG, E4, EN9, CB10 and CB11</span>.'),
        placeholder=example,
        own_canonical=True,
    ))

# Keyword pages (24 Nov 2026): one per search that used to land on /book-online, so the page Google checks for
# that keyword's landing page experience matches the search word for word (title, headline, intro, a section that
# answers it). 28 Nov 2026: these were ads-only (canonical to /book-online, not in the sitemap) and Google rated
# their landing page experience "Below average" while /eicr-certificate, the one with its own canonical, got
# "Average". So each now has its own canonical and is in the sitemap, like /eicr-certificate. Facts come from the FAQ on /book-online and /eicr-explained.
EXTRA = ('Most homes have <span data-cfg="pricing.EICR_DOM.included">8</span> circuits or fewer. If yours has more, '
         'it\'s <span data-price="EICR_DOM.extra">£15</span> + VAT per extra circuit. Parking or congestion charges '
         'are only added if we have to pay them.')
CODES = ('<b>C1</b> danger present, <b>C2</b> potentially dangerous, <b>C3</b> improvement recommended and '
         '<b>FI</b> further investigation')
HOW_OFTEN = ('Landlords need a new EICR at least every 5 years. For a home you live in, every 10 years is '
             'recommended, and whenever you buy or move in.')
AREAS = ('Areas we cover', 'Chelmsford, Southend, Basildon, Colchester, Brentwood, Billericay, Harlow, Romford, '
         'Ilford and surrounding areas: postcodes <span data-coverage-areas>CM, SS, CO, RM, IG, E4, EN9, CB10 and CB11</span>.')

TEST_EXTRA = section('bo-tests', 'The tests in an EICR, one by one', (
    '<p>An EICR is a visual inspection followed by a set of tests that BS 7671 sets out. Some are done with the power '
    'off ("dead" tests), and some with it on ("live" tests). Here\'s what each one checks, in plain English.</p>'
    '<dl class="bo-defs">'
    '<div><dt>Visual inspection</dt><dd>The fuse board, cables, sockets, switches and fittings are checked for damage, '
    'overheating, missing covers and anything not up to standard. A sample of accessories is opened up to check the '
    'connections inside.</dd></div>'
    '<div><dt>Continuity of protective conductors</dt><dd>Checks the earth wire runs unbroken from the fuse board to '
    'every point, so a fault would trip the circuit instead of making metalwork live. Recorded as R1 + R2.</dd></div>'
    '<div><dt>Ring final circuits</dt><dd>Most socket circuits are wired as a ring. Each leg of the ring is measured to '
    'make sure it\'s complete, with no breaks or wrong connections.</dd></div>'
    '<div><dt>Insulation resistance</dt><dd>A test voltage, usually 500 V, checks the insulation between the wires is '
    'sound, so current can\'t leak where it shouldn\'t.</dd></div>'
    '<div><dt>Polarity</dt><dd>Checks switches and fuses are on the live wire, not the neutral, so switching something '
    'off really makes it safe.</dd></div>'
    '<div><dt>Earth fault loop impedance</dt><dd>With the power on, measures how easily fault current can flow, to '
    'confirm each circuit breaker or fuse would disconnect a fault fast enough. Recorded as Zs, against the maximum '
    'allowed for that device.</dd></div>'
    '<div><dt>Prospective fault current</dt><dd>The largest current a fault could draw at the fuse board, to check the '
    'devices fitted can safely handle it.</dd></div>'
    '<div><dt>RCD tests</dt><dd>Each RCD is tripped on purpose to check it switches off fast enough to protect you '
    'from an electric shock, and its test button is checked too.</dd></div>'
    '</dl>'
    '<p>Every result goes into the schedule of test results in your report, circuit by circuit. '
    '<a href="/eicr-certificate#bo-sample">See a sample report</a>.</p>'
    '<h3>What can limit the inspection</h3>'
    '<p>Cables buried in walls, floors and ceilings can\'t be seen, and some areas, like a boarded-out loft or a '
    'fuse board behind fitted units, may be hard to reach. Anything that couldn\'t be checked is listed in the report '
    'as a limitation, so you know exactly what was covered.</p>'
))

TOWN_ROWS = ''.join(f'<li><a href="/eicr-{slug}">{town}</a><span>{", ".join(pcs)}</span></li>'
                    for slug, town, pcs, *_ in TOWNS)
NEAR_EXTRA = section('bo-local-how', 'How booking a local EICR works', (
    '<ol class="bo-steps">'
    '<li><strong>Enter your postcode.</strong> The booking page checks we cover it and shows the dates our '
    'electricians are free in your area.</li>'
    '<li><strong>Pick a morning or afternoon.</strong> Appointments are Monday to Friday, with an arrival window in '
    'the morning or the afternoon. You can reschedule free of charge up to 24 hours before.</li>'
    '<li><strong>Pay online.</strong> You see the full price, including VAT, before you pay. Parking or congestion '
    'charges are only added if we have to pay them.</li>'
    '<li><strong>We email when we\'re on the way.</strong> Your electrician\'s arrival time comes by email on the '
    'day.</li>'
    '</ol>'
    '<h3>Towns we cover</h3>'
    f'<ul class="bo-towns">{TOWN_ROWS}</ul>'
    '<p>Plus the rest of the CM, SS, CO, RM and IG postcodes, E4, EN9, CB10 and CB11. In East London we cover E4 and '
    'the IG and RM postcodes; other E postcodes aren\'t covered yet. Not sure? The booking page checks your '
    'postcode before you pay anything.</p>'
))

PRICE_ROWS = ''.join(f'<tr><th scope="row">{label}</th><td><span data-price="EICR_DOM.{key}">£{n}</span> + VAT</td>'
                     f'<td><span data-price="HOMEBUYER.{key}">£{h}</span> + VAT</td></tr>'
                     for key, label, n, h in [('studio', 'Studio flat', 79, 149), ('bed1', '1 bedroom', 90, 159),
                                              ('bed2', '2 bedrooms', 100, 169), ('bed3', '3 bedrooms', 110, 189),
                                              ('bed4', '4 bedrooms', 120, 209), ('bed5', '5 bedrooms', 130, 229),
                                              ('bed6', '6 bedrooms', 140, 249)])
PRICES_EXTRA = section('bo-price-how', 'How the price is worked out', (
    '<p>The price depends on two things: the size of the home and how many circuits its fuse board has. Each price '
    'covers one fuse board with up to <span data-cfg="pricing.EICR_DOM.included">8</span> circuits.</p>'
    '<div class="bo-table-wrap"><table class="bo-table"><caption>Prices by size of home</caption>'
    '<thead><tr><th scope="col">Home</th><th scope="col">EICR</th><th scope="col">Homebuyer\'s report</th></tr></thead>'
    f'<tbody>{PRICE_ROWS}</tbody></table></div>'
    '<p>Every circuit over <span data-cfg="pricing.EICR_DOM.included">8</span> is '
    '<span data-price="EICR_DOM.extra">£15</span> + VAT. For example, a 3-bedroom house with 10 circuits pays the '
    '3-bedroom price plus 2 extra circuits.</p>'
    '<h3>How to count your circuits</h3>'
    '<p>Open your fuse board and count the switches in the row (circuit breakers or fuses), leaving out the big main '
    'switch and any RCD switches marked with a "T" test button. Each one is usually a circuit: cooker, shower, '
    'sockets, lights and so on. Not sure? Book for your size of home: our electrician counts the circuits on the day, '
    'tells you about any extra, and it\'s added to your final bill, to be paid before your report is released.</p>'
    '<h3>What isn\'t in the price</h3>'
    + ticks([
        'Repairs. If anything needs putting right, we send a quote with photos, and nothing is done without your '
        'approval.',
        'Parking or congestion charges, only if we have to pay them.',
        'A second fuse board, such as one in a garage or outbuilding. If we find one, we tell you before we test it '
        'whether there\'s any extra charge.',
    ])
    + '<h3>Paying</h3>'
    '<p>You pay online when you book, and see the full price including VAT first. Your VAT invoice is saved in your '
    'online account with your report. <a href="/eicr-cost">More on what an EICR costs</a>.</p>'
))

REPORT_EXTRA = section('bo-when', 'When do you need an EICR?', (
    '<dl class="bo-defs">'
    '<div><dt>You rent out a home</dt><dd>The law in England says at least every 5 years, with copies for your tenants. '
    '<a href="/landlord-eicr">Landlord EICRs</a>.</dd></div>'
    '<div><dt>You\'re buying or selling</dt><dd>It shows the condition of the wiring before you commit, and gives you '
    'something to negotiate with. Our homebuyer\'s report adds a price for each repair.</dd></div>'
    '<div><dt>It\'s your own home</dt><dd>Every 10 years is recommended, and whenever you move in.</dd></div>'
    '<div><dt>Something\'s not right</dt><dd>Breakers tripping, flickering lights, scorch marks, a burning smell, or '
    'sockets that feel warm. Don\'t wait for the 10 years.</dd></div>'
    '<div><dt>After a flood or fire</dt><dd>Water and heat damage wiring you can\'t see.</dd></div>'
    '<div><dt>Someone asks for one</dt><dd>Mortgage lenders, insurers, letting agents and councils (for an HMO '
    'licence) often ask for a current EICR.</dd></div>'
    '</dl>'
    '<h3>Who can carry out an EICR?</h3>'
    '<p>It should be done by an electrician who is competent in inspection and testing, ideally one registered with a '
    'government-approved scheme such as NAPIT, so the work is checked and you have somewhere to go if anything is '
    'wrong. Our NAPIT and TrustMark registrations are linked above, so you can check them yourself.</p>'
    '<h3>EICR and other names for it</h3>'
    '<p>An EICR is also called an electrical safety certificate, a landlord electrical certificate, a periodic '
    'inspection report, or the older PIR. They all mean the same report. <a href="/eicr-certificate#bo-sample">See a '
    'sample</a>.</p>'
))

# 28 Nov 2026: more of each page's own, so /eicr-prices and the EICR report page stand on their own like /eicr-certificate.
PRICES_EXTRA += section('bo-price-faq', 'EICR cost questions', (
    '<dl class="bo-defs">'
    '<div><dt>Why do EICR prices vary so much?</dt><dd>An EICR takes longer the more circuits and rooms there are. A '
    'single price for every home means small flats pay for time they don\'t use, or big houses get rushed. We price by '
    'size and count the circuits on the day, so you pay for your home and nothing else.</dd></div>'
    '<div><dt>Is a cheaper EICR a worse one?</dt><dd>It can be. A proper EICR tests every circuit and records the '
    'readings, circuit by circuit. A "certificate" with no schedule of test results isn\'t a full EICR, and a letting '
    'agent or council may not accept it. Ours always includes the full test results.</dd></div>'
    '<div><dt>Is VAT included?</dt><dd>Prices on this page are + VAT. The booking page shows the full price including '
    'VAT before you pay, and your VAT invoice is saved in your online account.</dd></div>'
    '<div><dt>Do I pay anything on the day?</dt><dd>No. You pay when you book. The only extras are circuits over '
    '<span data-cfg="pricing.EICR_DOM.included">8</span>, which our electrician tells you about on the day, and any '
    'parking or congestion charges we have to pay.</dd></div>'
    '<div><dt>What if the report finds problems?</dt><dd>The EICR price stays the same whatever it finds. Repairs are '
    'quoted separately with photos, and you\'re free to use any qualified electrician for them.</dd></div>'
    '<div><dt>Do landlords pay the same?</dt><dd>Yes, the same prices by size of home. We can send the report to you, '
    'your letting agent and your tenants, and remind you before the next one is due.</dd></div>'
    '</dl>'
))

REPORT_EXTRA += section('bo-report-day', 'How long an EICR takes, and getting ready', (
    '<p>Most flats take a morning or an afternoon. A 3 or 4-bedroom house can take most of the day, depending on '
    'the number of circuits and how easy the fuse board and sockets are to reach.</p>'
    '<h3>Before we arrive</h3>'
    + ticks([
        'Clear the area around the fuse board, and make sure we can get into every room.',
        'Save any work on computers: the power goes off for short spells while circuits are tested.',
        'Tell us about anything that mustn\'t be switched off, such as medical equipment, a fish tank or a freezer '
        'full of food, so we can plan around it.',
        'If you\'re a landlord, let your tenants know, or arrange a key with your letting agent.',
    ])
    + '<h3>After the inspection</h3>'
    '<p>If we find anything dangerous, our electrician tells you before leaving and makes it safe with your agreement. '
    'The full report, on the IET model form, is emailed within 48 hours and saved in your online account.</p>'
    + shot('eicr-summary', 'Page 1 of a sample electrical installation condition report, showing the property, what '
           'was inspected and the overall result', 1000, 844,
           'Page 1 of a sample report: the property, what was inspected, and the overall result.')
    + '<p class="bo-sample-link"><a href="/assets/sample-eicr.pdf" target="_blank" rel="noopener">See the full 8-page '
      'sample (PDF)</a></p>'
), 'bo-sample-wrap')

pages.append(build(
    'eicr-test',
    'EICR test from £79 + VAT | Essex & East London | testmyelectrics.com',
    'Book an EICR test online from £79 + VAT. NAPIT-registered electricians inspect and test your wiring, fuse board, '
    'sockets and fittings across Essex and East London.',
    'EICR tests',
    'A full electrical inspection and test by NAPIT-registered electricians across Essex &amp; East London. '
    'Pick a slot and pay online.',
    'bo-test', 'What happens on the day',
    '<p>Our electrician inspects and tests your wiring, fuse board, sockets and fittings against the UK wiring '
    'regulations (BS 7671).</p>'
    + ticks([
        'How long it takes: a flat is usually a morning or an afternoon; a larger house can take most of the day.',
        'The power goes off for short spells while circuits are tested, so save any work and expect to reset clocks afterwards.',
        'We need to reach the fuse board, and the sockets and fittings in each room.',
        'Someone aged 18 or over needs to let us in, or you can arrange access with your tenant, your letting agent or a key safe.',
        'If we find a danger, we make it safe before we leave, with your agreement.',
        'Your report is emailed within 48 hours and saved in your online account.',
    ])
    + '<p>What the results mean: <a href="/eicr-explained">C1, C2, C3 and FI explained</a>.</p>',
    extra=TEST_EXTRA,
    own_canonical=True,
))

TOWN_LINKS = ', '.join(f'<a href="/eicr-{slug}">{town}</a>' for slug, town, *_ in TOWNS[:-1])
TOWN_LINKS += f' and <a href="/eicr-{TOWNS[-1][0]}">{TOWNS[-1][1]}</a>'
pages.append(build(
    'eicr-near-me',
    'EICR near me from £79 + VAT | Local electricians in Essex & East London',
    'Local EICRs from £79 + VAT. NAPIT-registered electricians across Chelmsford, Southend, Colchester, Basildon, '
    'Romford, Ilford and the rest of Essex and East London. Book online.',
    'EICRs near you',
    'Local NAPIT-registered electricians across Essex &amp; East London. Enter your postcode to see the next free dates.',
    'bo-near', 'Local electricians across Essex &amp; East London',
    '<p>We cover <span data-coverage-areas>CM, SS, CO, RM, IG, E4, EN9, CB10 and CB11</span> postcodes, including '
    f'{TOWN_LINKS}.</p>'
    + ticks([
        'The same fixed prices wherever you are: you see the full price before you pay.',
        'Choose a morning or afternoon slot, with free rescheduling up to 24 hours before.',
        'Your report is emailed within 48 hours and saved in your online account.',
    ]),
    areas=AREAS,
    extra=NEAR_EXTRA,
    own_canonical=True,
))

pages.append(build(
    'eicr-prices',
    'EICR cost from £79 + VAT | Fixed prices by property size | Essex & East London',
    'EICR prices from £79 + VAT, fixed by property size and shown in full before you pay. NAPIT-registered '
    'electricians across Essex and East London. Book online.',
    'EICR cost:',
    'Fixed prices by property size, shown in full before you pay. NAPIT-registered electricians across '
    'Essex &amp; East London.',
    'bo-cost', 'What\'s included in the price',
    ticks([
        'A full inspection and test of one fuse board with up to <span data-cfg="pricing.EICR_DOM.included">8</span> circuits.',
        'Your EICR certificate, emailed within 48 hours and saved in your online account.',
        'Free rescheduling up to 24 hours before your appointment.',
    ])
    + '<h3 class="bo-local-h3">What can add to the cost</h3>'
    + f'<p>{EXTRA} Any repairs are quoted separately, and nothing is done without your approval.</p>'
    + '<p>Prices for your home are below. More detail: <a href="/eicr-cost">how much an EICR costs</a>.</p>',
    extra=PRICES_EXTRA,
    own_canonical=True,
))

pages.append(build(
    'electrical-installation-condition-report',
    'Electrical installation condition report (EICR) from £79 + VAT | Essex & East London',
    'Book an electrical installation condition report (EICR) online from £79 + VAT. NAPIT-registered electricians '
    'across Essex and East London. Your report is emailed and saved in your online account.',
    'Electrical installation condition reports',
    'An EICR by NAPIT-registered electricians across Essex &amp; East London. Pick a slot and pay online.',
    'bo-eicr', 'What\'s in an electrical installation condition report?',
    '<p>An electrical installation condition report (EICR) comes from a full inspection and test of your wiring, '
    'fuse board, sockets and fittings against the UK wiring regulations (BS 7671).</p>'
    f'<p>It lists anything that needs attention, with a code for each: {CODES}. Any C1 or C2 makes the report '
    'Unsatisfactory; C3 and FI don\'t.</p>'
    f'<p>{HOW_OFTEN} <a href="/eicr-explained">The codes explained</a>.</p>',
    extra=REPORT_EXTRA,
    own_canonical=True,
))

pages.append(build(
    'eicr-certificate',
    'EICR certificate from £79 + VAT | Essex & East London | testmyelectrics.com',
    'Get your EICR certificate from £79 + VAT. NAPIT-registered electricians across Essex and East London. Emailed '
    'and saved in your online account, with the date your next one is due.',
    'EICR certificates',
    'Your EICR certificate from NAPIT-registered electricians across Essex &amp; East London, emailed and saved in '
    'your online account. Pick a slot and pay online.',
    'bo-cert', 'What you get',
    ticks([
        'Your EICR certificate (electrical installation condition report), emailed within 48 hours and saved in your online account.',
        'A clear result: Satisfactory, or Unsatisfactory, with each item coded C1, C2, C3 or FI.',
        'The date your next one is due, kept in your account.',
        'Landlords: a copy ready for your tenants (within 28 days) and for the council (within 7 days if they ask).',
    ])
    + f'<p>{HOW_OFTEN} <a href="/eicr-explained">What the codes mean</a>.</p>',
    extra=CERT_EXTRA,
))

# ---------------------------------------------------------------------------------------------------------------
# /homebuyer-electrical-report (25 Nov 2026, Wayne: every page an ad sends people to must let them book straight
# away). The Homebuyer's Report sitelink and price item land here. Same page as the others, but the booking box,
# headline price, price cards and buttons are for the homebuyer's report (service HOMEBUYER in the booking app).
# ---------------------------------------------------------------------------------------------------------------
HB_PRICE = '<span class="hl"><span data-price="HOMEBUYER.studio">£149</span>&nbsp;+&nbsp;VAT</span>'
HB_BANDS = [('studio', 'Studio', 149), ('bed1', '1 bedroom', 159), ('bed2', '2 bedrooms', 169), ('bed3', '3 bedrooms', 189),
            ('bed4', '4 bedrooms', 209), ('bed5', '5 bedrooms', 229), ('bed6', '6 bedrooms', 249)]
HB_PRICES = (
    '<h2 id="bo-prices">Homebuyer\'s report cost: from <span data-price="HOMEBUYER.studio">£149</span> + VAT</h2>\n'
    '        <div class="bo-price-grid">\n'
    '          <article class="price-card featured bo-eicr">\n'
    '            <span class="price-flag">Before you exchange</span>\n'
    '            <h3>Homebuyer\'s electrical report</h3>\n'
    '            <p class="price-for">A full EICR plus every repair priced. One fuse board, up to '
    '<span data-cfg="pricing.HOMEBUYER.included">8</span> circuits. All prices + VAT.</p>\n'
    '            <div class="tiers">\n'
    + ''.join(f'              <div><span>{label}</span><span class="mono" data-price="HOMEBUYER.{key}">£{n}</span></div>\n'
              for key, label, n in HB_BANDS)
    + '            </div>\n'
    '            <p class="bo-offer"><svg class="icon"><use href="#i-alarm"/></svg><span><strong>Free smoke, heat &amp; CO '
    'alarm check</strong> with every homebuyer\'s report: up to 6 mains-interlinked or battery alarms. Tick it when you '
    'book.</span></p>\n'
    '            <a class="btn btn-volt" href="/#book" data-book="HOMEBUYER" data-check-prices="HOMEBUYER">Check dates &amp; prices</a>\n'
    '          </article>\n'
    '          <article class="price-card bo-homebuyer" id="eicr-only">\n'
    '            <h3>Just need an EICR?</h3>\n'
    '            <p class="price-for">The same inspection and certificate, without the repair prices. A good choice if '
    'you\'re selling.</p>\n'
    '            <p class="price"><small>from</small><strong data-price="EICR_DOM.studio">£79</strong><small>+VAT</small></p>\n'
    '            <a class="btn btn-ghost" href="/#book" data-book="EICR_DOM" data-check-prices="EICR_DOM">Book an EICR</a>\n'
    '          </article>\n'
    '        </div>')


def homebuyer_page(p):
    # booking box: the homebuyer's report
    p = swap(p, '<form class="quick-book bo-book" data-quick-book data-require-postcode aria-label="Check dates and prices for an EICR">\n'
                '            <input type="hidden" name="service" value="EICR_DOM">',
             '<form class="quick-book bo-book" data-quick-book data-require-postcode aria-label="Check dates and prices for a homebuyer\'s report">\n'
             '            <input type="hidden" name="service" value="HOMEBUYER">')
    p = swap(p, 'Free smoke &amp; CO alarm check with every EICR</p>', 'Free smoke &amp; CO alarm check with every homebuyer\'s report</p>')
    # header button, phone menu and phone bar: without JavaScript they open the booking app at the homebuyer's report
    p = p.replace('data-book="EICR_DOM" data-check-prices=""', 'data-book="HOMEBUYER" data-check-prices=""')
    p = p.replace('<a class="btn btn-volt" href="/#book" data-book="EICR_DOM">Check dates &amp; prices</a>',
                  '<a class="btn btn-volt" href="/#book" data-book="HOMEBUYER">Check dates &amp; prices</a>')
    # price cards: the homebuyer's report first, the plain EICR second
    p = re.sub(r'<h2 id="bo-prices">.*?</h2>\s*<div class="bo-price-grid">.*?</article>\s*</div>', lambda m: HB_PRICES, p,
               count=1, flags=re.S)
    p = swap(p, 'A smoke, heat and CO alarm check is free with every EICR:', 'A smoke, heat and CO alarm check is free with every EICR or homebuyer\'s report:')
    return p


HB_EXTRA = section('bo-hb-how', 'Buying a home: how it works', (
    '<ol class="bo-steps">'
    '<li><strong>Book before you exchange contracts.</strong> You\'ll need the seller\'s agreement for the visit, usually '
    'arranged through the estate agent. Someone aged 18 or over needs to be there to let us in.</li>'
    '<li><strong>The inspection.</strong> A full EICR: our electrician inspects the fuse board, wiring, sockets, switches '
    'and fittings, and tests every circuit, the same as for a landlord or homeowner.</li>'
    '<li><strong>Your report.</strong> The EICR, with each item coded C1, C2, C3 or FI, plus a written report with a '
    'fixed price for each repair. It\'s emailed to you and saved in your online account.</li>'
    '<li><strong>Negotiate.</strong> Use the prices to agree a lower price with the seller, or to ask them to have the '
    'work done before completion.</li>'
    '<li><strong>Once it\'s yours.</strong> If you\'d like us to do the repairs, we book them in. Nothing is done '
    'without your approval, and you get a certificate for the work.</li>'
    '</ol>'
    '<h3>Why a survey isn\'t enough</h3>'
    '<p>A home survey looks at what can be seen, but it doesn\'t test the electrics. Under the RICS home survey '
    'standard, if there\'s no recent test, the surveyor should recommend one. A homebuyer\'s report gives you that '
    'test, and what any repairs will cost, before you commit.</p>'
    '<h3>What the codes mean</h3>' + CODES_DL
    + '<h3>Selling instead?</h3>'
    '<p>A recent EICR answers buyers\' and solicitors\' questions early, with no surprises later in the sale. '
    '<a href="/eicr-selling-a-house">Do you need an EICR to sell a house?</a></p>'
))

pages.append(build(
    'homebuyer-electrical-report',
    "Homebuyer's electrical report from £149 + VAT | Essex & East London",
    "A full EICR plus every repair priced, so you can negotiate before you exchange. From £149 + VAT across Essex "
    "and East London. NAPIT-registered electricians, book online.",
    "Homebuyer's electrical reports",
    'A full EICR with every repair priced, so you can negotiate before you exchange. NAPIT-registered electricians '
    'across Essex &amp; East London.',
    'bo-hb', 'What you get',
    ticks([
        'A full EICR: every circuit tested, with the same codes and report as a standard EICR.',
        'A written report with a fixed price for each repair, to show the seller or your solicitor.',
        'A free smoke, heat and CO alarm check: up to 6 mains-interlinked or battery alarms.',
        'Everything emailed to you and saved in your online account.',
    ]),
    extra=HB_EXTRA, price=HB_PRICE, post=homebuyer_page,
))

print('wrote', len(pages), 'pages:', ', '.join(pages))

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_common import inline_css  # noqa: E402
inline_css()
