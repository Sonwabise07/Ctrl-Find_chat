import { render } from '@testing-library/react';
import { RichText } from './richText';

describe('RichText', () => {
  it('turns ** markers into bold text', () => {
    const { container } = render(<RichText text="**3 laptops** are available." />);
    expect(container.querySelector('strong')).toHaveTextContent('3 laptops');
    expect(container).toHaveTextContent('3 laptops are available.');
  });

  it('keeps plain text as it is and never injects HTML', () => {
    const { container } = render(<RichText text="<b>no</b> markup" />);
    expect(container.querySelector('b')).toBeNull();
    expect(container).toHaveTextContent('<b>no</b> markup');
  });
});
