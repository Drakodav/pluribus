# Bundled / Optimized Assets (`src/assets/`)

Files in this directory are meant to be imported directly into Astro and React components:

```astro
---
import { Image } from "astro:assets";
import brandLogo from "@/assets/branding/logo.svg";
---

<Image src={brandLogo} alt="Luxe Bear Logo" />
```

## Recommended Structure

```text
src/assets/
├── branding/    # Logos, badges, and watermark graphics used in UI components
└── images/      # Static illustrations, background vectors, and decorative UI artwork
```

## Guidelines

- Astro will process, compress, hash, and generate responsive `srcset` variants for raster images (`.png`, `.jpg`, `.webp`, `.avif`) placed here when passed to Astro's `<Image />` component.
- For favicon and root-level assets, use `public/` instead.
