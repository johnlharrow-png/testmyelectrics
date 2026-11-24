/* ==========================================================================
   TestMyElectrics: Google tag, Microsoft Clarity + cookie banner (brief section 04)
   - Does nothing until TME_CONFIG.analytics has a GA4, Google Ads or Clarity ID.
   - Google Consent Mode v2: analytics and ads storage are denied until the
     visitor accepts.
   - Microsoft Clarity (heatmaps + session recordings) only loads after the
     visitor accepts, and stops again if they change their mind.
   - The choice is also kept in a "cookie_consent" cookie on the parent domain,
     so the booking app (book.testmyelectrics.com) doesn't ask a second time.
   ========================================================================== */
(() => {
  'use strict';

  const A = (window.TME_CONFIG && window.TME_CONFIG.analytics) || {};
  const ids = [A.ga4Id, A.adsId].filter(Boolean);
  const clarityId = String(A.clarityId || '').trim();
  const settingsButtons = document.querySelectorAll('[data-cookie-settings]');

  if (!ids.length && !clarityId) {
    // No tags configured, so no cookies to ask about
    settingsButtons.forEach((b) => (b.closest('li') || b).remove());
    return;
  }

  const KEY = 'tme_consent_v1';
  const COOKIE = 'cookie_consent';
  const DENIED = { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' };
  const GRANTED = { ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted', analytics_storage: 'granted' };

  /* ---------- Remembering the choice (this site + the booking subdomain) ---------- */
  function readCookie() {
    const m = document.cookie.match(/(?:^|;\s*)cookie_consent=(granted|denied)/);
    return m ? m[1] : null;
  }
  function writeCookie(value) {
    const host = location.hostname;
    const parts = host.split('.');
    const parent = /^[\d.]+$/.test(host) || parts.length < 2 ? '' : parts.slice(parts.length >= 3 ? 1 : 0).join('.');
    const base = `${COOKIE}=${value}; path=/; max-age=${180 * 24 * 3600}; SameSite=Lax` + (location.protocol === 'https:' ? '; Secure' : '');
    if (parent) document.cookie = `${base}; domain=${parent}`;
    if (readCookie() !== value) document.cookie = base;   // parent domain refused (e.g. a preview host)
  }

  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch (_) { /* storage blocked */ }
  if (saved !== 'granted' && saved !== 'denied') saved = readCookie();

  /* ---------- Google tag (GA4 + Ads), Consent Mode v2 ---------- */
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() { window.dataLayer.push(arguments); };
  const gtag = window.gtag;
  if (ids.length) {
    gtag('consent', 'default', { ...DENIED, wait_for_update: 500 });
    if (saved === 'granted') gtag('consent', 'update', GRANTED);
    // Fetch the tag (about 340 KB) on the visitor's first scroll, tap or key press, or 4 seconds after
    // the page has loaded, whichever comes first. Google's speed test counts anything fetched before the
    // first screen appears against the main photo. The calls below wait in dataLayer until it arrives;
    // ad click IDs still reach the booking app in the link (eeg_attr).
    let tagLoaded = false;
    const WAKE = ['scroll', 'pointerdown', 'touchstart', 'keydown'];
    const loadTag = () => {
      if (tagLoaded) return;
      tagLoaded = true;
      WAKE.forEach((ev) => window.removeEventListener(ev, loadTag));
      const tag = document.createElement('script');
      tag.async = true;
      tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ids[0]);
      document.head.appendChild(tag);
    };
    WAKE.forEach((ev) => window.addEventListener(ev, loadTag, { once: true, passive: true }));
    const later = () => setTimeout(loadTag, 4000);
    if (document.readyState === 'complete') later();
    else window.addEventListener('load', later, { once: true });
    gtag('js', new Date());
    ids.forEach((id) => gtag('config', id));
  }

  /* ---------- Microsoft Clarity: heatmaps + recordings, only with consent ---------- */
  let clarityLoaded = false;
  function startClarity() {
    if (!clarityId) return;
    if (!clarityLoaded) {
      clarityLoaded = true;
      window.clarity = window.clarity || function () { (window.clarity.q = window.clarity.q || []).push(arguments); };
      const s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.clarity.ms/tag/' + encodeURIComponent(clarityId);
      document.head.appendChild(s);
    }
    window.clarity('consentv2', { ad_Storage: 'denied', analytics_Storage: 'granted' });
  }
  function stopClarity() {
    if (!clarityLoaded || typeof window.clarity !== 'function') return;
    window.clarity('consentv2', { ad_Storage: 'denied', analytics_Storage: 'denied' });
    window.clarity('consent', false);   // erase Clarity's cookies and stop recording
  }
  if (saved === 'granted') startClarity();

  /* ---------- Banner ---------- */
  const tools = [];
  if (A.ga4Id) tools.push('Google Analytics');
  if (A.adsId) tools.push('Google Ads');
  if (clarityId) tools.push('Microsoft Clarity');
  const toolText = tools.length > 1 ? `${tools.slice(0, -1).join(', ')} and ${tools[tools.length - 1]}` : tools[0];

  let banner = null;
  function choose(value) {
    try { localStorage.setItem(KEY, value); } catch (_) { /* storage blocked */ }
    writeCookie(value);
    if (ids.length) gtag('consent', 'update', value === 'granted' ? GRANTED : DENIED);
    if (value === 'granted') startClarity(); else stopClarity();
    if (banner) { banner.remove(); banner = null; }
    document.documentElement.style.removeProperty('--consent-h');
  }
  function showBanner() {
    if (banner) return;
    banner = document.createElement('div');
    banner.className = 'consent';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Cookie choices');
    banner.innerHTML = `
      <p><strong>Cookies</strong><span class="consent-long">Analytics and ad cookies (${toolText}) stay off unless you accept. We count visits without cookies; Reject turns that off too. <a href="/privacy#stats">Privacy policy</a></span><span class="consent-short">Analytics &amp; ad cookies? <a href="/privacy#cookies">Privacy</a></span></p>
      <div class="consent-actions">
        <button type="button" class="btn btn-ink btn-sm" data-choice="denied">Reject</button>
        <button type="button" class="btn btn-ink btn-sm" data-choice="granted">Accept</button>
      </div>`;
    banner.addEventListener('click', (e) => {
      const b = e.target.closest('[data-choice]');
      if (b) choose(b.dataset.choice);
    });
    document.body.appendChild(banner);
    // The phone booking bar sits just above the strip (styles.css reads --consent-h)
    const setH = () => { if (banner) document.documentElement.style.setProperty('--consent-h', banner.offsetHeight + 'px'); };
    // ResizeObserver reports the first size itself, after layout, so reading offsetHeight doesn't force a reflow
    if ('ResizeObserver' in window) new ResizeObserver(setH).observe(banner);
    else requestAnimationFrame(setH);
  }

  if (!saved) showBanner();
  else if (saved !== readCookie()) writeCookie(saved);   // share an earlier choice with the booking app
  settingsButtons.forEach((b) => b.addEventListener('click', showBanner));
})();
