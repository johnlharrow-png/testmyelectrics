# Builds eicr-explained.html, the "What is an EICR? Codes explained" guide, from book-online.html's
# head, header and footer, so it shares the same fonts, scripts, cookie banner and tracking.
# Run after changing book-online.html:  python tools/build-eicr-guide.py
#
# The wording is our own, taken from the field app's engineer coding guide (eicr-field-pro src/guide.js
# and src/seed/library.js), which follows BS 7671 and Electrical Safety First's Best Practice Guide 4.
# Pictures marked esf-* come from Best Practice Guide 4 (issue 6, 2022) and carry a credit line.
import html

from site_common import build_page, check, cta, faq_section, icon, more_guides, EICR_FROM as PRICE

ESF = 'https://www.electricalsafetyfirst.org.uk/resources-for-electricians/best-practice-guides/'
CREDIT = f'<span class="eg-credit">Picture: <a href="{ESF}" rel="noopener">Electrical Safety First, Best Practice Guide 4</a></span>'


FAQ = [
    ('How long does an EICR take?',
     'It depends on the size of the property and how many circuits it has. A flat is usually a morning or an '
     'afternoon; a larger house can take most of the day. The power goes off for short spells while circuits are '
     'tested, so save any work and expect to reset clocks afterwards.'),
    ('How often do I need one?',
     'Landlords in England need one at least every 5 years, or sooner if the last report says so. For a home you '
     'live in, every 10 years is recommended, and whenever you buy or move into a property.'),
    ('What happens if my report is Unsatisfactory?',
     'We explain each C1 and C2 in plain English and send a fixed quote for the work. Nothing is done without your '
     'OK. Once it is done you get a certificate for the work, which goes with the report to show the installation '
     'is safe.'),
    ('Do C3 recommendations have to be done?',
     'No. A C3 means part of the installation does not meet the current edition of the wiring regulations but is '
     'not dangerous. It does not make the report Unsatisfactory. It is worth planning for, for example when you '
     'next have electrical work done.'),
    ('How much does an EICR cost?',
     'From £79 + VAT for a studio flat, including up to 8 circuits and 1 consumer unit. You see the full price for '
     'your property before you pay. Extra circuits are £15 + VAT each.'),
]


def code_card(cls, code, name, art, art_alt, summary, examples, next_step, credit=''):
    items = ''.join(f'<li>{e}</li>' for e in examples)
    round_ = ' class="eg-round"' if art.endswith('.webp') else ''  # the guide's photo is a circle on white
    return f'''        <article class="eg-code {cls}" id="{code.lower()}">
          <figure class="eg-code-art"><img{round_} src="{art}" alt="{html.escape(art_alt)}" width="320" height="220" loading="lazy" decoding="async">{credit}</figure>
          <div class="eg-code-body">
            <h3 class="eg-code-tag"><b>{code}</b><span>{name}</span></h3>
            <p class="eg-code-sum">{summary}</p>
            <ul>{items}</ul>
            <p class="eg-next"><strong>What happens next:</strong> {next_step}</p>
          </div>
        </article>'''


CTA = cta('Book your EICR online',
          f'From {PRICE}. NAPIT-registered electricians across Essex and East London. Your certificate is emailed '
          'and saved in your online account.',
          f'Codes follow BS 7671 and Electrical Safety First\'s free <a href="{ESF}" rel="noopener">Best Practice Guide 4</a>.')

