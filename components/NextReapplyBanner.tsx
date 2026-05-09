'use client';

interface Props {
  uv: number;
  indoorMode: boolean;
  lastAppliedAt: number | null; // Date.now() when sunscreen was last applied/notified
}

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

export default function NextReapplyBanner({ uv, indoorMode, lastAppliedAt }: Props) {
  if (indoorMode || uv < 3) return null;

  const reapplyAt = lastAppliedAt ? lastAppliedAt + 2 * 60 * 60 * 1000 : null;
  const isOverdue = reapplyAt ? Date.now() > reapplyAt : false;

  return (
    <div className={`mx-4 mb-5 rounded-2xl px-4 py-3 flex items-center gap-3 border ${
      isOverdue
        ? 'bg-red-500/15 border-red-500/30'
        : 'bg-violet-500/15 border-violet-500/30'
    }`}>
      <span className="text-xl">{isOverdue ? '⏰' : '🧴'}</span>
      <div>
        <p className="text-xs text-white/50 font-medium uppercase tracking-wide">
          {isOverdue ? 'Reapplication overdue' : 'Next reapplication'}
        </p>
        <p className="text-sm font-semibold text-white">
          {reapplyAt
            ? isOverdue
              ? 'Reapply sunscreen now'
              : `Reapply sunscreen at ${formatTime(reapplyAt)}`
            : 'Reapply every 2 hours outdoors'}
        </p>
      </div>
    </div>
  );
}
