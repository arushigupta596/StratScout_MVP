export const mockData = {
  user: {
    company: "Bella Vita Organic",
    website: "bellavitaorganic.com",
    industry: "D2C Beauty & Personal Care"
  },
  onboarding: {
    competitors: [
      { name: "Mamaearth", id: "mamaearth", selected: true, logo: "M" },
      { name: "Plum", id: "plum", selected: true, logo: "P" },
      { name: "The Derma Co", id: "dermaco", selected: true, logo: "D" },
      { name: "Minimalist", id: "minimalist", selected: false, logo: "m" },
      { name: "WOW Skin Science", id: "wow", selected: false, logo: "W" },
    ]
  },
  dashboard: {
    alerts: [
      {
        id: 1,
        type: "urgent",
        title: "Urgent Opportunity Detected!",
        description: "Mamaearth launched winter campaign on Jan 15. 40% increase in ad spend detected, targeting 'dry skin winter care'.",
        action: "Launch counter-campaign by Jan 25 targeting 'winter skincare for sensitive skin'"
      }
    ],
    marketPosition: [
      { name: "Bella Vita", ads: 12, color: "#6366f1" },
      { name: "Mamaearth", ads: 23, color: "#cbd5e1", isLeader: true },
      { name: "Plum", ads: 18, color: "#cbd5e1" },
      { name: "Derma Co", ads: 15, color: "#cbd5e1" }
    ],
    porter: [
        { label: "Competitive Rivalry", score: 8, max: 10, level: "High" },
        { label: "Buyer Power", score: 7, max: 10, level: "High" },
        { label: "Threat of New Entrants", score: 5, max: 10, level: "Medium" },
        { label: "Supplier Power", score: 4, max: 10, level: "Low-Med" },
        { label: "Substitute Threat", score: 6, max: 10, level: "Medium" }
    ]
  },
  deepDive: {
    competitor: "Mamaearth",
    ads: [
        { id: 1, date: "Jan 15", type: "img" },
        { id: 2, date: "Jan 18", type: "img" },
        { id: 3, date: "Jan 20", type: "img" },
        { id: 4, date: "Jan 22", type: "video" }
    ],
    analysis: {
        visualTheme: "Lifestyle (70%) vs Product-focused (30%)",
        visualEvidence: "14/20 ads show people using products",
        colors: "Earthy tones (green, brown, beige)",
        colorsEvidence: "85% of ads use natural color schemes",
        target: "Women 25-40, mothers with kids",
        targetEvidence: "12/20 ads feature mothers, 8 mention 'baby safe'"
    },
    messaging: {
        keywords: [
            { text: "natural", count: 18 },
            { text: "toxin-free", count: 15 },
            { text: "safe for babies", count: 12 },
            { text: "dermatologist tested", count: 10 }
        ],
        primaryHook: "Safety + Natural ingredients",
        secondaryHook: "Affordable luxury",
        cta: [
            { text: "Urgency ('Limited time')", pct: 40 },
            { text: "Social Proof ('10M+ customers')", pct: 35 },
            { text: "Curiosity ('Discover the secret')", pct: 25 }
        ]
    },
    gaps: [
        { title: "Zero LinkedIn presence", impact: "B2B/Corporate gifting market untapped", size: "8.5k monthly searches" },
        { title: "Not targeting 'vegan skincare'", impact: "Trending +45% YoY", stat: "Only 1 of 20 ads mentions 'vegan'" },
        { title: "Weak on educational content", impact: "Opportunity: Build authority", stat: "5% of ads educational vs 20% industry avg" }
    ]
  },
  strategy: {
    comparison: [
        { metric: "Ad Volume", you: "12/month", comp: "19/month", status: "danger" },
        { metric: "Platforms", you: "FB, Insta", comp: "FB, IG, YT", status: "neutral" },
        { metric: "Primary Hook", you: "Luxury", comp: "Safety", status: "neutral" },
        { metric: "Price Mention", you: "60%", comp: "35%", status: "success" },
        { metric: "Video Ads", you: "25%", comp: "45%", status: "danger" },
        { metric: "UGC Content", you: "10%", comp: "30%", status: "danger" }
    ],
    recommendations: [
        { title: "Increase ad volume", reason: "You're running 37% fewer ads.", action: "Increase to 18-20 ads/month", impact: "+25% brand visibility" },
        { title: "Add more video content", reason: "Competitors use 45% video, you use 25%.", action: "Create 3-5 video ads this month", impact: "3x engagement boost" },
        { title: "Differentiate messaging", reason: "Your 'luxury' positioning overlaps with Plum.", action: "Shift to 'Affordable luxury + sustainability'", impact: "Capture undecided buyers" }
    ]
  }
};
