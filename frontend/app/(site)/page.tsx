'use client';

import Link from 'next/link';

export default function PlannerLanding() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <section className="rounded-3xl bg-white p-8 shadow-sm">
        <h1 className="text-3xl font-semibold text-brand-secondary">Batumi Lunch Planner</h1>
        <p className="mt-4 text-lg text-slate-600">
          Полноценный планировщик недели находится в разработке. Этот экран отрисовывает skeleton, а основные UI-компоненты
          будут добавлены в следующих задачах: грид дней, пресеты, сводка корзины, гостевой вход.
        </p>
        <div className="mt-6 flex gap-4">
          <Link
            href="/planner"
            className="rounded-lg bg-brand-primary px-4 py-2 font-medium text-white shadow hover:bg-brand-primary/90"
          >
            Перейти к планировщику (стадия MVP)
          </Link>
          <Link href="/menu" className="rounded-lg border border-brand-primary px-4 py-2 text-brand-primary">
            Посмотреть меню
          </Link>
        </div>
      </section>
    </main>
  );
}
