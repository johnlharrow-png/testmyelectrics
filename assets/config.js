/* ==========================================================================
   TestMyElectrics: site configuration
   Everything the team (or Wayne) is likely to change lives in this file.
   See INTEGRATION.md for how the site links into the booking app.
   ========================================================================== */
window.TME_CONFIG = {
  business: {
    name: 'TestMyElectrics',
    email: 'bookings@testmyelectrics.com',
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

  /* Google reviews on /book-online. The badge (score, count, stars) only shows once BOTH score and url
     are filled in, so the rating links to reviews people can check. The TestMyElectrics.com Google
     listing had no reviews on 2026-11-23, so all of this is empty for now.
     - url: the link to your reviews (Google Business Profile > Read reviews > Share)
     - items: 2–3 real reviews, copied word for word, e.g.
       { text: 'The review, word for word', name: 'First name', detail: 'landlord, Chelmsford' }
       The reviews section appears as soon as there's at least one. */
  reviews: {
    score: '',
    count: '',
    url: '',
    items: [],
  },

  /* Tracking (brief section 04). Use the SAME IDs as Back office > Settings > Marketing.
     All empty = no tags and no cookie banner. Everything waits for the cookie banner (consent.js).
     - ga4Id: Google Analytics 4 (visits, where people came from, button clicks as "button_click" events)
     - adsId: Google Ads tag, account 184-703-9523 (keeps the ad click so the booking counts as a conversion)
     - clarityId: Microsoft Clarity project ID (heatmaps and recordings of where people click) */
  analytics: {
    ga4Id: 'G-RZZKMYENGW',     // same property as the booking app (Back office > Settings > Marketing)
    adsId: 'AW-18579487106',
    clarityId: 'zf2uvj0rgx',   // same Clarity project as the booking app (linked to Analytics)
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

    /* Letting agents page (/letting-agents): the AGENT price list, not the public one above.
       Source of truth: Back office > Agent prices (Testing prices and Remedial prices tabs).
       The flyer PDF has the same table. Copied from the flyer on 18 Nov 2026.
       If the back office changes, change these numbers the same day. The page shows inc VAT
       in brackets, worked out from these (x 1.2). The item wording is in letting-agents.html. */
    AGENT: {
      // EICR and add-ons ("from" prices for the EICR)
      studio: 79, flat: 99, house: 120, included: 8, extraCircuit: 10,
      smoke: 30, patUpTo10: 40, patExtra: 1,
      spendLimit: 150,   // the spend limit per job we suggest to agents
      // Fixes on the visit: sockets, switches and lights
      socket: 20, spur: 25, cookerSwitch: 30, ceilingRose: 25, ledBatten: 45, gu10: 15,
      ip65Light: 50, outdoorSocket: 45, enclose: 25,
      // Consumer unit: blanks, seals and devices
      blanks: 15, seal: 15, rcd: 70, mcb: 25, labels: 10,
      // Earthing and bonding
      bondingClamp: 20, bondingOne: 65, bondingBoth: 110,
      // Consumer unit replacement (separate visit)
      cuDualRcd: 495, cuRcbo: 650, cuExtraCircuit: 25, tails: 75,
    },
  },

  /* Letting agents page: files on the booking app (BASE). */
  agents: {
    priceListPdf: '/downloads/testmyelectrics-letting-agents.pdf',
  },

  /* Postcode coverage for homes & rentals (used by the "Do we cover you?" checker).
     Entries can be postcode AREAS ('CM') or DISTRICTS ('EN9'). */
  coverage: {
    domestic: ['CM', 'SS', 'CO', 'RM', 'IG', 'E4', 'EN9', 'CB10', 'CB11'],   // East London postcodes: E4 only for homes
  },
};
