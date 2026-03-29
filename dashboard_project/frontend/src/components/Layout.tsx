import React from 'react';
import { cn } from '../utils';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}

function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-primary-600">ALVO Platform</h1>
            </div>
            <nav className="hidden md:ml-10 md:flex md:space-x-8">
              <NavItem label="Dashboard" active />
              <NavItem label="Agents" />
              <NavItem label="Tasks" />
              <NavItem label="Analytics" />
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            <ConnectionStatus />
            <div className="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center text-white font-medium text-sm">
              A
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

function NavItem({ label, active = false }: { label: string; active?: boolean }) {
  return (
    <a
      href="#"
      className={cn(
        'inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-colors',
        active
          ? 'border-primary-500 text-primary-600'
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      )}
    >
      {label}
    </a>
  );
}

function ConnectionStatus() {
  const [connected, setConnected] = React.useState(true);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setConnected(Math.random() > 0.1);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center space-x-2">
      <div
        className={cn(
          'h-2.5 w-2.5 rounded-full',
          connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
        )}
      />
      <span className="text-xs text-gray-500">
        {connected ? 'Live' : 'Disconnected'}
      </span>
    </div>
  );
}
