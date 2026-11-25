# Builds the guide pages that sit alongside /eicr-explained, from book-online.html's head, header and footer:
#   eicr-cost.html, landlord-electrical-safety.html, smoke-co-alarm-rules.html, eicr-selling-a-house.html
# Run after changing book-online.html or a price in assets/config.js:  python tools/build-guides.py
#
# Sources (checked 23 Nov 2026):
#   Electrical Safety Standards in the Private Rented Sector and Social Rented Sector (England) Regulations 2020,
#     https://www.legislation.gov.uk/uksi/2020/312 (penalty £40,000 since S.I. 2025/1043; FI wording removed
#     for inspections from 30 Nov 2026 by S.I. 2026/1196) and the gov.uk guidance for landlords.
#   Smoke and Carbon Monoxide Alarm (England) Regulations 2015 as amended by S.I. 2022/707,
#     https://www.legislation.gov.uk/uksi/2015/1693 and the gov.uk guidance booklet.
#   Alarm grades and categories: the field app's engineer guide (eicr-field-pro src/guide.js, BS 5839-6).
#   Prices: assets/config.js, which matches the booking app (GET /api/public/config).
from site_common import (inline_css, EMAIL, EICR_FROM, build_page, cfg, check, cta, faq_section, icon, more_guides, price,
                         pspan, rules)

ESS = 'https://www.legislation.gov.uk/uksi/2020/312/contents'
SMOKE = 'https://www.legislation.gov.uk/uksi/2015/1693/contents'
NOTE = 'Guide page, built by tools/build-guides.py from book-online.html.'
CIRCUITS = cfg('EICR_DOM.included')
EXTRA = f'{pspan("EICR_DOM.extra")} + VAT'


def hero(eyebrow, h1, lead, card, actions=None):
    actions = actions or f'<a class="btn btn-volt" href="/book-online"><span>Book an EICR from {EICR_FROM}</span></a>'
    return f'''    <section class="eg-hero" aria-labelledby="eg-title">
      <div class="container eg-hero-inner">
        <div>
          <p class="eyebrow">{eyebrow}</p>
          <h1 id="eg-title">{h1}</h1>
          <p class="eg-lead">{lead}</p>
          <div class="eg-actions">{actions}</div>
          <p class="eg-by">Written by the NAPIT-registered electricians at testmyelectrics.com.</p>
        </div>
{card}
      </div>
    </section>
'''


def card(label, side, rows, foot=None, cls=''):
    """The white summary card on the right of the hero (the .eg-report style from /eicr-explained)."""
    items = ''.join(f'<li><span>{a}</span><span class="eg-chip {c}">{b}</span></li>' for a, b, c in rows)
    foot = f'<p class="eg-result eg-result-ok">{foot}</p>' if foot else ''
    return f'''        <figure class="eg-report {cls}" aria-label="{label}">
          <div class="eg-report-head"><span>{label}</span><span>{side}</span></div>
          <ul>{items}</ul>
          {foot}
        </figure>'''


def section(sec_id, h2, body, intro='', alt=False):
    intro = f'\n        <p class="eg-intro">{intro}</p>' if intro else ''
    return f'''    <section class="bo-section{' eg-alt' if alt else ''}" aria-labelledby="{sec_id}">
      <div class="container">
        <h2 id="{sec_id}">{h2}</h2>{intro}
        {body}
      </div>
    </section>
'''


def checks(*items):
    return '<ul class="eg-checks">' + ''.join(check(*i) for i in items) + '</ul>'


def more(href, text):
    return f'<p class="eg-more"><a href="{href}">{text}</a> {icon("arrow")}</p>'


def main(*parts):
    return '  <main id="main">\n' + '\n'.join(parts) + '  </main>\n'


def tick(text):
    return f'<li class="eg-myth"><span class="tick">{icon("check")}</span><div>{text}</div></li>'


def cross(text):
    return f'<li class="eg-myth eg-no"><span class="eg-x">{icon("alert")}</span><div>{text}</div></li>'


pages = []

