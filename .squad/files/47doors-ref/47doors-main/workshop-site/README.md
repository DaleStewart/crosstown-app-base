# 47 Doors Workshop Companion Site

A visual, tab-based React + Tailwind CSS website serving as an executive briefing and workshop companion for the **Trustworthy Agentic AI in Higher Education** workshop.

## Overview

This site presents the 47 Doors architecture — a three-agent pipeline that transforms how universities handle student support queries. It demonstrates how trust is built architecturally, not just through policy.

## Design Principles

- **Microsoft Fluent 2 visual language**: Generous whitespace, calm typography, restrained color
- **Primary palette**: Microsoft blue (#0078D4), neutral gray (#F3F2F1), dark text (#323130)
- **Accent**: Indiana University crimson (#990000) used sparingly
- **Text-light, visually rich**: Icons, diagrams, callout cards
- **Accessible**: Keyboard navigable, semantic HTML, high contrast, WCAG AA compliant

## Tech Stack

- React 18 with TypeScript
- Tailwind CSS 3.4+
- Vite 5 as build tool
- Heroicons for icons
- No external component libraries

## Local Development

### Prerequisites

- Node.js 18+ and npm

### Install Dependencies

```bash
cd workshop-site
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Structure

```
workshop-site/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main app with tab navigation
│   ├── index.css             # Global styles and Tailwind imports
│   ├── components/           # Reusable components
│   │   ├── TabNavigation.tsx
│   │   ├── CollapsibleNotes.tsx
│   │   ├── CalloutCard.tsx
│   │   ├── DiagramSVG.tsx
│   │   └── Footer.tsx
│   └── tabs/                 # Tab content components
│       ├── Overview.tsx
│       ├── TheProblem.tsx
│       ├── ChatbotsToAgents.tsx
│       ├── TrustBoundaries.tsx
│       ├── Architecture.tsx
│       ├── VoiceAccessibility.tsx
│       ├── DemoWalkthrough.tsx
│       ├── ResponsibleAI.tsx
│       ├── ReuseAcrossCampus.tsx
│       └── YourFirstAgent.tsx
└── public/                   # Static assets
```

## Features

### 10 Workshop Tabs

1. **Overview** — Introduction and workshop framing
2. **The Problem (47 Front Doors)** — The student support routing problem
3. **From Chatbots to Agents** — Distinguishing agentic AI from traditional chatbots
4. **Trust & Boundaries** — Constitutional principles and governance
5. **Architecture (Three-Agent Pattern)** — Technical architecture deep dive
6. **Voice & Accessibility** — Real-time voice interaction via WebRTC
7. **Live Demo Walkthrough** — Step-by-step voice demo flow
8. **Responsible AI in Practice** — Concrete governance and audit trails
9. **Reuse Across Campus** — Institutional customization and deployment
10. **Your First Agent** — Interactive exercise for attendees

### Keyboard Navigation

- **Tab/Shift+Tab**: Navigate between tabs and interactive elements
- **Arrow keys**: Move between tabs
- **Enter/Space**: Activate tabs
- **Escape**: Collapse expanded notes

## Accessibility

- Semantic HTML with proper ARIA labels
- Keyboard navigable throughout
- High contrast text (WCAG AA 4.5:1 ratio)
- Screen reader friendly
- Accessible diagrams with figure/figcaption

## License

Part of the 47 Doors project — Trustworthy Agentic AI for Higher Education.
