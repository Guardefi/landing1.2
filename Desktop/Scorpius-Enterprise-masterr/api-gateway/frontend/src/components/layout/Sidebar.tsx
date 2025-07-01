import {
  Shield,
  TrendingUp,
  GitBranch,
  BarChart3,
  Cpu,
  Activity,
  Search,
  Atom,
  Home,
  X,
} from 'lucide-react';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const navigation = [
  { name: 'Overview', href: '/', icon: Home, current: true },
  { name: 'Security Operations', href: '/security', icon: Shield, current: false },
  { name: 'AI Trading Engine', href: '/trading', icon: TrendingUp, current: false },
  { name: 'Cross-Chain Bridge', href: '/bridge', icon: GitBranch, current: false },
  { name: 'Enterprise Analytics', href: '/analytics', icon: BarChart3, current: false },
  { name: 'Computing Engine', href: '/computing', icon: Cpu, current: false },
  { name: 'Monitoring', href: '/monitoring', icon: Activity, current: false },
  { name: 'Blockchain Forensics', href: '/forensics', icon: Search, current: false },
  { name: 'Quantum Security', href: '/quantum', icon: Atom, current: false },
];

export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={onClose} />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-border">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="ml-2 text-lg font-semibold">Scorpius X</span>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="lg:hidden">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map(item => {
              const Icon = item.icon;
              return (
                <a
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    item.current
                      ? 'bg-primary/10 text-primary border-r-2 border-primary'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent',
                  )}
                >
                  <Icon
                    className={cn(
                      'mr-3 h-5 w-5 flex-shrink-0',
                      item.current
                        ? 'text-primary'
                        : 'text-muted-foreground group-hover:text-foreground',
                    )}
                  />
                  {item.name}
                </a>
              );
            })}
          </div>
        </nav>

        {/* Bottom section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <div className="text-sm text-muted-foreground">All systems operational</div>
          </div>
        </div>
      </div>
    </>
  );
}