# ------------------------------------------------------------------------------------------------
# /eicr-cost
# ------------------------------------------------------------------------------------------------
COST_FAQ = [
    ('How much does an EICR cost?',
     f'Our domestic EICR is from {price("EICR_DOM.studio")} + VAT for a studio flat, and '
     f'{price("EICR_DOM.bed6")} + VAT for a six-bedroom home. Every price includes up to 8 circuits and one '
     f'consumer unit. You see the full price for your property before you pay.'),
    ('Are your prices with or without VAT?',
     'Our website shows prices without VAT. VAT is added at 20%, and the booking page shows the full price, '
     'including VAT, before you pay.'),
    ('How do I know how many circuits I have?',
     'Each circuit has its own fuse or circuit breaker in your fuse board, so counting them gives you a rough idea. '
     'Most homes have 8 or fewer. You do not need to count them before you book: our electrician counts them '
     'on the day.'),
    ('What if you find more circuits than I booked?',
     f'Each circuit over 8 is {price("EICR_DOM.extra")} + VAT. We tell you, and the extra goes on a final bill in your '
     'online account. Your certificate is issued once that bill is paid.'),
    ('Is the cost of repairs included?',
     'No. If something needs fixing, we explain it in plain English and send you a fixed quote for the work. '
     'Nothing is done without your OK. The exception is a C1 (danger present): with your agreement we make it '
     'safe before we leave, usually by switching off that circuit.'),
    ('Can I change my appointment?',
     'Yes, free of charge, up to 24 hours before your appointment, through your online account or by email.'),
]

pages.append(build_page(
    'eicr-cost',
    f'How much does an EICR cost? From {price("EICR_DOM.studio")} + VAT | testmyelectrics.com',
    f'EICR prices from {price("EICR_DOM.studio")} + VAT: what is included, what changes the price, what extras cost '
    'and what happens if your report is Unsatisfactory. Essex and East London.',
    main(
        hero('EICR prices',
             'How much does an EICR cost?',
             f'Our domestic EICR costs from {EICR_FROM}. The price depends on the size of your home and includes up to '
             f'{CIRCUITS} circuits and one consumer unit (fuse board). You see the full price before you pay.',
             card('Domestic EICR', 'All + VAT', [
                 ('Studio', pspan('EICR_DOM.studio'), 'eg-price'),
                 ('1 bedroom', pspan('EICR_DOM.bed1'), 'eg-price'),
                 ('2 bedrooms', pspan('EICR_DOM.bed2'), 'eg-price'),
                 ('3 bedrooms', pspan('EICR_DOM.bed3'), 'eg-price'),
                 ('4 bedrooms', pspan('EICR_DOM.bed4'), 'eg-price'),
                 ('5 bedrooms', pspan('EICR_DOM.bed5'), 'eg-price'),
                 ('6 bedrooms', pspan('EICR_DOM.bed6'), 'eg-price'),
             ], f'<span>Up to {CIRCUITS} circuits included</span><span>{EXTRA} each extra</span>')),
        section('eg-inc', 'What the price includes', checks(
            ('check', 'A full inspection and test', 'Your wiring, fuse board, sockets, switches and lights, checked against the UK wiring regulations (BS 7671).'),
            ('bolt', f'Up to {CIRCUITS} circuits', 'Most homes have 8 or fewer. Our electrician counts them on the day.'),
            ('home', 'One consumer unit', 'The fuse board, with its circuit breakers and RCDs. Online prices are for one board in one property.'),
            ('file', 'Your report', 'Emailed within 48 hours once your booking is paid in full, and saved in your online account.'),
            ('shield', 'Plain-English results', 'Any problem is coded C1, C2, C3 or FI, and we explain what each one means for you.'),
            ('calendar', 'A slot that suits you', 'Choose a morning or afternoon. Rescheduling is free up to 24 hours before.'),
        ), 'One fixed price for the size of your home, shown before you pay.'),
        section('eg-change', 'What changes the price', rules([
            '<strong>The size of your home.</strong> Prices go up with the number of bedrooms, from a studio to six bedrooms.',
            f'<strong>The number of circuits.</strong> Up to {CIRCUITS} are included. Each extra circuit is {EXTRA}, counted by our electrician on the day.',
            '<strong>More than one consumer unit.</strong> Some homes have a second board, for example for an annexe or a garage. '
            'We price these for you. If we find a second board when we arrive, we tell you before we test it whether there is any extra charge.',
            '<strong>Parking and congestion charges.</strong> Only added if we have to pay them to reach you, at cost.',
        ]) + f'<p class="eg-note">Any extras go on a final bill in your online account. Your certificate is issued once it is paid. '
             f'Several properties or more than one board? Email {EMAIL} for a price.</p>', alt=True),
        section('eg-extras', 'Extras you can add', f'''<ul class="eg-prices">
          <li><span class="eg-ic">{icon('plug')}</span><h3>PAT testing</h3><p class="eg-p"><strong>{pspan('PAT.upTo10')}</strong> + VAT</p><p>Up to 10 portable appliances, then {pspan('PAT.extra')} + VAT per extra item.</p></li>
          <li><span class="eg-ic">{icon('alarm')}</span><h3>Smoke, heat &amp; CO alarm check</h3><p class="eg-p"><strong>Free</strong> with an EICR</p><p>Up to {cfg('FIRE.included')} mains-interlinked or battery alarms, then {pspan('FIRE.extra')} + VAT per extra alarm. <a href="/smoke-co-alarm-rules">The alarm rules</a>.</p></li>
          <li><span class="eg-ic">{icon('key')}</span><h3>Homebuyer's electrical report</h3><p class="eg-p"><small>from</small> <strong>{pspan('HOMEBUYER.studio')}</strong> + VAT</p><p>A full EICR plus a written report with repairs priced, instead of a standard EICR. <a href="/eicr-selling-a-house">For buyers and sellers</a>.</p></li>
        </ul>''', 'PAT testing and the alarm check are add-ons: book them with an EICR or a homebuyer\'s report. The alarm check is free with either.'),
        section('eg-after', 'If your report is Unsatisfactory', rules([
            'A report is Unsatisfactory if it has at least one C1 (danger present) or C2 (potentially dangerous). C3s are recommendations and don\'t fail it.',
            'For a C1, we make it safe before we leave, with your agreement, usually by switching off that circuit. You get a written danger notice the same day.',
            'We explain each item in plain English and send a fixed quote for the work. Nothing is done without your OK.',
            'Once the work is done, you get a certificate for it. Keep it with the report to show the problems have been put right.',
            'Landlords have 28 days to have the work done, or less if the report says so. <a href="/landlord-electrical-safety">The rules for landlords</a>.',
        ]) + more('/eicr-explained#codes', 'What C1, C2, C3 and FI mean'), alt=True),
        faq_section(COST_FAQ, 'EICR cost questions'),
        more_guides('eicr-cost'),
        cta('Get your exact price', f'Pop in your postcode and the size of your home to see dates and the full price. From {EICR_FROM}, '
            'NAPIT-registered electricians across Essex and East London.'),
    ),
    COST_FAQ, NOTE))

