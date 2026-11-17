/* ==========================================================================
   TestMyElectrics: site configuration
   Everything the team (or Wayne) is likely to change lives in this file.
   See INTEGRATION.md for how the site links into the booking app.
   ========================================================================== */
window.TME_CONFIG = {
  business: {
    name: 'TestMyElectrics',
    email: 'bookings@testmyelectrics.com',  // TODO: confirm mailbox exists
  },

  /* BASE: the booking app's permanent address (brief section 01).
     Every "Book" button, the postcode boxes and "My account" are built from this one value. */
  booking: {
    base: 'https://book.testmyelectrics.com',
  },

  /* "Request a callback" form (more than one board, several properties, business).
     Posts to /api/lead on this website; Caddy (Caddyfile) forwards it server-side to the
     booking app's /api/public/lead, so it works without the app allowing this domain (CORS). */
  callback: {
    enabled: true,
    endpoint: '/api/lead',
  },

  /* Google reviews badge at the top of /book-online. Paste the link to your Google reviews
     into url (from your Google Business Profile) and the badge becomes a link to it. */
  reviews: {
    score: '4.7',
    url: '',
  },

  /* Tracking (brief section 04). Use the SAME IDs as Back office > Settings > Marketing.
     All empty = no tags and no cookie banner. Everything waits for the cookie banner (consent.js).
     - ga4Id: Google Analytics 4 (visits, where people came from, button clicks as "button_click" events)
     - adsId: Google Ads tag, account 184-703-9523 (keeps the ad click so the booking counts as a conversion)
     - clarityId: Microsoft Clarity project ID (heatmaps and recordings of where people click) */
  analytics: {
    ga4Id: 'G-RZZKMYENGW',     // same property as the booking app (Back office > Settings > Marketing)
    adsId: 'AW-18579487106',
    clarityId: '',             // e.g. 'abcd1234ef' (Clarity > Settings > Overview > Project ID)
  },

  /* Prices shown on the site, EXCLUDING VAT (appointments are Monday to Friday only).
     They MUST match the back office, because the booking page charges what the back office says.
     If you change a number here, also check the tier labels in index.html and the JSON-LD block. */
  pricing: {
    EICR_DOM:   { studio: 79, bed1: 90, bed2: 100, bed3: 110, bed4: 120, bed5: 130, bed6: 140, included: 8, extra: 15 },
    // Homebuyer's report = EICR + written report. Booked online as service HOMEBUYER (same prices in Back office > Settings > Prices).
    HOMEBUYER:  { studio: 149, bed1: 159, bed2: 169, bed3: 189, bed4: 209, bed5: 229, bed6: 249, included: 8, extra: 15 },
    // PAT testing and the alarm check are add-ons only: booked with a Domestic EICR or homebuyer's report
    PAT:        { upTo10: 40, extra: 1.5 },   // back office: £48 inc VAT for 10 items, £1.80 inc VAT each extra
    FIRE:       { price: 40, included: 6, extra: 8.33 },
    COMMERCIAL: { price: 169, included: 10, extra: 10 },
    EMERGENCY:  { monthly: 80, annual: 199 },
  },

  /* Postcode coverage for homes & rentals (used by the "Do we cover you?" checker).
     Entries can be postcode AREAS ('CM') or DISTRICTS ('EN9'). */
  coverage: {
    domestic: ['CM', 'SS', 'CO', 'RM', 'IG', 'E', 'EN9', 'CB10', 'CB11'],
  },
};
