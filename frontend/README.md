# StratScout Frontend

React + TypeScript frontend for the StratScout competitive intelligence platform.

## Features

- **Dashboard**: Overview of competitors, opportunities, and metrics
- **Competitor Deep Dive**: Detailed analysis of individual competitors
- **Gap Analysis**: Market opportunities and competitive gaps
- **Predictions**: AI-powered campaign performance predictions
- **Scout AI**: Conversational AI assistant for competitive intelligence

## Tech Stack

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling
- **Zustand**: State management
- **React Router**: Navigation
- **Recharts**: Data visualization
- **Lucide React**: Icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` folder.

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── MetricCard.tsx
│   │   └── CompetitorCard.tsx
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx
│   │   ├── CompetitorDeepDive.tsx
│   │   ├── GapAnalysis.tsx
│   │   ├── Predictions.tsx
│   │   └── Scout.tsx
│   ├── store/            # State management
│   │   └── useStore.ts
│   ├── lib/              # Utilities
│   │   └── api.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html            # HTML template
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

## Pages

### Dashboard (`/dashboard`)
- Overview metrics (competitors, campaigns, opportunities)
- Top opportunities cards
- Competitor cards with quick access

### Competitor Deep Dive (`/competitor/:id`)
- Detailed competitor information
- Messaging strategy analysis
- Creative strategy analysis
- Recent analyses timeline

### Gap Analysis (`/gaps`)
- Market opportunities by category
- Priority-based filtering
- Detailed gap descriptions
- Confidence scores

### Predictions (`/predictions`)
- Campaign performance predictions
- Reach, engagement, and duration forecasts
- Comparative charts
- Confidence scores

### Scout AI (`/scout`)
- Conversational AI interface
- Natural language queries
- Suggested questions
- Real-time responses

## API Integration

The frontend connects to the backend API via the `api.ts` client:

```typescript
import { api } from '@/lib/api'

// Get competitors
const competitors = await api.getCompetitors()

// Send chat message
const response = await api.sendMessage('Show me top campaigns')
```

Configure the API URL in `.env`:

```
VITE_API_URL=https://your-api-gateway-url.com/api
```

## State Management

Uses Zustand for global state:

```typescript
import { useStore } from '@/store/useStore'

function MyComponent() {
  const { competitors, setCompetitors } = useStore()
  // ...
}
```

## Styling

Uses Tailwind CSS with custom configuration:

- Primary color: Blue (`primary-*`)
- Custom components: `.card`, `.btn-primary`, `.btn-secondary`
- Responsive design with mobile-first approach

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Adding a New Page

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/Layout.tsx`

### Adding a New API Endpoint

1. Add method to `src/lib/api.ts`
2. Add TypeScript types to `src/types/index.ts`
3. Use in components with error handling

## Deployment

### AWS S3 + CloudFront

The CDK infrastructure automatically sets up:
- S3 bucket for static hosting
- CloudFront distribution
- Automatic deployment on build

```bash
# Build
npm run build

# Deploy (via CDK)
cd ../infrastructure
cdk deploy
```

### Environment Variables

Production environment variables:

```
VITE_API_URL=https://your-api-gateway.execute-api.us-east-1.amazonaws.com/prod
VITE_ENV=production
```

## Mock Data

For development without backend:

1. Create `src/lib/mockData.ts`
2. Add mock responses
3. Toggle in `src/lib/api.ts`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting with React.lazy()
- Image optimization
- Lazy loading for charts
- Memoization for expensive computations

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Proprietary - StratScout MVP

---

**Last Updated**: March 8, 2026
