import type { Meta } from '../../api/types';
import { Icon } from '../Icon';
import './chat.css';

/** The side panel listing what the assistant can answer. Greyed out when the data is not there yet. */
export function SupportedTypes({ categories }: { categories: Meta['categories'] }) {
  return (
    <section className="supported" aria-label="Supported question types">
      <h2>Supported question types</h2>
      <ul>
        {categories.map((category) => (
          <li key={category.label}>
            <span
              className={
                category.available ? 'supported__tick' : 'supported__tick supported__tick--off'
              }
            >
              <Icon name={category.available ? 'check' : 'dash'} />
            </span>
            <span>
              {category.label}
              {!category.available && (
                <small>Needs audit and loss data that is not in the system yet</small>
              )}
            </span>
          </li>
        ))}
      </ul>
      <p className="supported__note">
        Only ever reports figures actually present in the data. States plainly when a question is
        out of scope, rather than estimating an answer.
      </p>
    </section>
  );
}
