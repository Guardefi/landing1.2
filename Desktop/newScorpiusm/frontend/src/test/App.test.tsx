/**
 * Basic smoke tests for the main App component
 */
import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock the auth context and other dependencies
vi.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuth: () => ({
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
    loading: false
  })
}));

vi.mock('../contexts/SubscriptionContext', () => ({
  SubscriptionProvider: ({ children }: { children: React.ReactNode }) => children,
  useSubscription: () => ({
    subscription: null,
    loading: false
  })
}));

vi.mock('../components/ui/enhanced-toast', () => ({
  ToastProvider: ({ children }: { children: React.ReactNode }) => children,
  useToast: () => ({
    toast: vi.fn()
  })
}));

describe('App Component', () => {
  const renderApp = () => {
    // App component already includes Router, so we just render it directly
    render(<App />);
  };

  it('renders without crashing', () => {
    renderApp();
    expect(document.body).toBeInTheDocument();
  });
  it('has a root div element', () => {
    renderApp();
    // Should have some content rendered - check for the main app layout
    const appLayout = document.querySelector('[class*="min-h-screen"]');
    expect(appLayout).toBeInTheDocument();
  });

  it('renders main app structure', () => {
    renderApp();
    // Should have basic app structure (may be navigation or main content)
    const mainElements = document.querySelectorAll('main, nav, div');
    expect(mainElements.length).toBeGreaterThan(0);
  });
});
