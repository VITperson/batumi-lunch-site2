'use client';

import type { MenuWeek } from '../lib/api/types';

interface Props {
  menuWeek: MenuWeek;
}

export default function PlannerGrid({ menuWeek }: Props) {
  return (
    <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {menuWeek.day_offers.map((day) => (
        <article key={day.id} className="flex flex-col justify-between rounded-2xl border border-slate-200 p-4">
          <header className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-brand-secondary">{day.day_of_week}</h2>
            {day.status !== 'available' && (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase text-slate-500">
                {day.status === 'sold_out' ? 'Нет мест' : 'Закрыто'}
              </span>
            )}
          </header>
          <ul className="mt-3 space-y-1 text-sm text-slate-600">
            {day.items.map((item, idx) => (
              <li key={idx}>• {item}</li>
            ))}
          </ul>
          <footer className="mt-4 flex items-center justify-between text-sm text-slate-500">
            <span>{day.price_lari ? `${day.price_lari} ₾` : `${menuWeek.base_price_lari} ₾`}</span>
            <span>Порции: TODO</span>
          </footer>
        </article>
      ))}
    </div>
  );
}
