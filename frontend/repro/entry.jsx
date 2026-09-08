/**
 * Reproduction harness: renders the REAL <App /> into a jsdom document and
 * drives a real login against the running backend, so we can see the route the
 * app actually lands on instead of reasoning about it.
 */
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from '../src/App.jsx';

export const errors = [];

const origError = console.error;
console.error = (...args) => {
  errors.push(args.map((a) => (a && a.stack) || String(a)).join(' '));
  origError(...args);
};

export async function run({ targetPath = '/' } = {}) {
  const container = document.createElement('div');
  container.id = 'root';
  document.body.appendChild(container);

  if (targetPath !== '/') {
    window.history.pushState({}, '', targetPath);
  }

  const root = createRoot(container);
  root.render(React.createElement(App));

  await wait(600);
  return { root, container };
}

export function wait(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

/** React ignores direct .value writes on controlled inputs; use the native setter. */
export function setValue(el, value) {
  const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
  setter.call(el, value);
  el.dispatchEvent(new window.Event('input', { bubbles: true }));
}

export function findByText(container, selector, text) {
  return [...container.querySelectorAll(selector)].find((el) =>
    (el.textContent || '').trim().toLowerCase().includes(text.toLowerCase())
  );
}

export function snapshot(container) {
  const text = (container.textContent || '').replace(/\s+/g, ' ').trim();
  return {
    href: window.location.pathname,
    headings: [...container.querySelectorAll('h1,h2,h3')].map((h) => h.textContent.trim()),
    hasLoginForm: !!container.querySelector('input[type="password"]'),
    text: text.slice(0, 400),
  };
}
