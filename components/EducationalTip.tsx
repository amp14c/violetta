'use client';

import { useMemo } from 'react';

const tips = [
  'UV rays can damage skin even on cloudy days — clouds block only 20% of UV.',
  'Windows filter UVB but not UVA rays. Apply sunscreen before driving.',
  'UV index can be high at altitude even when it feels cool.',
  'SPF 30 blocks 97% of UVB rays. Higher SPF offers slightly more protection.',
  'Sunscreen expires — check the date and replace yearly.',
  'Sand and water reflect UV, increasing your exposure by up to 80%.',
  'The UV index is highest between 10 AM and 4 PM.',
  'Darker clothing provides more UV protection than light-coloured fabric.',
];

export default function EducationalTip() {
  // Pick a tip based on the current hour so it rotates through the day
  const tip = useMemo(() => {
    const hour = new Date().getHours();
    return tips[hour % tips.length];
  }, []);

  return (
    <div className="px-4 mb-8">
      <div className="bg-violet-900/30 rounded-2xl border border-violet-500/20 px-4 py-3 flex gap-3 items-start">
        <span className="text-lg mt-0.5">💡</span>
        <p className="text-xs text-white/60 leading-relaxed">{tip}</p>
      </div>
    </div>
  );
}
