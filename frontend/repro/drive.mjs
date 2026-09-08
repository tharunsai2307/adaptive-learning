/**
 * Drives the real app in jsdom against the live backend.
 * Usage: node repro/drive.mjs [startPath]
 */
import { JSDOM } from 'jsdom';

const ORIGIN = 'http://127.0.0.1:5173';
const startPath = process.argv[2] || '/';

const dom = new JSDOM('<!doctype html><html><body class="bg-slate-900"><div id="root"></div></body></html>', {
  url: ORIGIN + startPath,
  pretendToBeVisual: true,
  runScripts: 'outside-only',
});

const { window } = dom;

// Simulate a cross-origin iframe where the browser blocks localStorage.
if (process.env.BLOCK_STORAGE === '1') {
  Object.defineProperty(window, 'localStorage', {
    configurable: true,
    get() { throw new window.DOMException('Access is denied for this document.', 'SecurityError'); },
  });
}

// Install browser globals BEFORE importing the app bundle.
globalThis.window = window;
globalThis.document = window.document;
Object.defineProperty(globalThis, 'navigator', { value: window.navigator, configurable: true, writable: true });
Object.defineProperty(globalThis, 'location', { value: window.location, configurable: true, writable: true });
globalThis.history = window.history;
globalThis.HTMLElement = window.HTMLElement;
globalThis.HTMLInputElement = window.HTMLInputElement;
globalThis.HTMLTextAreaElement = window.HTMLTextAreaElement;
globalThis.Event = window.Event;
globalThis.Node = window.Node;
globalThis.getComputedStyle = window.getComputedStyle;
globalThis.requestAnimationFrame = window.requestAnimationFrame;
globalThis.cancelAnimationFrame = window.cancelAnimationFrame;
globalThis.XMLHttpRequest = window.XMLHttpRequest;
try {
  Object.defineProperty(globalThis, 'localStorage', {
    get: () => window.localStorage, configurable: true,
  });
} catch { /* leave undefined */ }
globalThis.IS_REACT_ACT_ENVIRONMENT = true;

// Simulate /api/auth/me failing (network blip, 5xx, proxy hiccup).
if (process.env.FAIL_ME === '1') {
  const origOpen = window.XMLHttpRequest.prototype.open;
  const origSend = window.XMLHttpRequest.prototype.send;
  window.XMLHttpRequest.prototype.open = function (m, u, ...r) { this.__url = u; return origOpen.call(this, m, u, ...r); };
  window.XMLHttpRequest.prototype.send = function (...a) {
    if (this.__url && String(this.__url).includes('/api/auth/me')) {
      setTimeout(() => this.dispatchEvent(new window.ProgressEvent('error')), 5);
      return;
    }
    return origSend.apply(this, a);
  };
}

const entry = await import('./dist/entry.js');

console.log(`\n=== jsdom harness: ${ORIGIN}${startPath} ===`);
console.log(`  localStorage writable? ${(() => { try { window.localStorage.setItem('__t', '1'); window.localStorage.removeItem('__t'); return 'yes'; } catch (e) { return 'no (' + e.name + ')'; } })()}`);

const { root, container } = await entry.run({ targetPath: startPath });
await entry.wait(500);

let snap = entry.snapshot(container);
console.log(`\n--- after initial load ---`);
console.log(`  path        : ${snap.href}`);
console.log(`  headings    : ${JSON.stringify(snap.headings)}`);
console.log(`  login form? : ${snap.hasLoginForm}`);

if (!snap.hasLoginForm) {
  console.log('\nNo login form rendered. Nothing to drive.');
  console.log(`  text: ${snap.text}`);
  process.exit(0);
}

// Fill the login form
const email = container.querySelector('input[type="email"]');
const password = container.querySelector('input[type="password"]');
if (!email || !password) {
  console.log('  !! could not find email/password inputs');
  process.exit(1);
}
entry.setValue(email, 'demo@adaptivelearn.com');
entry.setValue(password, 'demo123');
await entry.wait(150);

const submit = [...container.querySelectorAll('button[type="submit"]')][0];
console.log(`\n--- submitting login (button: "${submit?.textContent.trim()}") ---`);
submit.dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));

for (const ms of [800, 1200, 1500]) {
  await entry.wait(ms);
  snap = entry.snapshot(container);
  console.log(`  t+${ms}ms  path=${snap.href}  loginForm=${snap.hasLoginForm}  headings=${JSON.stringify(snap.headings)}`);
}

console.log('\n--- verdict ---');
if (snap.href === '/' && snap.hasLoginForm) {
  console.log('  REPRODUCED: bounced back to the login page');
} else {
  console.log(`  login held; landed on ${snap.href}`);
}

const shown = container.querySelector('.bg-red-500\\/20');
if (shown) console.log(`  on-screen error banner: "${shown.textContent.trim()}"`);

if (entry.errors.length) {
  console.log(`\n--- ${entry.errors.length} console.error(s) ---`);
  entry.errors.slice(0, 6).forEach((e, i) => console.log(`  [${i}] ${e.slice(0, 400)}`));
} else {
  console.log('\n  no console errors captured');
}

console.log(`\n--- final page text ---\n  ${snap.text.slice(0, 300)}`);
root.unmount();
process.exit(0);
