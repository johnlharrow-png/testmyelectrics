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
          drop_homebuyer=False, own_canonical=True):
    p = SRC
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
# answers it). Ads-only: canonical to /book-online and not in the sitemap, so they don't compete in Google search
# with /book-online and the guides. Facts come from the FAQ on /book-online and /eicr-explained.
EXTRA = ('Most homes have <span data-cfg="pricing.EICR_DOM.included">8</span> circuits or fewer. If yours has more, '
         'it\'s <span data-price="EICR_DOM.extra">£15</span> + VAT per extra circuit. Parking or congestion charges '
         'are only added if we have to pay them.')
CODES = ('<b>C1</b> danger present, <b>C2</b> potentially dangerous, <b>C3</b> improvement recommended and '
         '<b>FI</b> further investigation')
HOW_OFTEN = ('Landlords need a new EICR at least every 5 years. For a home you live in, every 10 years is '
             'recommended, and whenever you buy or move in.')
AREAS = ('Areas we cover', 'Chelmsford, Southend, Basildon, Colchester, Brentwood, Billericay, Harlow, Romford, '
         'Ilford and surrounding areas: postcodes <span data-coverage-areas>CM, SS, CO, RM, IG, E4, EN9, CB10 and CB11</span>.')

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
    own_canonical=False,
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
    own_canonical=False,
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
    own_canonical=False,
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
    own_canonical=False,
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
    own_canonical=False,
))

print('wrote', len(pages), 'pages:', ', '.join(pages))

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_common import inline_css  # noqa: E402
inline_css()
