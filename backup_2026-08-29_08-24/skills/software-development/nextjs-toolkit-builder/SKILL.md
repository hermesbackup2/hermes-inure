---
name: nextjs-toolkit-builder
description: "Build and deploy multi-tool Next.js dashboard apps."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Next.js, React, TypeScript, Dashboard, Deployment]
---

# Next.js Toolkit Builder

Build production-ready multi-tool dashboard applications with Next.js, React 19, TypeScript, Tailwind CSS, and shadcn-style UI. Deploy to Vercel/Netlify as static export.

## When to Use

- User asks to build a dashboard, utility app, or tool collection
- User asks to create a web app with multiple independent tools/features
- User asks for a privacy-focused or client-side-only web application
- User asks to scaffold a Next.js project with specific tools
- User asks to deploy a static site to Vercel/Netlify

## Prerequisites

- `node` v18+ and `npm` or `bun`
- Git and GitHub account (for deployment)
- Disk space: ~500MB for node_modules

## Project Structure

```
project-name/
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── next.config.js
├── .prettierrc
├── .gitignore
├── README.md
└── src/
    ├── app/
    │   ├── layout.tsx        # Root layout (dark mode, fonts)
    │   ├── page.tsx          # Dashboard home
    │   ├── globals.css       # CSS variables, glassmorphism
    │   └── [tool]/page.tsx   # One route per tool
    ├── components/
    │   ├── Sidebar.tsx       # Responsive navigation
    │   ├── ToolPage.tsx      # Page wrapper with animation
    │   ├── ui/               # Shared UI (Card, Button, Input, Textarea, Badge)
    │   └── tools/            # One component per tool
    ├── lib/                  # Utility functions per tool
    ├── hooks/                # Shared hooks (useCopyToClipboard, useLocalStorage)
    └── types/                # TypeScript interfaces
```

## Procedure

### 1. Scaffold Project

```bash
mkdir project-name && cd project-name
```

Create `package.json` with dependencies:
- `next`, `react`, `react-dom` (latest)
- `framer-motion`, `lucide-react`
- `clsx`, `tailwind-merge`
- Dev: `typescript`, `tailwindcss`, `postcss`, `autoprefixer`, `prettier`

```bash
npm install   # or bun install
```

### 2. Configuration Files

**next.config.js** — static export for Vercel/Netlify:
```js
module.exports = { output: 'export', images: { unoptimized: true }, trailingSlash: true };
```

**tailwind.config.js** — dark theme with CSS variable colors.

**globals.css** — CSS custom properties for dark glassmorphism theme.

### 3. Core Components

1. **Sidebar.tsx** — responsive nav with category grouping, mobile hamburger menu
2. **ToolPage.tsx** — page wrapper with Framer Motion fade-in animation
3. **ui/** — Card, Button, Input, Textarea, Badge (shadcn-style with cn() utility)

### 4. Tool Components (per tool)

Each tool gets:
- `src/components/tools/ToolName.tsx` — React component
- `src/app/toolname/page.tsx` — dynamic import with `ssr: false`
- `src/lib/toolname.ts` — utility functions
- TypeScript types in `src/types/index.ts`

Pattern for page route (avoids SSR issues):
```tsx
'use client';
import dynamic from 'next/dynamic';
const Component = dynamic(() => import('@/components/tools/ToolName'), { ssr: false });
export default function Page() { return <Component />; }
```

### 5. Key Patterns

- **Client-only**: All tool components use `'use client'`
- **No SSR**: Use `dynamic(() => import(...), { ssr: false })` for browser-API tools
- **Copy to clipboard**: Shared `useCopyToClipboard` hook
- **Crypto**: Use `crypto.getRandomValues()` never `Math.random()`
- **Hashing**: Use Web Crypto API (`crypto.subtle.digest`)
- **Animations**: Framer Motion for page transitions and progress bars
- **Responsive**: Mobile-first with lg: breakpoint for sidebar

### 6. Build & Deploy

**Local dev:**
```bash
npm run dev    # http://localhost:3000
```

**Build for static export:**
```bash
npm run build  # Output in out/
```

**Deploy to Vercel:**
1. Push to GitHub
2. Import in Vercel
3. Framework: Next.js (auto-detected)
4. Output directory: `out`
5. Deploy

**Deploy to Netlify:**
1. Push to GitHub
2. Import in Netlify
3. Build: `npm run build`
4. Publish: `out`

### 7. Git Setup & Push

```bash
git init && git add -A
git config user.email "user@users.noreply.github.com"
git config user.name "username"
git commit -m "feat: project description"
git remote add origin https://github.com/user/repo.git
git branch -M main
git push -u origin main
```

Create repo via API:
```bash
curl -X POST https://api.github.com/user/repos \
  -H "Authorization: token <TOKEN>" \
  -d '{"name":"repo-name","description":"desc","auto_init":false}'
```

## Pitfalls

1. **SSR + browser APIs = crash.** Always use `dynamic` with `ssr: false` for tools accessing `navigator`, `screen`, `crypto`, `RTCPeerConnection`.

2. **Disk space for node_modules.** Next.js node_modules is ~300MB. If `/data` is small, install in `/tmp` and symlink: `ln -s /tmp/project-name/node_modules ./node_modules`

3. **Webpack cache on small partitions.** Next.js `.next` cache can be 100MB+. If build hangs at "Collecting page data", symlink `.next` to a larger partition.

4. **Static export limitations.** `output: 'export'` means no API routes, no server components, no middleware. All logic must be client-side.

5. **TypeScript strict mode.** WebGL `getContext()` returns union types — cast explicitly: `as WebGLRenderingContext | null`.

6. **GitHub token in commands.** Never commit tokens to git. Use `git remote set-url origin` with token in URL for one push, then remove.

## Verification

After building, verify the project works:

```bash
npm run dev &
sleep 5
curl -s http://localhost:3000 | head -20
# Should return HTML with the app shell
```

Check deployment:
```bash
curl -s -o /dev/null -w "%{http_code}" https://your-app.vercel.app
# Should return 200
```
