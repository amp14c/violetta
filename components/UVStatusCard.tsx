'use client';

import { uvLabel, uvColor } from '@/lib/uv';

interface Props {
  uv: number;
  location: string;
}

export default function UVStatusCard({ uv, location }: Props) {
  const label = uvLabel(uv);
  const color = uvColor(uv);

  return (
    <div className="flex flex-col items-center py-8 px-4">
      <p className="text-sm text-white/50 mb-1 tracking-wide uppercase">{location}</p>

      {/* Big UV number */}
      <div
        className="w-44 h-44 rounded-full flex flex-col items-center justify-center mb-4 shadow-2xl"
        style={{ background: `radial-gradient(circle at 40% 35%, ${color}55, ${color}22)`, border: `2px solid ${color}66` }}
      >
        <span className="text-6xl font-bold leading-none" style={{ color }}>{uv}</span>
        <span className="text-sm font-medium mt-1 tracking-wider" style={{ color }}>{label}</span>
      </div>

      {/* Scale bar */}
      <div className="w-full max-w-xs h-2 rounded-full overflow-hidden bg-white/10 mt-2">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${Math.min((uv / 12) * 100, 100)}%`,
            background: `linear-gradient(to right, #22c55e, #eab308, #f97316, #ef4444, #a855f7)`,
          }}
        />
      </div>
      <div className="flex justify-between w-full max-w-xs text-[10px] text-white/30 mt-1 px-0.5">
        <span>Low</span><span>Moderate</span><span>High</span><span>V.High</span><span>Extreme</span>
      </div>
    </div>
  );
}
