# Static Public Assets (`public/`)

Files in this directory are served directly at the web root (`/`) without processing or bundling by Astro/Vite.

## Recommended Structure

```text
public/
├── favicon.svg          # Primary SVG favicon (served at /favicon.svg)
├── favicon.ico          # Fallback ICO favicon (served at /favicon.ico)
├── branding/            # Static brand marks & logos
│   ├── logo.svg         # Primary navbar & header vector logo (/branding/logo.svg)
│   ├── logo-dark.svg    # Dark-mode logo variant (optional)
│   └── logo-mark.svg    # Isolated icon/mark (optional)
├── icons/               # PWA icons & app shortcuts
│   ├── icon-192.png
│   ├── icon-512.png
│   └── apple-touch-icon.png
└── site.webmanifest     # Optional PWA manifest
```

## Guidelines

- **Use `public/` for**: Favicons, fixed root URLs (`robots.txt`, `site.webmanifest`), and logos that must be referenced via raw URLs (e.g. OpenGraph tags, transactional emails, or external embeds).
- **Use `src/assets/` for**: Content images or UI assets imported directly into `.astro` or `.tsx` components that should be optimized, resized, or hashed by Astro's asset pipeline (`<Image src={...} />`).
- **Use EmDash Media Library for**: Client-managed photos (occasions hero photos, product gallery uploads, blog post covers).
