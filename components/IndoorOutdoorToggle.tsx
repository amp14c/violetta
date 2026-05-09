'use client';

interface Props {
  indoorMode: boolean;
  onChange: (indoor: boolean) => void;
}

export default function IndoorOutdoorToggle({ indoorMode, onChange }: Props) {
  return (
    <div className="px-4 mb-6">
      <div className="flex bg-white/5 rounded-2xl p-1 border border-white/10">
        <button
          onClick={() => onChange(false)}
          className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
            !indoorMode
              ? 'bg-violet-600 text-white shadow-lg'
              : 'text-white/40 hover:text-white/60'
          }`}
        >
          <span>☀️</span> Outdoor
        </button>
        <button
          onClick={() => onChange(true)}
          className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
            indoorMode
              ? 'bg-white/15 text-white shadow-lg'
              : 'text-white/40 hover:text-white/60'
          }`}
        >
          <span>🏠</span> Indoor
        </button>
      </div>
    </div>
  );
}
