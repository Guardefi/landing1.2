import { cn } from "@/lib/utils";
import { useSystemStatus } from "@/hooks";

interface SystemStatusWidgetProps {
  className?: string;
}

export const SystemStatusWidget = ({ className }: SystemStatusWidgetProps) => {
  const { data, isLoading, error } = useSystemStatus();

  if (isLoading) {
    return <div className={cn("p-4", className)}>Loading system status...</div>;
  }

  if (error || !data?.success) {
    return <div className={cn("p-4 text-red-600", className)}>Failed to load system status</div>;
  }

  const status = data.data ?? data;
  const metrics = status.metrics || {};
  const services = status.services || {};

  return (
    <div className={cn("p-4 bg-slate-800 rounded-lg", className)}>
      <h3 className="text-lg font-semibold mb-2 text-cyan-400">System Status</h3>
      <div className="text-sm text-gray-300 mb-4">
        Active Connections: {metrics.active_connections ?? 0}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {Object.entries(services).map(([name, info]: any) => (
          <div key={name} className="flex justify-between text-sm bg-slate-900 p-2 rounded">
            <span className="font-medium">{name}</span>
            <span className={info.status === 'healthy' ? 'text-emerald-400' : info.status === 'unhealthy' ? 'text-red-500' : 'text-yellow-400'}>
              {info.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SystemStatusWidget;
