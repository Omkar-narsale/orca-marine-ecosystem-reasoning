import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ORCA — Marine EcOsystem Reasoning with Collaborative Agents',
  description:
    'Agentic AI-powered Marine Intelligence Platform for oceanographic, weather, satellite and geospatial reasoning. SIH 2026 Phase 1 Prototype.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-slate-50 text-slate-900 font-sans antialiased selection:bg-teal-100 selection:text-teal-900 min-h-screen flex flex-col">
        {children}
      </body>
    </html>
  );
}