MAIN = f'''  <main id="main">
    <section class="eg-hero" aria-labelledby="eg-title">
      <div class="container eg-hero-inner">
        <div>
          <p class="eyebrow">EICR guide</p>
          <h1 id="eg-title">What is an EICR? The codes C1, C2, C3 and FI explained</h1>
          <p class="eg-lead">An EICR (Electrical Installation Condition Report) is a full inspection and test of a property's wiring, fuse board, sockets and fittings. The electrician checks everything against the UK wiring regulations (BS 7671) and gives anything that isn't right a code that shows how serious it is.</p>
          <div class="eg-actions">
            <a class="btn btn-volt" href="/book-online">Book an EICR from {PRICE}</a>
            <a class="btn btn-ghost-light" href="#codes">See what the codes mean</a>
          </div>
          <p class="eg-by">Written by the NAPIT-registered electricians at testmyelectrics.com.</p>
        </div>
        <figure class="eg-report" aria-label="Example EICR summary">
          <div class="eg-report-head"><span>Example report</span><span>3-bed house</span></div>
          <ul>
            <li><span>Fuse board and RCDs</span><span class="eg-chip ok">OK</span></li>
            <li><span>Earthing and bonding</span><span class="eg-chip eg-c2">C2</span></li>
            <li><span>Wiring and insulation tests</span><span class="eg-chip ok">OK</span></li>
            <li><span>Sockets, switches and lights</span><span class="eg-chip eg-c3">C3</span></li>
          </ul>
          <p class="eg-result"><span>Result: Unsatisfactory</span><span>1 C2 to put right</span></p>
        </figure>
      </div>
    </section>

    <section class="bo-section" aria-labelledby="eg-checks">
      <div class="container">
        <h2 id="eg-checks">What an EICR checks</h2>
        <p class="eg-intro">The electrician looks over the whole fixed installation, then tests every circuit with calibrated instruments.</p>
        <ul class="eg-checks">
          {check('bolt', 'The fuse board', 'Its condition, the circuit breakers and RCDs, and whether each circuit is labelled.')}
          {check('shield', 'Earthing and bonding', 'The main earth, and the earth connections to your gas and water pipes.')}
          {check('plug', 'Sockets, switches and lights', 'A sample is opened up to check the connections, polarity and signs of overheating.')}
          {check('home', 'Wiring', 'Damage, wear and cables that are unsupported or in the wrong place.')}
          {check('check', 'Tests on every circuit', 'Continuity, insulation resistance, polarity, earth fault loop impedance and RCD trip times.')}
          {check('alert', 'Bathrooms and outdoors', 'The extra protection needed where water and electricity meet.')}
        </ul>
        <div class="eg-figrow">
          <figure class="eg-fig"><img src="/assets/img/guide/esf-socket-check.webp" alt="A socket outlet unscrewed from its back box so its connections can be checked" width="375" height="321" loading="lazy" decoding="async"><figcaption>We take the front off a sample of sockets, switches and lights to check the connections behind them.{CREDIT}</figcaption></figure>
          <figure class="eg-fig"><img src="/assets/img/guide/esf-rcd-test.webp" alt="An electrician holding an RCD tester showing a trip time" width="353" height="348" loading="lazy" decoding="async"><figcaption>Each RCD is tripped with a tester to make sure it switches off fast enough to stop a fatal shock.{CREDIT}</figcaption></figure>
        </div>
      </div>
    </section>

    <section class="bo-section eg-alt" aria-labelledby="eg-result">
      <div class="container">
        <h2 id="eg-result">Satisfactory or Unsatisfactory?</h2>
        <div class="eg-results">
          <div class="eg-res pass"><h3><span class="tick">{icon('check')}</span>Satisfactory</h3><p>No C1 or C2 codes. You can still have C3 recommendations and pass.</p></div>
          <div class="eg-res fail"><h3><span class="eg-x">{icon('alert')}</span>Unsatisfactory</h3><p>At least one C1 or C2. Landlords must put these right within 28 days, or sooner if the report says so.</p></div>
        </div>
      </div>
    </section>

    <section class="bo-section" id="codes" aria-labelledby="eg-codes">
      <div class="container">
        <h2 id="eg-codes">The codes on your report</h2>
        <p class="eg-intro">Each problem the electrician finds is recorded once, at the most serious code that applies.</p>
        <div class="eg-codes">
{code_card('eg-c1', 'C1', 'Danger present', '/assets/img/guide/c1-socket.svg', 'Drawing of a broken socket with a live terminal showing',
           'Someone could get a shock or burn, or a fire could start, as things are today.',
           ['Live parts you can touch, such as a broken socket or a missing cover on the fuse board',
            'Metalwork that has become live because of a fault',
            'The live and neutral swapped over where the supply comes in'],
           'We make it safe before we leave, with your agreement, usually by switching off and isolating that circuit. You get a written danger notice the same day.')}
{code_card('eg-c2', 'C2', 'Potentially dangerous', '/assets/img/guide/esf-taped-cable.webp', 'Photo of a damaged cable joint wrapped in insulating tape',
           'Not dangerous this minute, but one fault, knock or accident away from it.',
           ['A cable joint wrapped in tape instead of being in a proper enclosure',
            'No earth bonding to the gas or water pipes',
            'No RCD protection for sockets that could be used for equipment outdoors',
            'An RCD that does not trip, or trips too slowly'],
           'It needs putting right urgently. We send a plain-English, fixed quote and nothing is done without your OK.', CREDIT)}
{code_card('eg-c3', 'C3', 'Improvement recommended', '/assets/img/guide/c3-labels.svg', 'Drawing of a fuse board with blank circuit labels',
           'Safe, but doesn\'t meet the current edition of the wiring regulations.',
           ['Circuits not labelled at the fuse board',
            'No surge protection where it would now be fitted',
            'An older type of RCD where a newer type is now needed, for example with an EV charger, solar panels or an induction hob',
            'A plastic fuse board under the stairs or on the way out of the house'],
           'Optional. A C3 on its own does not make the report Unsatisfactory.')}
{code_card('eg-fi', 'FI', 'Further investigation', '/assets/img/guide/fi-trace.svg', 'Drawing of a cable disappearing into a wall under a magnifying glass',
           'The electrician has found a reason to suspect a problem but couldn\'t get to the bottom of it during the inspection.',
           ['A circuit that can\'t be traced to where it ends',
            'An RCD that keeps tripping with no obvious cause',
            'Signs of damage to wiring hidden in walls or under floors'],
           'It is a strong recommendation to get it looked into. For landlords it was a legal duty within 28 days for inspections before 30 November 2026; the rules dropped it for inspections from that date.')}
        </div>
        <p class="eg-lim"><b>LIM (limitation) is not a fault.</b> It lists anything the electrician couldn't get to or test, such as a boarded-over loft or a freezer that had to stay on, so the next electrician knows.</p>
      </div>
    </section>

    <section class="bo-section eg-alt" aria-labelledby="eg-myths">
      <div class="container">
        <h2 id="eg-myths">Things that don't fail an EICR on their own</h2>
        <p class="eg-intro">Electrical Safety First's guidance for electricians says these should not be coded just because they are there.</p>
        <ul class="eg-myths">
          <li class="eg-myth"><span class="tick">{icon('check')}</span><div><h3>Old-style rewireable fuses</h3><p>A fuse box with fuse wire isn't a fault in itself, as long as the fuses protect the circuits properly.</p></div></li>
          <li class="eg-myth"><span class="tick">{icon('check')}</span><div><h3>Old red and black wiring</h3><p>Cable colours changed in 2004. Older colours are fine if the wiring is in good condition.</p></div></li>
          <li class="eg-myth"><span class="tick">{icon('check')}</span><div><h3>No earth wire to the sink or bath</h3><p>Kitchen sinks don't need one, and most bathrooms don't when the circuits have RCD protection and the main bonding is in place.</p></div></li>
          <li class="eg-myth"><span class="tick">{icon('check')}</span><div><h3>No switches on sockets</h3><p>Unswitched sockets are still allowed. They don't need changing for an EICR.</p></div></li>
        </ul>
      </div>
    </section>

    <section class="bo-section" aria-labelledby="eg-landlords">
      <div class="container">
        <h2 id="eg-landlords">For landlords: the rules in England</h2>
        <p class="eg-intro">Under the Electrical Safety Standards in the Private Rented Sector (England) Regulations 2020:</p>
        <ol class="eg-rules">
          <li>Have an EICR done at least every 5 years, or sooner if the last report says so.</li>
          <li>Give your tenants a copy within 28 days of the inspection, and new tenants a copy before they move in.</li>
          <li>Send the council a copy within 7 days if they ask for one.</li>
          <li>Put right any C1 or C2 within 28 days, or sooner if the report says so. (For inspections before 30 November 2026, FI items also had to be investigated.)</li>
          <li>Give your tenants and the council written confirmation within 28 days of the work being finished.</li>
        </ol>
        <p class="eg-more"><a href="/landlord-eicr">Landlord EICRs from {PRICE}</a> {icon('arrow')}</p>
      </div>
    </section>

    <section class="bo-section eg-alt" aria-labelledby="eg-not">
      <div class="container">
        <h2 id="eg-not">What an EICR doesn't cover</h2>
        <div class="eg-figrow">
          <figure class="eg-fig"><img src="/assets/img/guide/esf-adaptors.webp" alt="Plugs and adaptors stacked in a double socket" width="369" height="353" loading="lazy" decoding="async"><figcaption><strong>Plugs, leads and appliances.</strong> An EICR covers the fixed wiring. Portable appliances are checked with a separate PAT test. Overloaded adaptors are still worth sorting out.{CREDIT}</figcaption></figure>
          <figure class="eg-fig"><img src="/assets/img/guide/esf-call-105.webp" alt="Sign reading Power cut? Call 105" width="350" height="313" loading="lazy" decoding="async"><figcaption><strong>The meter and main fuse.</strong> These belong to your network operator or energy supplier. If they are damaged we'll tell you, and you can report it free on 105.{CREDIT}</figcaption></figure>
        </div>
      </div>
    </section>

{faq_section(FAQ, 'EICR questions')}
{more_guides('eicr-explained')}
{CTA}  </main>
'''

build_page('eicr-explained',
           'What is an EICR? C1, C2, C3 and FI codes explained | testmyelectrics.com',
           'What an EICR checks, what the codes C1, C2, C3 and FI mean, what makes a report Satisfactory or '
           'Unsatisfactory, and the rules for landlords. Written by NAPIT-registered electricians.',
           MAIN, FAQ, 'EICR guide, built by tools/build-eicr-guide.py from book-online.html.')
print('wrote eicr-explained.html')