# ------------------------------------------------------------------------------------------------
# /landlord-electrical-safety
# ------------------------------------------------------------------------------------------------
LL_FAQ = [
    ('How often does a rented home need an EICR?',
     'At least every 5 years in England, or sooner if the last report says so. A new tenancy can start on the '
     'current report, as long as it is less than 5 years old and its next inspection date has not passed.'),
    ('Do C3 items have to be fixed?',
     'No. The government guidance says a C3 means an improvement is recommended, not that remedial work is required. '
     'Only C1 and C2 items make a report Unsatisfactory.'),
    ('What if my tenant will not let the electrician in?',
     'You are not in breach if you can show you took all reasonable steps to get the inspection done. Keep a record '
     'of your letters, emails and the dates you offered.'),
    ('Do the rules cover lodgers?',
     'No. Lodgers who share a kitchen, bathroom, toilet or living room with you or your family are excluded. So are '
     'leases of 7 years or more, student halls, hostels, refuges and care homes.'),
    ('Do I need a PAT test as well?',
     'These regulations cover the fixed wiring, not appliances. It is still sensible to have the appliances you '
     'supply PAT tested, and some councils ask for a PAT certificate when you apply for an HMO licence.'),
    ('How much can the council fine me?',
     'Up to £40,000 for breaching these regulations. The council can also serve a remedial notice giving you 28 days '
     'to put things right.'),
]

