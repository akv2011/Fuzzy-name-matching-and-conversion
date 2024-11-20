// tests/components/Dashboard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Dashboard from '@/components/dashboard/Dashboard';

describe('Dashboard', () => {
  it('renders dashboard components', () => {
    render(<Dashboard />);
    expect(screen.getByText('Fuzzy Name Conversion Dashboard')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter name to search')).toBeInTheDocument();
    expect(screen.getByText('Process & Search')).toBeInTheDocument();
  });

  it('handles name input and search', async () => {
    render(<Dashboard />);
    const input = screen.getByPlaceholderText('Enter name to search');
    const searchButton = screen.getByText('Process & Search');

    fireEvent.change(input, { target: { value: 'Suresh Kumar' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('सुरेश कुमार')).toBeInTheDocument();
    });
  });
});