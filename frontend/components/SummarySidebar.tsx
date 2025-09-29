'use client';

export default function SummarySidebar() {
  return (
    <aside className="sticky top-6 h-fit rounded-3xl bg-white p-6 shadow-sm lg:w-80">
      <h2 className="text-xl font-semibold text-brand-secondary">Сводка заказа</h2>
      <p className="mt-2 text-sm text-slate-500">
        Тут появится динамическая сводка выбранных дней, промокоды, управление количеством недель и переключатель подписки.
        Данные будут синхронизированы с Zustand-стейтом.
      </p>
      <div className="mt-6 space-y-3 text-sm text-slate-600">
        <div className="flex items-center justify-between">
          <span>Выбрано дней</span>
          <span className="font-medium">0</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Скидка</span>
          <span className="font-medium">0 ₾</span>
        </div>
        <div className="flex items-center justify-between text-base font-semibold text-brand-secondary">
          <span>Итого</span>
          <span>0 ₾</span>
        </div>
      </div>
      <button className="mt-6 w-full rounded-xl bg-brand-primary px-4 py-3 text-white shadow hover:bg-brand-primary/90">
        Перейти к оформлению
      </button>
      <p className="mt-3 text-xs text-slate-400">Оплата и гостевой вход будут реализованы после интеграции с backend.</p>
    </aside>
  );
}
