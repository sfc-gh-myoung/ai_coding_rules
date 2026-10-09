# Vendored assets

- `alpinejs-3.14.8.min.js` — Alpine.js v3.14.8 (MIT), fetched from
  `https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js`.
  `render_report` inlines this file into the generated HTML so the report's
  tabs, filters, and tables work with no network access. The Vega chart
  libraries intentionally remain on the CDN (heavy); charts degrade to a
  fallback note when the CDN is unreachable.
