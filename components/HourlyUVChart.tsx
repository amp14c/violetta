'use client';

import { BarChart, Bar, XAxis, YAxis, Cell, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import type { HourlyUV } from '@/lib/types';
import { uvColor } from '@/lib/uv';

interface Props {
  hourly: HourlyUV[];
  peakTime: string;
}

function formatHour(iso: string) {
  const d = new Date(iso);
  const h = d.getHours();
  if (h === 0) return '12a';
  if (h === 12) return '12p';
  return h < 12 ? `${h}a` : `${h - 12}p`;
}

export default function HourlyUVChart({ hourly, peakTime }: Props) {
  // Show next 12 hours from now
  const now = Date.now();
  const slots = hourly
    .filter((h) => {
      const t = new Date(h.time).getTime();
      return t >= now - 60 * 60 * 1000 && t <= now + 11 * 60 * 60 * 1000;
    })
    .slice(0, 12);

  if (slots.length === 0) return null;

  const peakHour = formatHour(peakTime);

  return (
    <div className="px-4 mb-6">
      <h2 className="text-xs font-semibold tracking-widest text-white/40 uppercase mb-3">
        Hourly UV — Next 12 Hours
      </h2>
      <div className="bg-white/5 rounded-2xl border border-white/10 p-4">
        <ResponsiveContainer width="100%" height={140}>
          <BarChart data={slots} barSize={16} margin={{ top: 4, right: 0, left: -28, bottom: 0 }}>
            <XAxis
              dataKey="time"
              tickFormatter={formatHour}
              tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[0, 12]}
              tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              ticks={[0, 3, 6, 8, 11]}
            />
            <ReferenceLine y={3} stroke="rgba(255,255,255,0.15)" strokeDasharray="3 3" />
            <Tooltip
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const d = payload[0].payload as HourlyUV;
                return (
                  <div className="bg-[#1a0f2e] border border-white/20 rounded-lg px-3 py-1.5 text-xs text-white">
                    <span className="font-semibold">{formatHour(d.time)}</span> · UV {d.uv}
                    {formatHour(d.time) === peakHour && <span className="ml-1 text-yellow-400">peak</span>}
                  </div>
                );
              }}
            />
            <Bar dataKey="uv" radius={[4, 4, 0, 0]}>
              {slots.map((entry) => (
                <Cell key={entry.time} fill={uvColor(entry.uv)} fillOpacity={0.85} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
