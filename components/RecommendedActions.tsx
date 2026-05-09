'use client';

interface Action {
  icon: string;
  label: string;
}

function getActions(uv: number, indoorMode: boolean): Action[] {
  if (indoorMode) return [{ icon: '🏠', label: 'You\'re indoors — enjoy!' }];
  if (uv < 3) return [{ icon: '✅', label: 'No sunscreen needed' }];

  const actions: Action[] = [{ icon: '🧴', label: 'Apply sunscreen SPF 30+' }];
  if (uv >= 3) actions.push({ icon: '🕶️', label: 'Wear sunglasses' });
  if (uv >= 6) actions.push({ icon: '🧢', label: 'Wear a hat' });
  if (uv >= 8) actions.push({ icon: '🌳', label: 'Seek shade when possible' });
  if (uv >= 11) actions.push({ icon: '⚠️', label: 'Avoid sun 10 AM – 4 PM' });
  return actions;
}

interface Props {
  uv: number;
  indoorMode: boolean;
}

export default function RecommendedActions({ uv, indoorMode }: Props) {
  const actions = getActions(uv, indoorMode);
  return (
    <div className="px-4 mb-6">
      <h2 className="text-xs font-semibold tracking-widest text-white/40 uppercase mb-3">
        Right Now
      </h2>
      <div className="flex flex-col gap-2">
        {actions.map((a) => (
          <div
            key={a.label}
            className="flex items-center gap-3 bg-white/5 rounded-2xl px-4 py-3 border border-white/10"
          >
            <span className="text-xl">{a.icon}</span>
            <span className="text-sm font-medium text-white/90">{a.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
