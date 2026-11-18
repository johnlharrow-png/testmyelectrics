/* ==========================================================================
   TestMyElectrics: page behaviour
   - Builds every booking / My account link from TME_CONFIG.booking.base (BASE)
   - Postcode boxes send people to BASE/book/?service=…&postcode=…
   - Business callback form (POST BASE/api/public/lead) when switched on
   - Coverage checker, nav, prices from config, mobile CTA bar
   See INTEGRATION.md.
   ========================================================================== */
(() => {
  'use strict';

  const CFG = window.TME_CONFIG;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const icon = (id) => `<svg class="icon" aria-hidden="true"><use href="#${id}"/></svg>`;
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const gbp = (n) => '£' + (Number.isInteger(Number(n))
    ? Number(n).toLocaleString('en-GB')
    : Number(n).toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
  const emailLink = () => `<a href="mailto:${esc(CFG.business.email)}">${esc(CFG.business.email)}</a>`;

  /* ---------- Postcodes & coverage ---------- */
  function parsePostcode(value) {
    const s = String(value || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
    const m = s.match(/^([A-Z]{1,2}\d[A-Z\d]?)(\d[A-Z]{2})?$/);
    if (!m) return null;
    return { outward: m[1], area: m[1].match(/^[A-Z]+/)[0], full: !!m[2], formatted: m[2] ? `${m[1]} ${m[2]}` : m[1] };
  }
  function isCovered(pc) {
    const list = CFG.coverage.domestic;
    return !!pc && (list.includes(pc.area) || list.includes(pc.outward));
  }

  /* ---------- Booking-app links (brief section 02) ---------- */
  const BASE = String(CFG.booking.base || '').replace(/\/+$/, '');

  // Ad parameters saved by the brief's tracking script (section 03), so links built later still carry them
  function savedAttribution() {
    try { return JSON.parse(sessionStorage.getItem('eeg_attr') || '{}') || {}; } catch (_) { return {}; }
  }
  function bookUrl(service, postcode) {
    if (!BASE) return '#book';
    const u = new URL(BASE + '/book/');
    if (service) u.searchParams.set('service', service);
    if (postcode) u.searchParams.set('postcode', postcode);
    const attr = savedAttribution();
    Object.keys(attr).forEach((k) => { if (!u.searchParams.has(k)) u.searchParams.set(k, attr[k]); });
    return u.toString();
  }
  const portalUrl = BASE ? BASE + '/portal/' : '#book';

  $$('[data-book]').forEach((a) => { a.href = bookUrl(a.dataset.book || ''); });
  $$('[data-portal]').forEach((a) => { a.href = portalUrl; });
  // Other files on the booking app, e.g. data-app="agents.priceListPdf" (a key in config.js)
  $$('[data-app]').forEach((a) => {
    let path = CFG;
    for (const key of a.dataset.app.split('.')) path = path == null ? path : path[key];
    if (BASE && typeof path === 'string') a.href = BASE + path;
  });

  window.TME = { parsePostcode, isCovered, bookUrl };

  /* ---------- Click tracking (Google Analytics) ----------
     Every link and button click goes to GA4 as a "button_click" event with the button's text,
     where it goes and which part of the page it was in. Phone and email links also send
     "phone_click" / "email_click", which can be marked as key events (conversions) in GA4.
     Nothing is sent unless consent.js has loaded the Google tag; Consent Mode decides what GA4 keeps. */
  document.addEventListener('click', (e) => {
    const el = e.target.closest('a, button, summary');
    if (!el || typeof window.gtag !== 'function' || el.closest('.consent')) return;
    const text = (el.getAttribute('aria-label') || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 100);
    const area = el.closest('section[id], header, footer, nav, .mobile-cta');
    const href = el.getAttribute('href') || '';
    const params = {
      link_text: text,
      link_url: el.href || href,
      click_location: area ? (area.id || area.className.split(' ')[0] || area.tagName.toLowerCase()) : 'page',
    };
    window.gtag('event', 'button_click', params);
    if (href.startsWith('tel:')) window.gtag('event', 'phone_click', params);
    if (href.startsWith('mailto:')) window.gtag('event', 'email_click', params);
  }, true);

  /* ---------- Contact details + prices from config ---------- */
  $$('[data-email]').forEach((el) => { el.textContent = CFG.business.email; });
  $$('[data-email-link]').forEach((a) => { a.href = 'mailto:' + CFG.business.email; });
  $$('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });
  const RV = CFG.reviews || {};
  $$('[data-rv-score]').forEach((el) => { if (RV.score) el.textContent = RV.score; });
  $$('[data-reviews]').forEach((a) => {
    const score = parseFloat(RV.score);
    if (score) {
      a.setAttribute('aria-label', `Rated ${RV.score} out of 5 on Google`);
      const stars = a.querySelector('.rv-stars');
      if (stars) stars.style.setProperty('--rv', `${Math.min(100, score * 20)}%`);
    }
    if (RV.url) { a.href = RV.url; a.target = '_blank'; a.rel = 'noopener'; }
  });
  const priceOf = (path) => {
    let v = CFG.pricing;
    for (const key of path.split('.')) v = v == null ? v : v[key];
    return typeof v === 'number' ? v : null;
  };
  $$('[data-price]').forEach((el) => {
    const v = priceOf(el.dataset.price);
    if (v != null) el.textContent = gbp(v);
  });
  // The same price with VAT at 20% (config prices are ex VAT), rounded to the penny
  $$('[data-price-inc]').forEach((el) => {
    const v = priceOf(el.dataset.priceInc);
    if (v != null) el.textContent = gbp(Math.round(v * 120) / 100);
  });
  $$('[data-cfg]').forEach((el) => {
    let v = CFG;
    for (const key of el.dataset.cfg.split('.')) v = v == null ? v : v[key];
    if (v != null) el.textContent = v;
  });

  /* ---------- Header + mobile nav ---------- */
  const header = $('[data-header]');
  const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const toggle = $('[data-nav-toggle]');
  const mnav = $('[data-mobile-nav]');
  const setNav = (open) => {
    if (!toggle || !mnav) return;   // pages without a menu (e.g. the ad landing page)
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    mnav.hidden = !open;
  };
  if (toggle && mnav) {
    toggle.addEventListener('click', () => setNav(mnav.hidden));
    mnav.addEventListener('click', (e) => { if (e.target.closest('a')) setNav(false); });
    window.matchMedia('(min-width: 1121px)').addEventListener('change', (e) => { if (e.matches) setNav(false); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setNav(false); });
  }

  /* ---------- Callback form: more than one board / several properties / business ---------- */
  // Sends to BASE/api/public/lead (brief §05). Needs callback.enabled in config.js, which in turn
  // needs Wayne to allow this website's domain (CORS) on the booking app.
  const cbForm = $('[data-callback-form]');
  const cbStatus = cbForm && $('[data-cb-status]', cbForm);
  const LEAD_URL = (CFG.callback && CFG.callback.endpoint) || (BASE ? BASE + '/api/public/lead' : '');
  const callbackOn = !!(cbForm && CFG.callback && CFG.callback.enabled && LEAD_URL);

  function goToCallback(postcode, need) {
    if (!$('#callback')) { window.location.href = '/#callback'; return; }   // pages without the callback section
    if (cbForm && postcode && !cbForm.elements.postcode.value) cbForm.elements.postcode.value = postcode;
    // e.g. need = 'homebuyer': tick just that box in "What do you need?"
    const needBox = cbForm && need && $(`input[name="needs"][data-need="${need}"]`, cbForm);
    if (needBox) $$('input[name="needs"]', cbForm).forEach((i) => { i.checked = i === needBox; });
    $('#callback').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    history.replaceState(null, '', '#callback');
    setTimeout(() => { if (cbForm) cbForm.elements.name.focus({ preventScroll: true }); }, reduceMotion ? 0 : 600);
  }

  // Buttons for services that are quoted rather than booked online (e.g. the homebuyer's report)
  $$('[data-callback-need]').forEach((a) => a.addEventListener('click', (e) => {
    e.preventDefault();
    goToCallback('', a.dataset.callbackNeed);
  }));

  function setStatus(type, html) {
    cbStatus.className = `cb-status is-${type}`;
    cbStatus.innerHTML = html;
    cbStatus.hidden = false;
  }

  function showThanks(name) {
    const first = (name || '').split(' ')[0];
    const box = document.createElement('div');
    box.className = 'cb-thanks';
    box.tabIndex = -1;
    box.innerHTML = `<strong>Thanks${first ? ', ' + esc(first) : ''}. We've got your request.</strong><p>We'll call you back to talk through your properties and give you a price.</p>`;
    cbForm.replaceWith(box);
    box.focus();
  }

  if (cbForm) {
    cbForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const f = cbForm.elements;
      const v = (n) => (f[n] && f[n].value ? f[n].value.trim() : '');
      const picked = (n) => { const el = cbForm.querySelector(`input[name="${n}"]:checked`); return el ? el.value : ''; };
      if (v('website')) { showThanks(v('name')); return; }   // honeypot: bots get a fake success

      const name = v('name');
      const phone = v('phone');
      const email = v('email');
      if (!name) { setStatus('error', 'Please give your name.'); f.name.focus(); return; }
      if (!phone && !email) { setStatus('error', 'Please give a phone number or an email address so we can call you back.'); f.phone.focus(); return; }
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { setStatus('error', 'Please check your email address.'); f.email.focus(); return; }
      if (!callbackOn) {
        setStatus('error', `Sorry, online callback requests aren't switched on yet. Please email us at ${emailLink()}.`);
        return;
      }

      const needs = $$('input[name="needs"]:checked', cbForm);
      const services = [...new Set(needs.map((i) => i.value).filter(Boolean))];   // only the app's own codes
      const pc = parsePostcode(v('postcode'));
      const message = [
        'Callback request from testmyelectrics.com',
        `I'm a: ${picked('who') || 'not given'}`,
        `Properties: ${picked('properties') || 'not given'}`,
        `Fuse boards per property: ${picked('boards') || 'not given'}`,
        needs.length && `Needs: ${needs.map((i) => i.dataset.label).join(', ')}`,
        v('organisation') && `Company: ${v('organisation')}`,
        v('message') && `Notes: ${v('message')}`,
      ].filter(Boolean).join('\n');

      const btn = $('button[type="submit"]', cbForm);
      btn.disabled = true;
      setStatus('info', 'Sending…');
      try {
        const res = await fetch(LEAD_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ kind: 'callback', name, phone, email, postcode: pc ? pc.formatted : v('postcode'), message, services }),
        });
        let data = {};
        try { data = await res.json(); } catch (_) { /* empty body */ }
        if (!res.ok || !data.ok) {
          const err = new Error(data.error || `HTTP ${res.status}`);
          err.userMessage = data.error;
          throw err;
        }
        showThanks(name);
        if (typeof window.gtag === 'function') window.gtag('event', 'generate_lead', { form: 'callback' });
      } catch (err) {
        console.error('[TME] callback failed', err);
        setStatus('error', `${err.userMessage ? esc(err.userMessage) + '.' : "Sorry, we couldn't send that just now."} Please try again, or email us at ${emailLink()}.`);
      } finally {
        btn.disabled = false;
      }
    });
  }

  /* ---------- Letting agents: "Get your agent account" form (/letting-agents) ----------
     Same route as the callback form: POST /api/lead on this site, which Caddy forwards to the
     booking app's /api/public/lead. kind "agent_request" lands in Back office > Leads and is
     emailed to the office, who then send the invite (Back office > Letting agents > Invite an agent).
     The agency and the number of properties go in message, as the app asks. */
  const agForm = $('[data-agent-form]');
  if (agForm) {
    const agStatus = $('[data-ag-status]', agForm);
    const say = (type, html) => {
      agStatus.className = `cb-status is-${type}`;
      agStatus.innerHTML = html;
      agStatus.hidden = false;
    };
    const thanks = (name) => {
      const first = (name || '').split(' ')[0];
      const box = document.createElement('div');
      box.className = 'cb-thanks';
      box.tabIndex = -1;
      box.innerHTML = `<strong>Thanks${first ? ', ' + esc(first) : ''}. We've got your request.</strong>`
        + '<p>We\'ll set up your agent account and email you a login link. The link works for 2 days: open it, sign our agent terms once, and you can raise your first job.</p>';
      agForm.replaceWith(box);
      box.focus();
    };

    agForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const f = agForm.elements;
      const v = (n) => (f[n] && f[n].value ? f[n].value.trim() : '');
      if (v('website')) { thanks(v('name')); return; }   // honeypot: bots get a fake success

      const agency = v('agency');
      const name = v('name');
      const email = v('email');
      const phone = v('phone');
      const props = (agForm.querySelector('input[name="properties"]:checked') || {}).value || '';
      if (!agency) { say('error', 'Please give the name of your agency.'); f.agency.focus(); return; }
      if (!name) { say('error', 'Please give your name.'); f.name.focus(); return; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
        say('error', 'Please give your work email address. Your login link goes to it.');
        f.email.focus();
        return;
      }
      if (!(CFG.callback && CFG.callback.enabled && LEAD_URL)) {
        say('error', `Sorry, online requests aren't switched on yet. Please email us at ${emailLink()}.`);
        return;
      }

      // Which email or ad brought them here (saved by the tracking script at the bottom of the page)
      const attr = savedAttribution();
      const source = ['utm_source', 'utm_medium', 'utm_campaign'].map((k) => attr[k]).filter(Boolean).join(' / ')
        || (attr.gclid || attr.gbraid || attr.wbraid ? 'Google Ads' : '');
      const message = [
        'Agent account request from testmyelectrics.com/letting-agents',
        `Agency: ${agency}`,
        `Properties managed: ${props || 'not given'}`,
        source && `Came from: ${source}`,
      ].filter(Boolean).join('\n');

      const btn = $('button[type="submit"]', agForm);
      btn.disabled = true;
      say('info', 'Sending…');
      try {
        const res = await fetch(LEAD_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ kind: 'agent_request', name, email, phone, message }),
        });
        let data = {};
        try { data = await res.json(); } catch (_) { /* empty body */ }
        if (!res.ok || !data.ok) {
          const err = new Error(data.error || `HTTP ${res.status}`);
          err.userMessage = data.error;
          throw err;
        }
        thanks(name);
        // The conversion: mark generate_lead as a key event in GA4 and import it into Google Ads
        if (typeof window.gtag === 'function') window.gtag('event', 'generate_lead', { form: 'agent_request' });
      } catch (err) {
        console.error('[TME] agent request failed', err);
        say('error', `${err.userMessage ? esc(err.userMessage) + '.' : "Sorry, we couldn't send that just now."} Please try again, or email us at ${emailLink()}.`);
      } finally {
        btn.disabled = false;
      }
    });
  }

  /* ---------- Screenshots (letting agents page) ----------
     A screenshot that isn't in assets/img/agents/ yet is hidden instead of showing a broken image:
     a missing phone overlay just goes, a missing main screenshot takes its whole card with it. */
  $$('img[data-shot]').forEach((img) => {
    const missing = () => {
      const phone = img.closest('.shot-phone');
      const card = img.closest('.ag-shot');
      if (phone && card && card.querySelector('.shot-frame')) phone.hidden = true;
      else if (card) card.hidden = true;
    };
    if (img.complete && !img.naturalWidth) missing();
    else img.addEventListener('error', missing);
  });

  /* ---------- Postcode boxes: straight into the booking app ---------- */
  $$('[data-quick-book]').forEach((form) => {
    // EICR add-ons (alarm check, PAT). Sent as ?service=EICR_DOM,FIRE,PAT. The booking app needs a one-line
    // change to read the list (see INTEGRATION.md); until then it just pre-selects the EICR.
    const addons = $('[data-addons]', form);
    const takesAddons = (v) => v === 'EICR_DOM' || v === 'HOMEBUYER';   // the homebuyer's report includes an EICR
    const syncAddons = () => { if (addons) addons.hidden = !takesAddons(form.elements.service.value); };
    form.elements.service.addEventListener('change', syncAddons);
    syncAddons();

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const extras = takesAddons(form.elements.service.value) ? $$('input[name="addons"]:checked', form).map((i) => i.value) : [];
      const service = [form.elements.service.value, ...extras].join(',');
      const raw = form.elements.postcode.value.trim();
      const pc = parsePostcode(raw);
      const postcode = pc ? pc.formatted : raw.toUpperCase();
      if (service.startsWith('business')) { goToCallback(postcode); return; }
      window.location.href = bookUrl(service, postcode);
    });
  });

  /* ---------- Coverage checker ---------- */
  const cov = $('[data-coverage-check]');
  const out = $('[data-coverage-result]');
  if (cov) cov.addEventListener('submit', (e) => {
    e.preventDefault();
    const pc = parsePostcode(cov.elements.postcode.value);
    if (!pc) {
      out.className = 'checker-result bad';
      out.innerHTML = `${icon('i-alert')}<span>That doesn't look like a UK postcode. Try something like CM2 or SS1 4AB.</span>`;
      return;
    }
    if (isCovered(pc)) {
      out.className = 'checker-result ok';
      out.innerHTML = `${icon('i-check')}<span>Yes, we cover <strong>${esc(pc.outward)}</strong> for homes, rentals and businesses. <a href="${esc(bookUrl('EICR_DOM', pc.full ? pc.formatted : ''))}">Book now →</a></span>`;
    } else {
      out.className = 'checker-result maybe';
      out.innerHTML = `${icon('i-alert')}<span><strong>${esc(pc.outward)}</strong> is outside our usual area for homes. Email us at ${emailLink()} and we'll see if we can help. Commercial sites are covered UK-wide.</span>`;
    }
  });

  /* ---------- Mobile sticky CTA: shown once the hero is gone, hidden over the booking section ----------
     (or over the section named in data-hide-over, e.g. the request form on /letting-agents) */
  const bar = $('[data-mobile-bar]');
  const hero = $('.hero');
  const book = bar && $(bar.dataset.hideOver || '#book');
  if (bar && hero && book && 'IntersectionObserver' in window) {
    let heroOn = true;
    let bookOn = false;
    const update = () => bar.classList.toggle('is-visible', !heroOn && !bookOn);
    new IntersectionObserver(([en]) => { heroOn = en.isIntersecting; update(); }).observe(hero);
    new IntersectionObserver(([en]) => { bookOn = en.isIntersecting; update(); }, { threshold: 0.02 }).observe(book);
  }
})();