pages.append(build_page(
    'landlord-electrical-safety',
    'Landlord electrical safety rules in England: EICR every 5 years | testmyelectrics.com',
    'What the Electrical Safety Standards Regulations 2020 ask of landlords in England: an EICR every 5 years, copies '
    'for tenants and the council, repairs within 28 days, HMOs and fines. Plain English.',
    main(
        hero('Landlord guide',
             'Landlord electrical safety: the rules in England',
             'If you rent out a home in England, the law says its wiring must be inspected and tested at least every '
             '5 years. Here is what the Electrical Safety Standards Regulations 2020 ask of you, in plain English.',
             card('Landlord checklist', 'England', [
                 ('EICR at least every', '5 years', 'eg-c3'),
                 ('Copy to tenants within', '28 days', 'eg-c3'),
                 ('Copy to the council if asked', '7 days', 'eg-c3'),
                 ('Repairs done within', '28 days', 'eg-c2'),
                 ('Maximum fine', '£40,000', 'eg-c1'),
             ]),
             f'<a class="btn btn-volt" href="/landlord-eicr"><span>Book a landlord EICR from {EICR_FROM}</span></a>'),
        section('eg-duties', 'Your duties as a landlord', rules([
            'Keep the electrical installation up to the standards in the wiring regulations (BS 7671) for as long as the home is let.',
            'Have it inspected and tested by a qualified person at least every 5 years, or sooner if the last report says so.',
            'Give each existing tenant a copy of the report within 28 days of the inspection.',
            'Give a new tenant a copy before they move in, and a prospective tenant a copy within 28 days if they ask in writing.',
            'Send the council a copy within 7 days if it asks in writing.',
            'Keep a copy until the next inspection, and give one to the electrician who does it.',
            'If the report says work is needed, have it done by a qualified person within 28 days, or sooner if the report says so.',
            'Get written confirmation that the work is done. Send it, with the report, to your tenants and the council within 28 days.',
        ]), 'Under the Electrical Safety Standards in the Private Rented Sector and Social Rented Sector (England) Regulations 2020.'),
        section('eg-fix', 'What has to be put right', f'''<div class="eg-results">
          <div class="eg-res fail"><h3><span class="eg-x">{icon('alert')}</span>C1 and C2</h3><p>Danger present, or potentially dangerous. These make the report Unsatisfactory, and you must have them put right within 28 days, or sooner if the report says so.</p></div>
          <div class="eg-res pass"><h3><span class="tick">{icon('check')}</span>C3</h3><p>Improvement recommended. The government guidance says a C3 doesn't need remedial work. It's worth planning for, but the report can still be Satisfactory.</p></div>
        </div>
        <p class="eg-lim"><b>FI (further investigation).</b> For inspections done before 30 November 2026, landlords must also have any FI item investigated within 28 days. An amendment to the regulations takes out the wording about further investigation for inspections from 30 November 2026.</p>''' + more('/eicr-explained#codes', 'C1, C2, C3 and FI explained'), alt=True),
        section('eg-hmo', 'HMOs and licensed properties', checks(
            ('users', 'HMOs are covered', 'The rules apply to homes shared by people from more than one household, such as house shares and bedsits.'),
            ('file', 'HMO licences', 'An HMO with 5 or more people from 2 or more households needs a licence from the council. Most councils we checked ask for a current EICR with the application.'),
            ('building', 'Selective licensing', 'Some councils also license ordinary rented homes in certain areas. Check with your council: our town pages say what we found for each area.'),
        ), 'If you let a house in multiple occupation, the same EICR rules apply, and your licence may add its own conditions.'),
        section('eg-enforce', 'If the rules aren\'t followed', rules([
            'The council can serve a remedial notice, giving you 28 days to do the work.',
            'It can fine you up to £40,000.',
            'You are not in breach if you can show you took all reasonable steps, for example if a tenant keeps refusing access. Keep a record of what you tried.',
        ]), alt=True),
        section('eg-nations', 'Wales and Scotland', '''<div class="eg-results">
          <div class="eg-res eg-plain"><h3>Wales</h3><p>Landlords must have a valid electrical condition report, renewed at least every 5 years, and give a copy to the contract-holder. This comes from the Renting Homes (Fitness for Human Habitation) (Wales) Regulations 2022.</p></div>
          <div class="eg-res eg-plain"><h3>Scotland</h3><p>The Repairing Standard asks for an EICR at least every 5 years, with a copy for new tenants before the tenancy starts. Scotland also has its own alarm rules.</p></div>
        </div>
        <p class="eg-note">We work in Essex and East London, so this guide is about the rules in England.</p>'''),
        faq_section(LL_FAQ, 'Landlord questions'),
        more_guides('landlord-electrical-safety'),
        cta('Book your landlord EICR', f'From {EICR_FROM}. Add your tenant\'s details and we arrange access with them or your letting agent. '
            'Your report is saved in your online account, ready to send to tenants and the council.',
            f'Source: <a href="{ESS}" rel="noopener">The Electrical Safety Standards Regulations 2020 on legislation.gov.uk</a>.'),
    ),
    LL_FAQ, NOTE))

