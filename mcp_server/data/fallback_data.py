"""
Fallback UI pattern dataset used when the Mobbin scraper is unavailable.
Contains 12 diverse patterns covering common UI types and styles.
"""

FALLBACK_PATTERNS: list[dict] = [
    {
        "type": "login",
        "style": "fintech",
        "platform": "mobile",
        "layout": "centered card",
        "components": ["email input", "password input", "login button", "forgot password link", "social login"],
        "notes": "Minimal trust-focused design. Blue/navy tones, rounded corners, subtle drop shadows. Biometric auth badge increases trust signal.",
        "references": [
            "https://mobbin.com/screens/revolut-login",
            "https://mobbin.com/screens/n26-login",
        ],
    },
    {
        "type": "login",
        "style": "minimal",
        "platform": "web",
        "layout": "split screen",
        "components": ["email input", "password input", "CTA button", "brand illustration"],
        "notes": "Left panel: large hero illustration. Right panel: clean login form. White background, single accent color CTA.",
        "references": [
            "https://mobbin.com/screens/notion-login",
            "https://mobbin.com/screens/linear-login",
        ],
    },
    {
        "type": "dashboard",
        "style": "saas analytics",
        "platform": "web",
        "layout": "sidebar + main content",
        "components": ["nav sidebar", "KPI cards", "line chart", "bar chart", "data table", "filter controls"],
        "notes": "Dark sidebar with icon navigation. KPI cards at top with trend indicators. Charts use vibrant accent colors on dark/light backgrounds.",
        "references": [
            "https://mobbin.com/screens/mixpanel-dashboard",
            "https://mobbin.com/screens/amplitude-dashboard",
        ],
    },
    {
        "type": "onboarding",
        "style": "consumer app",
        "platform": "mobile",
        "layout": "paginated steps",
        "components": ["progress indicator", "illustration", "headline", "subtext", "next button", "skip link"],
        "notes": "3-5 step carousel onboarding. Full-screen illustrations per step. Bottom-anchored primary CTA. Light, energetic color palette.",
        "references": [
            "https://mobbin.com/screens/duolingo-onboarding",
            "https://mobbin.com/screens/headspace-onboarding",
        ],
    },
    {
        "type": "profile",
        "style": "social",
        "platform": "mobile",
        "layout": "header + scrollable feed",
        "components": ["avatar", "cover photo", "username", "bio", "stats row (followers/following)", "post grid", "follow button"],
        "notes": "Hero cover image. Circular avatar overlapping header. Stats displayed inline. Content grid below the fold.",
        "references": [
            "https://mobbin.com/screens/instagram-profile",
            "https://mobbin.com/screens/twitter-profile",
        ],
    },
    {
        "type": "todo",
        "style": "minimal productivity",
        "platform": "mobile",
        "layout": "list view",
        "components": ["task input bar", "task list items", "checkbox", "swipe actions", "category pills", "FAB add button"],
        "notes": "Ultra-minimal. White canvas, thin typography. Swipe-left to delete, swipe-right to complete. Color-coded priority badges.",
        "references": [
            "https://mobbin.com/screens/things3-tasks",
            "https://mobbin.com/screens/todoist-mobile",
        ],
    },
    {
        "type": "checkout",
        "style": "ecommerce",
        "platform": "mobile",
        "layout": "stepper form",
        "components": ["step indicator", "address form", "payment form", "order summary", "place order CTA", "trust badges"],
        "notes": "Single-column step flow. Persistent order summary at the bottom. Trust signals (SSL badge, return policy) near CTA to reduce anxiety.",
        "references": [
            "https://mobbin.com/screens/shopify-checkout",
            "https://mobbin.com/screens/amazon-checkout",
        ],
    },
    {
        "type": "home",
        "style": "fintech",
        "platform": "mobile",
        "layout": "scrollable feed with hero balance card",
        "components": ["balance card", "quick actions row", "recent transactions list", "bottom tab bar", "notification bell"],
        "notes": "Prominent balance display on gradient card. Color-coded transaction items (red/green). Quick-send shortcuts as icon grid.",
        "references": [
            "https://mobbin.com/screens/cash-app-home",
            "https://mobbin.com/screens/paypal-home",
        ],
    },
    {
        "type": "settings",
        "style": "ios native",
        "platform": "mobile",
        "layout": "grouped list sections",
        "components": ["section headers", "toggle switches", "disclosure arrows", "destructive action (red)", "account info row"],
        "notes": "iOS-style grouped table view. Clear section labels. Toggles for binary settings. Destructive items (delete account) in red at the bottom.",
        "references": [
            "https://mobbin.com/screens/ios-settings",
        ],
    },
    {
        "type": "landing page",
        "style": "saas startup",
        "platform": "web",
        "layout": "hero + features + pricing + footer",
        "components": ["nav bar", "hero headline + CTA", "social proof logos", "feature cards", "pricing table", "FAQ accordion", "footer"],
        "notes": "Bold hero with gradient background. Social proof logos in grayscale. Alternating feature sections (text left/right). Clear 3-tier pricing with highlighted recommended plan.",
        "references": [
            "https://mobbin.com/screens/stripe-landing",
            "https://mobbin.com/screens/vercel-landing",
        ],
    },
    {
        "type": "search",
        "style": "travel",
        "platform": "mobile",
        "layout": "search header + filtered results",
        "components": ["sticky search bar", "filter chips", "result cards (image + price)", "map toggle", "sort dropdown"],
        "notes": "Full-width search at top. Horizontal scrollable filter row. Card-based results with photo, rating, and price. Floating map view toggle.",
        "references": [
            "https://mobbin.com/screens/airbnb-search",
            "https://mobbin.com/screens/booking-search",
        ],
    },
    {
        "type": "empty state",
        "style": "minimal",
        "platform": "mobile",
        "layout": "centered illustration",
        "components": ["illustration", "headline", "subtext", "primary action CTA"],
        "notes": "Friendly illustration matching app brand. Clear messaging about what's missing and how to get started. Single action CTA.",
        "references": [
            "https://mobbin.com/screens/slack-empty-state",
        ],
    },
]
