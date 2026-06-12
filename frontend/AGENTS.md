<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->
# Frontend Development Guidelines – Trauma Care Dashboard

## 1. Mission
Build a Next.js 14+ trauma care dashboard that connects patients, caregivers, and healthcare providers with real-time data, secure communication, and empathetic AI guidance. The frontend must be:
- modular
- responsive
- accessible (WCAG AA)
- designed with trauma-informed principles
- fast (90+ Lighthouse score)
- beautiful and calming

## 2. UI Stack

### Framework
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4 + Shadcn/UI
- **Animation**: Framer Motion
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (react-query)
- **Forms**: React Hook Form + Zod
- **Icons**: Lucide React

### Component Library
Use **Shadcn/UI** components as the foundation, with custom styling:
- ✅ All core components (Button, Card, Input, Table, Tabs, Dialog, etc.)
- ✅ Use custom config from `components.json`
- ❌ Do not invent or write from scratch unless absolutely necessary

## 3. Design System

### Colors

#### Primary (Trauma Care)
Use calming, trustworthy colors:
```typescript
// Trauma care palette
--color-primary-bg: #0a192f;
--color-primary-card: #050a14;
--color-primary-text: #f0f0f0;

// Secondary + Accents
--color-accent: #2a62ff;
--color-success: #28a745;
--color-warning: #ffc107;
--color-danger: #dc3545;
```

#### Calm Palette (Trauma-informed)
```typescript
// Calm / therapeutic
--color-calm-100: #e8f4f8;  // soft blue
--color-calm-500: #60a5fa;  // gentle blue
--color-calm-900: #1e3a5f;  // deep trustworthy

// Soothing tones
--color-soothing-500: #7dd3fc;  // light sky
--color-soothing-900: #0f766e;  // sea green

// Warm support
--color-warm-500: #fca5a5;  // soft red
--color-warm-900: #b91c1c;  // gentle warmth
```

#### Color Usage Rules
- ✅ 60% neutral backgrounds
- ✅ 30% calm accents
- ✅ 10% emotional highlights (use sparingly)
- ❌ No harsh bright colors (no pure white, no pure black)
- ❌ No neon or high-saturation colors
- ❌ Avoid red for error states unless necessary (use yellow/amber instead)

### Typography
```typescript
// Headings - Inter or Sora (if available)
font-family: 'Inter', sans-serif; 
font-weight: 600; 
font-size: 1.875rem (30px);

// Body - system font
font-family: system-ui, -apple-system, sans-serif;
font-size: 1rem (16px);
line-height: 1.6; 

// Trauma-informed design
- Increase font size (16px minimum)
- Increase line height (1.6+) 
- Use generous letter spacing
- Avoid all caps (except UI labels)
```

### Layout & Spacing
- Use **rem** units only (no px)
- Tailwind spacing scale only
- Minimum 24px (1.5rem) between interactive elements
- Generous whitespace
- Maximum 50–70 characters per line

### Typography System (Tailwind)
```typescript
<h1 className="text-3xl font-semibold">Page Title</h1>
<h2 className="text-2xl font-medium">Section Title</h2>
<h3 className="text-xl font-medium">Card Title</h3>
<p className="text-base leading-relaxed">Body text</p>
<p className="text-sm text-muted-foreground">Helper text</p>
```

## 4. File Structure (Next.js 14 App Router)
```
src/
├── app/                    # App Router
│   ├── (auth)/
│   ├── patient/            # Patient routes
│   ├── caregiver/         # Caregiver routes
│   ├── provider/           # Provider routes
│   ├── admin/              # Admin routes
│   ├── api/                # API routes
│   └── layout.tsx
│   └── page.tsx

├── components/
│   ├── ui/                 # Shadcn components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── layout/             # Layout components
│   │   ├── AppHeader.tsx
│   │   ├── Sidebar.tsx
│   │   ├── MobileNav.tsx
│   │   ├── Footer.tsx
│   │   └── DashboardShell.tsx
│   ├── patient/
│   │   ├──forms/ 
│   │   ├──PatientRecordCard.tsx
│   │   └──HealthDashboard.tsx
│   ├── caregiver/
│   │   ├──NotificationsPanel.tsx
│   │   └──CaregiverSummary.tsx
│   ├── provider/
│   │   ├──TreatmentPlanCard.tsx
│   │   └──ProviderDashboard.tsx
│   ├── admin/
│   │   ├── UserManagementTable.tsx
│   │   └── RoleManagement.tsx
│   ├── common/             # Reusable across app
│   │   ├── ProtectedRoute.tsx
│   │   ├── FormInput.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorBoundary.tsx
│   └── trauma/             # Trauma-specific components
│       ├── TraumaIndicators.tsx
│       ├── EmergencyGuide.tsx
│       └── SupportResources.tsx

├── lib/
│   ├── api.ts              # API client (axios)
│   ├── utils.ts            # Helper functions
│   ├── validation.ts       # Zod schemas
│   ├── auth.ts             # Auth utilities
│   ├── consent.ts          # Consent management
│   ├── notifications.ts    # Notification logic
│   └── trauma-guidance.ts  # AI trauma guidance

├── stores/ 
│   ├── auth.ts             # Auth store (Zustand)
│   ├── patient.ts          # Patient state
│   ├── notifications.ts    # Notifications store
│   ├── socket.ts           # WebSocket
│   └── websocket.ts 

├── hooks/
│   ├── useAuth.ts          # Auth hook
│   ├── useConsent.ts       # Consent hook
│   ├── useNotifications.ts
│   └── useRealtime.ts

├── public/
├── styles/
├── types/
└── middleware.ts
```

## 5. Route Structure & Protected Routes

```typescript
// app/
/patient/dashboard      # Patient dashboard  
/admin/dashboard        
/auth/login
/auth/signup
/auth/consent           # Consent flow

// Protected routes
if user is not authenticated:
  redirect to /auth/login

if user is authenticated but no consent:
  redirect to /auth/consent

if user has consent:
  allow access
```