# ------------------------------------------------------------------------------------------------
# /smoke-co-alarm-rules
# ------------------------------------------------------------------------------------------------
SMOKE_FAQ = [
    ('Do I need a CO alarm for a gas cooker?',
     'No. Gas cookers are the one fixed combustion appliance the rules leave out. You do need one in any room used as '
     'living accommodation with a boiler, gas fire, wood burner or other fixed appliance that burns fuel.'),
    ('Can I fit battery smoke alarms?',
     'Yes. The rules in England don\'t say what type of alarm to fit. The government guidance prefers alarms with '
     'sealed-for-life batteries to ones with replaceable batteries. Many landlords choose mains-powered alarms with a '
     'sealed standby battery.'),
    ('Do the alarms have to be interlinked?',
     'Not in England, though BS 5839-6 recommends it, so that every alarm sounds when one goes off. Wales and Scotland '
     'have their own alarm rules.'),
    ('Do I need a heat alarm in the kitchen?',
     'Not by law in England. A heat alarm in the kitchen is part of the higher LD2 level of protection in BS 5839-6, '
     'which we recommend for rented homes.'),
    ('Who tests the alarms during the tenancy?',
     'The rules only say you must check them on the first day of a new tenancy. After that, show your tenants how to '
     'test them and ask them to tell you about any fault. You must then repair or replace the alarm.'),
    ('Do the rules apply to social housing?',
     'Yes. Since 1 October 2022 they apply to homes let by private landlords and by social housing providers, unless '
     'the tenancy is excluded.'),
]

