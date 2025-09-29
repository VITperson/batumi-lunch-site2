import './globals.css';
import type { Metadata } from 'next';
import Providers from '../components/Providers';

export const metadata: Metadata = {
  title: 'Batumi Lunch Planner',
  description: 'Weekly lunch ordering experience for Batumi.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="bg-slate-50 text-slate-900 min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
