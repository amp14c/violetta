'use client';

const guidelines = [
  {
    icon: '👆👆',
    title: 'Face & Neck',
    detail: '2 finger lengths of sunscreen — about ⅓ to ½ teaspoon',
  },
  {
    icon: '🥃',
    title: 'Full Body',
    detail: 'About a shot glass amount (1 oz) for complete coverage',
  },
  {
    icon: '⏱️',
    title: 'Reapplication',
    detail: 'Every 2 hours outdoors, and after swimming or sweating',
  },
  {
    icon: '⏰',
    title: 'Apply Early',
    detail: 'Apply 15–30 minutes before going outside for best protection',
  },
];

export default function SunscreenGuidance() {
  return (
    <div className="px-4 mb-6">
      <h2 className="text-xs font-semibold tracking-widest text-white/40 uppercase mb-3">
        Sunscreen Guide
      </h2>
      <div className="grid grid-cols-2 gap-2">
        {guidelines.map((g) => (
          <div
            key={g.title}
            className="bg-white/5 rounded-2xl border border-white/10 p-4 flex flex-col gap-1"
          >
            <span className="text-xl">{g.icon}</span>
            <p className="text-xs font-semibold text-white/80">{g.title}</p>
            <p className="text-xs text-white/45 leading-relaxed">{g.detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
