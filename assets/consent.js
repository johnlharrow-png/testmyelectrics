/* ==========================================================================
   TestMyElectrics: Google tag + cookie banner (integration brief, section 04)
   - Does nothing until TME_CONFIG.analytics has a GA4 or Google Ads ID.
   - Google Consent Mode v2: analytics and ads storage are denied until the
     visitor accepts. The booking app has its own banner for its own tags.
   ========================================================================== */
(() => {
  'use strict';

  const A = (window.TME_CONFIG && window.TME_CONFIG.analytics) || {};
  const ids = [A.ga4Id, A.adsId].filter(Boolean);
  const settingsButtons = document.querySelectorAll('[data-cookie-settings]');

  if (!ids.length) {
    // No tags configured, so no cookies to ask about
    settingsButtons.forEach((b) => (b.closest('li') || b).remove());
    return;
  }

  const KEY = 'tme_consent_v1';
  const DENIED = { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' };
  const GRANTED = { ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted', analytics_storage: 'granted' };

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() { window.dataLayer.push(arguments); };
  const gtag = window.gtag;

  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch (_) { /* storage blocked */ }

  gtag('consent', 'default', { ...DENIED, wait_for_update: 500 });
  if (saved === 'granted') gtag('consent', 'update', GRANTED);

  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ids[0]);
  document.head.appendChild(tag);
  gtag('js', new Date());
  ids.forEach((id) => gtag('config', id));

  let banner = null;
  function choose(value) {
    try { localStorage.setItem(KEY, value); } catch (_) { /* storage blocked */ }
    gtag('consent', 'update', value === 'granted' ? GRANTED : DENIED);
    if (banner) { banner.remove(); banner = null; }
  }
  function showBanner() {
    if (banner) return;
    banner = document.createElement('div');
    banner.className = 'consent';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Cookie choices');
    banner.innerHTML = `
      <p><strong>Cookies</strong>We'd like to use Google Analytics and Google Ads cookies to see how the site is used and which ads work. They stay off unless you accept. <a href="/privacy">Privacy policy</a></p>
      <div class="consent-actions">
        <button type="button" class="btn btn-ink btn-sm" data-choice="denied">Reject</button>
        <button type="button" class="btn btn-ink btn-sm" data-choice="granted">Accept</button>
      </div>`;
    banner.addEventListener('click', (e) => {
      const b = e.target.closest('[data-choice]');
      if (b) choose(b.dataset.choice);
    });
    document.body.appendChild(banner);
  }

  if (!saved) showBanner();
  settingsButtons.forEach((b) => b.addEventListener('click', showBanner));
})();