pages.append(build_page(
    'smoke-co-alarm-rules',
    'Smoke and carbon monoxide alarm rules for landlords in England | testmyelectrics.com',
    'The smoke and CO alarm rules for landlords in England since October 2022: an alarm on every storey, CO alarms by '
    'fixed combustion appliances, checks on the first day of a tenancy and repairs.',
    main(
        f'''    <section class="eg-hero" aria-labelledby="eg-title">
      <div class="container eg-hero-inner">
        <div>
          <p class="eyebrow">Landlord guide</p>
          <h1 id="eg-title">Smoke and carbon monoxide alarm rules for landlords</h1>
          <p class="eg-lead">Since 1 October 2022, landlords in England must have a smoke alarm on every storey of a rented home, and a carbon monoxide (CO) alarm in any room with a fixed combustion appliance. Here is what that means in practice.</p>
          <div class="eg-actions"><a class="btn btn-volt" href="/book-online">Add an alarm check to your EICR</a></div>
          <p class="eg-by">Written by the NAPIT-registered electricians at testmyelectrics.com.</p>
        </div>
        <figure class="eg-art"><img src="/assets/img/guide/alarms-house.svg" alt="A two-storey house with a smoke alarm on each storey and a CO alarm next to the boiler and the wood burner" width="360" height="330" decoding="async"></figure>
      </div>
    </section>
''',
        section('eg-rules4', 'The four rules', rules([
            '<strong>A smoke alarm on every storey</strong> that has a room used as living accommodation. Bathrooms and toilets count, and so do halls and landings.',
            '<strong>A CO alarm in every room with a fixed combustion appliance</strong>, if the room is used as living accommodation. Gas cookers are left out.',
            '<strong>Check every alarm works on the day a new tenancy starts.</strong> Keep a record, for example by having the tenant sign the inventory.',
            '<strong>Repair or replace any alarm you are told is faulty</strong>, as soon as reasonably practicable.',
        ]), 'Under the Smoke and Carbon Monoxide Alarm (England) Regulations 2015, as changed by the Smoke and Carbon Monoxide Alarm (Amendment) Regulations 2022.'),
        section('eg-appl', 'Which appliances need a CO alarm?', f'''<ul class="eg-myths">
          {tick('<h3>Gas or oil boiler</h3><p>Any fixed appliance that burns fuel to make heat counts.</p>')}
          {tick('<h3>Wood or log burner</h3><p>Wood, coal and other solid fuel stoves count too.</p>')}
          {tick('<h3>Gas fire</h3><p>A fixed gas fire burns fuel to heat the room, so it needs one.</p>')}
          {cross('<h3>Gas cooker</h3><p>Gas cookers are the one exception. So is a decorative fireplace that isn\'t used.</p>')}
        </ul>''', 'The guidance suggests fitting CO alarms at head height, on a wall or shelf, about 1 to 3 metres from the appliance, and following the maker\'s instructions.', alt=True),
        section('eg-types', 'Which alarms to fit', checks(
            ('bolt', 'Grade D1', 'Mains powered, with a sealed standby battery. The usual choice for rented homes.'),
            ('bolt', 'Grade D2', 'Mains powered, with a standby battery you can replace.'),
            ('alarm', 'Battery alarms', 'Allowed in England. The guidance prefers sealed-for-life batteries to replaceable ones.'),
            ('home', 'LD3 cover', 'Smoke alarms in the hall and on each landing. The minimum for most existing homes.'),
            ('shield', 'LD2 cover', 'LD3 plus the main living room, and a heat alarm in the kitchen. What we recommend for rented homes.'),
            ('calendar', 'Replace at 10 years', 'Alarms wear out. Check the replace-by date printed on each one.'),
        ), 'The law in England doesn\'t say which type to fit. These grades and levels come from the British Standard for alarms in homes, BS 5839-6.'),
        section('eg-check', 'Our alarm check', rules([
            'We press-test every alarm and check the others sound with it, if they are interlinked.',
            'We check the replace-by date on each alarm.',
            'We check mains-powered alarms are switched on and showing their power light.',
            'We check each alarm is in a sensible place, for example not too close to a wall or light, and no smoke alarms in kitchens or bathrooms.',
        ]) + f'<p class="eg-note">Free with every EICR or homebuyer\'s report for up to {cfg("FIRE.included")} mains-interlinked or battery alarms, then {pspan("FIRE.extra")} + VAT per extra alarm. '
             'It doesn\'t cover fire alarm systems with a control panel. Booked with your EICR, so it is done on the same visit. Anything that fails is on your report with a quote to fix it.</p>', alt=True),
        section('eg-fine', 'If the rules aren\'t followed', rules([
            'The council can serve a remedial notice, giving you 28 days to fit, repair or replace the alarms.',
            'If you don\'t, it can charge a penalty of up to £5,000.',
            'Licensed HMOs follow the same kind of rules through their licence conditions instead.',
        ])),
        faq_section(SMOKE_FAQ, 'Alarm questions'),
        more_guides('smoke-co-alarm-rules'),
        cta('Book an EICR with an alarm check', f'EICR from {EICR_FROM}, with a free smoke, heat and CO alarm check on the same visit. '
            'NAPIT-registered electricians across Essex and East London.',
            f'Source: <a href="{SMOKE}" rel="noopener">The Smoke and Carbon Monoxide Alarm (England) Regulations 2015 on legislation.gov.uk</a>.'),
    ),
    SMOKE_FAQ, NOTE))

# ------------------------------------------------------------------------------------------------
# /eicr-selling-a-house
# ------------------------------------------------------------------------------------------------
SELL_FAQ = [
    ('Is an EICR a legal requirement when selling a house?',
     'Not for a home you live in. The EICR rules in England are for landlords. Buyers, surveyors and solicitors '
     'often ask about the electrics, though, so a recent report can help.'),
    ('How old can the report be?',
     'There is no fixed rule for a sale. For a home you live in, a test every 10 years is recommended, and when a new '
     'owner moves in. A buyer will usually be happier with a recent report.'),
    ('Can a buyer book the EICR?',
     'Yes. You will need the seller\'s agreement for the visit, usually arranged through the estate agent. Someone aged '
     '18 or over must be there to let us in.'),
    ('What is the difference between an EICR and a homebuyer\'s report?',
     f'A homebuyer\'s electrical report is a full EICR plus a written report with the repairs priced, to help you '
     f'negotiate. It costs from {price("HOMEBUYER.studio")} + VAT. An EICR on its own is from '
     f'{price("EICR_DOM.studio")} + VAT.'),
    ('Does an Unsatisfactory report stop a sale?',
     'No. It means at least one C1 or C2 needs putting right. You can have the work done before you sell, or share the '
     'report and our quote with the buyer so it can be agreed between you.'),
]

