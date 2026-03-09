# StratScout

**AI-powered competitive intelligence for D2C brands.**

StratScout helps brands monitor competitor ad campaigns, decode marketing strategies, and surface actionable opportunities — all in one place.

---

## What It Does

StratScout walks users through a 5-stage flow:

1. **Onboarding** — Auto-detects your company details and lets you select up to 3 competitors to track
2. **Dashboard** — Market overview with key alerts, ad volume share, and Porter's Five Forces analysis
3. **Deep Dive** — Per-competitor breakdown: ad creatives, messaging strategy, keyword analysis, campaign timing, and competitive gaps
4. **Strategy Comparison** — Side-by-side view of your strategy vs. competitor averages with AI recommendations
5. **Export** — Download reports (PDF, CSV, PPTX) and configure ongoing alerts

---

## Tech Stack

- **React 19** with Vite
- **Framer Motion** — page transitions and animations
- **Recharts** — market share bar charts
- **Lucide React** — icons
- **clsx** — conditional classNames
- **Tailwind CSS** (via index.css utility classes)

---

## Getting Started

```bash
npm install
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

### Other Commands

| Command | Description |
|---|---|
| `npm run build` | Production build |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |

---

## Project Structure

```
src/
├── App.jsx       # All stage components and main app logic
├── data.js       # Mock data (competitors, alerts, market stats)
├── App.css       # Component styles
└── index.css     # Global styles and utility classes
```

---

## Notes

- All data is currently mocked via `src/data.js` — no backend required to run
- The demo is scoped to a D2C skincare use case (Bella Vita vs. Mamaearth, WOW, etc.)
