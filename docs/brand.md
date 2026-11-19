# Line of Blue: the mark (version A)

Agreed 19 November 2026. Source of truth: `app/splash.html`.

- **Page:** pure black, `#000000`. Nothing else on the page.
- **Line:** bright blue `#3d9bff`, stroke width 1.6 px, round caps and joins, no fill.
- **Form:** one continuous stroke. The pen goes down at the far left edge, writes **"line of blue"** in plain, upright lowercase without lifting, and leaves at the far right edge. The word gaps run along the line itself. The i is left undotted, because a dot would need the pen lifted.
- **Meaning:** plain, fair, just and simple. Upright rather than flowing script.
- **Size:** small and delicate. Scale factor 1.7 on desktop and 1.3 below 600 px wide, against the path units below. The line sits at half the page height.
- **Motion:** draws left to right over 4.2 s (ease in and out). No motion when the viewer prefers reduced motion.

## Path
Units: baseline y = 0, x-height 12.5, ascenders 25, descender 12, word width 119. The page prefixes `M0 y L x0 y`, scales and offsets every coordinate pair, and suffixes `L width y`. Copy the `WORD` string from `app/splash.html` exactly; do not redraw it.

## Rejected options (kept for reference)
- `app/splash-fonts.html`: ten typefaces, structural to flowing.
- `app/splash-options.html`: version A beside version 8 (a Sacramento-style single stroke).