pages.append(build_page(
    'eicr-selling-a-house',
    'Do you need an EICR to sell a house? | testmyelectrics.com',
    'An EICR is not a legal requirement to sell a home you live in, but buyers, surveyors and solicitors often ask. '
    'What to do if it is Unsatisfactory, and our homebuyer\'s electrical report.',
    main(
        hero('Buying and selling',
             'Do you need an EICR to sell a house?',
             'No law says you need one to sell a home you live in. But buyers, surveyors and solicitors often ask about '
             'the electrics, and a recent report means fewer questions and no surprises later in the sale.',
             card('Selling or buying?', 'England', [
                 ('Legal to sell without one', 'Yes', 'ok'),
                 ('Home with tenants in', 'Needs one', 'eg-c2'),
                 ('Buyers and surveyors', 'Often ask', 'eg-c3'),
                 ('Homebuyer\'s report', f'from {pspan("HOMEBUYER.studio")}', 'eg-c3'),
             ]),
             f'<a class="btn btn-volt" href="/book-online"><span>Book an EICR from {EICR_FROM}</span></a>'
             f'<a class="btn btn-ghost-light" href="#buying">Buying a home?</a>'),
        section('eg-sell', 'Selling: why have one done first', checks(
            ('file', 'Answer questions early', 'Buyers\' solicitors ask what you know about the electrics and any work done. A recent report answers that.'),
            ('alert', 'No late surprises', 'Find any problems on your own terms, with a fixed quote, before a buyer\'s survey does.'),
            ('key', 'Keep your certificates', 'Electrical work done since 2005, such as a rewire or a new fuse board, should have a certificate. Find them now.'),
        ), 'An EICR is a full inspection and test of the wiring, fuse board, sockets and lights. <a href="/eicr-explained">What an EICR checks</a>.'),
        section('eg-survey', 'What surveyors and solicitors look for', rules([
            'A survey looks at what can be seen, but it doesn\'t test the electrics.',
            'Under the RICS home survey standard, if there\'s no recent test of the electrics, the surveyor should recommend one.',
            'Buyers\' solicitors often ask about electrical work done on the property, and for any certificates.',
        ]), alt=True),
        section('buying', 'Buying: our homebuyer\'s electrical report', f'''<ul class="eg-prices">
          <li><span class="eg-ic">{icon('check')}</span><h3>A full EICR</h3><p>Every circuit tested, with the same codes and report as a standard EICR.</p></li>
          <li><span class="eg-ic">{icon('file')}</span><h3>Repairs priced</h3><p>A written report with a price for each repair, so you can negotiate with the seller.</p></li>
          <li><span class="eg-ic">{icon('key')}</span><h3>From {pspan('HOMEBUYER.studio')} + VAT</h3><p>Priced by the size of the home, including up to {cfg('HOMEBUYER.included')} circuits and one fuse board.</p></li>
        </ul>
        <p class="eg-note">You'll need the seller's agreement for the visit, usually arranged through the estate agent.</p>''',
                'Before you exchange contracts, find out what the electrics need and what it will cost.'),
        section('eg-unsat', 'If the report is Unsatisfactory', rules([
            'It means at least one C1 (danger present) or C2 (potentially dangerous). C3s are recommendations and don\'t fail the report.',
            'A C1 is made safe before we leave, with your agreement.',
            'We explain each item in plain English and send a fixed quote. Nothing is done without your OK.',
            'You can have the work done before you sell and pass on the certificate, or share the report and our quote with the buyer and agree it between you.',
        ]) + more('/eicr-explained#codes', 'What the codes mean'), alt=True),
        section('eg-let', 'Selling a home with tenants in it', '<p class="eg-note eg-note-big">While a home is let, the landlord rules still apply: '
                'an EICR at least every 5 years, with copies for the tenants. If you are buying a home with tenants who are staying, '
                'ask for the current report. <a href="/landlord-electrical-safety">The rules for landlords</a>.</p>'),
        faq_section(SELL_FAQ, 'Buying and selling questions'),
        more_guides('eicr-selling-a-house'),
        cta('Book an EICR or homebuyer\'s report', f'EICR from {EICR_FROM}, homebuyer\'s report from {pspan("HOMEBUYER.studio")} + VAT. '
            'NAPIT-registered electricians across Essex and East London.'),
    ),
    SELL_FAQ, NOTE))

print('wrote', len(pages), 'pages:', ', '.join(pages))
inline_css()
