// Puts each page's own styles inside the page (critical CSS), so the first screen can be drawn
// without waiting for /assets/styles.css. The full stylesheet still loads straight after, without
// holding up the page, and is cached for the rest of the site.
//
// Run after changing styles.css, any page, or running the page builders:
//     npm install            (once)
//     npm run inline-css     (or: node tools/inline-css.mjs page.html ...)
// The build scripts in tools/ run it for you if node_modules is installed.
//
// It is safe to run again: it first puts the plain <link rel="stylesheet"> back, then rebuilds the block
// between the <!-- critical-css --> markers from the current styles.css.
import Beasties from 'beasties';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

// Classes and states the scripts add after the page loads: keep their rules in the page too, so the
// cookie banner, the sticky phone bar, the scrolled header and the mobile menu never show unstyled.
const ALLOW = [/consent/, /is-scrolled/, /is-visible/, /needs-postcode/, /aria-expanded/, /\[hidden\]/, /mobile-bar/, /nav/];

const BLOCK = /<!-- critical-css -->[\s\S]*?<!-- \/critical-css -->/;
const LINK = /<link rel="stylesheet" href="(\/?assets\/styles\.css(?:\?v=[^"]*)?)">/;

class SiteBeasties extends Beasties {
  // hrefs carry ?v= cache-busting numbers; read the file on disk
  readFile(filename) {
    return fs.readFileSync(filename.replace(/\?.*$/, ''), 'utf8');
  }
}

const beasties = new SiteBeasties({
  path: ROOT,
  publicPath: '/',
  preload: 'swap',
  pruneSource: false,
  reduceInlineStyles: false,
  inlineFonts: false,
  preloadFonts: false,
  compress: true,
  mergeStylesheets: false,
  keyframes: 'critical',
  allowRules: ALLOW,
  logLevel: 'warn',
});

function restore(html) {
  const m = html.match(BLOCK);
  if (!m) return html;
  const href = m[0].match(/data-href="([^"]+)"/)[1];
  return html.replace(BLOCK, `<link rel="stylesheet" href="${href}">`);
}

async function inline(file) {
  const src = restore(fs.readFileSync(file, 'utf8'));
  const link = src.match(LINK);
  if (!link) return null;
  const href = link[1].startsWith('/') ? link[1] : '/' + link[1];
  // Beasties works out which rules this page uses; take just that CSS and write the block ourselves
  const out = await beasties.process(src.replace(LINK, `<link rel="stylesheet" href="${href}">`));
  const styles = [...out.matchAll(/<style>([\s\S]*?)<\/style>/g)].map((m) => m[1]);
  const before = [...src.matchAll(/<style>([\s\S]*?)<\/style>/g)].map((m) => m[1]);
  const critical = styles.filter((s) => !before.includes(s)).join('');
  if (!critical) throw new Error(`${path.basename(file)}: no critical CSS produced`);
  const block = [
    '<!-- critical-css -->',
    `<style data-critical data-href="${href}">${critical}</style>`,
    `<link rel="preload" href="${href}" as="style" onload="this.onload=null;this.rel='stylesheet'">`,
    `<noscript><link rel="stylesheet" href="${href}"></noscript>`,
    '<!-- /critical-css -->',
  ].join('\n  ');
  fs.writeFileSync(file, src.replace(LINK, block));
  return critical.length;
}

const files = process.argv.slice(2).length
  ? process.argv.slice(2).map((f) => path.resolve(f))
  : fs.readdirSync(ROOT).filter((f) => f.endsWith('.html')).map((f) => path.join(ROOT, f));
const full = fs.statSync(path.join(ROOT, 'assets', 'styles.css')).size;
for (const f of files) {
  const n = await inline(f);
  if (n) console.log(`${path.basename(f)}: ${(n / 1024).toFixed(1)} KB of ${(full / 1024).toFixed(1)} KB inlined`);
}
