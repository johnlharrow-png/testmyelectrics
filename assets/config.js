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

  /* BASE: the booking app's address (brief section 01).
     Every "Book" button, the postcode boxes and "My account" are built from this one value.
     TEMPORARY: book.testmyelectrics.com doesn't exist yet (Wayne needs to add it as a custom
     domain on the booking app in Railway, then a CNAME in GoDaddy). Until then this points at
     the app's Railway address so the buttons work. Switch it back to
     'https://book.testmyelectrics.com' as soon as that address loads. */
  booking: {
    base: 'https://eicr-web-production.up.railway.app',
  },

  /* "Request a callback" form (more than one board, several properties, business)
     -> POST BASE/api/public/lead (brief section 05).
     Leave false until Wayne has added https://testmyelectrics.com to the app's CORS list
     AND BASE is live; until then browsers block the request, so the form asks people to email. */
  callback: {
    enabled: false,
  },

  /* Google tags (brief section 04). Use the SAME IDs Wayne enters in
     Back office > Settings > Marketing. Empty = no tags and no cookie banner. */
  analytics: {
    ga4Id: '',   // e.g. 'G-XXXXXXXXXX'
    adsId: '',   // e.g. 'AW-XXXXXXXXX'
  },

  /* Prices shown on the site, EXCLUDING VAT (weekday appointments).
     They MUST match the back office, because the booking page charges what the back office says.
     If you change a number here, also check the tier labels in index.html and the JSON-LD block. */
  pricing: {
    EICR_DOM:   { studio: 79, bed1: 90, bed2: 100, bed3: 110, bed4: 120, bed5: 130, bed6: 140, included: 8, extra: 15 },
    PAT:        { upTo10: 59.95, extra: 1.5 },   // back office: £71.94 inc VAT for 10 items, £1.80 inc VAT each extra
    FIRE:       { price: 50, included: 6, extra: 8.33 },
    COMMERCIAL: { price: 169, included: 10, extra: 10 },
    EMERGENCY:  { monthly: 80, annual: 199 },
  },

  /* Postcode coverage for homes & rentals (used by the "Do we cover you?" checker).
     Entries can be postcode AREAS ('CM') or DISTRICTS ('EN9'). */
  coverage: {
    domestic: ['CM', 'SS', 'CO', 'RM', 'IG', 'E', 'EN9', 'CB10', 'CB11'],
  },
};
