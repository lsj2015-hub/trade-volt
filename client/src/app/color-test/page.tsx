export default function ColorTestPage() {
  return (
    <div className="flex gap-2.5 text-center font-sans">
      <div className="flex-1">
        <div className="h-20 rounded-lg bg-slate-700"></div>
        <p className="mt-2 font-bold">Deep Slate Blue</p>
        <p className="text-sm text-gray-500">#334155</p>
      </div>
      <div className="flex-1">
        <div className="h-20 rounded-lg bg-teal-500"></div>
        <p className="mt-2 font-bold">Cool Teal</p>
        <p className="text-sm text-gray-500">#14B8A6</p>
      </div>
      <div className="flex-1">
        <div className="h-20 rounded-lg bg-amber-400"></div>
        <p className="mt-2 font-bold">Soft Gold</p>
        <p className="text-sm text-gray-500">#FBBF24</p>
      </div>
      <div className="flex-1">
        <div className="h-20 rounded-lg border border-slate-200 bg-slate-100"></div>
        <p className="mt-2 font-bold">Light Slate</p>
        <p className="text-sm text-gray-500">#F1F5F9</p>
      </div>
      <div className="flex-1">
        <div className="h-20 rounded-lg bg-slate-800"></div>
        <p className="mt-2 font-bold">Charcoal</p>
        <p className="text-sm text-gray-500">#1E293B</p>
      </div>
    </div>
  );
}
