import type { Chip } from '../../api/types';

interface Props {
  chips: Chip[];
  onAsk: (question: string) => void;
}

/** Suggested questions, and the dashboard choices after "What dashboards are there?". */
export function Suggestions({ chips, onAsk }: Props) {
  if (chips.length === 0) return null;
  return (
    <div className="chips">
      {chips.map((chip) => (
        <button
          key={chip.label}
          type="button"
          className="chip"
          onClick={() => onAsk(chip.question)}
        >
          {chip.label}
        </button>
      ))}
    </div>
  );
}
