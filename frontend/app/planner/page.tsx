'use client';

import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchMenuWeek } from '../../lib/api/menu';
import PlannerGrid from '../../components/PlannerGrid';
import SummarySidebar from '../../components/SummarySidebar';

export default function PlannerPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ['menu', 'current'], queryFn: fetchMenuWeek });

  useEffect(() => {
    // TODO: send analytics event "planner_viewed"
  }, []);

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-8 lg:flex-row">
      <div className="flex-1 rounded-3xl bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-brand-secondary">Планировщик недели</h1>
        {isLoading && <p className="mt-4 text-slate-500">Загружаем меню...</p>}
        {error && <p className="mt-4 text-red-500">Не удалось загрузить меню. Попробуйте позже.</p>}
        {data && <PlannerGrid menuWeek={data} />}
      </div>
      <SummarySidebar />
    </main>
  );
}
