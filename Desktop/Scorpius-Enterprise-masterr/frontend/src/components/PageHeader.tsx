import { useState, useEffect } from "react";
import { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  title: string;
  description: string;
  icon: LucideIcon;
  iconGradient?: string;
  borderColor?: string;
  action?: React.ReactNode;
}

export const PageHeader = ({
  title,
  description,
  icon: Icon,
  iconGradient = "from-cyan-500 to-blue-600",
  borderColor = "border-cyan-400/30",
  action,
}: PageHeaderProps) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className={`glass border ${borderColor} rounded-2xl mb-8`}>
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div
              className={`p-3 rounded-xl bg-gradient-to-br ${iconGradient} glow-cyan`}
            >
              <Icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{title}</h1>
              <p className="text-gray-400">{description}</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {action}
            <div className="text-right">
              <div className="text-sm font-medium">
                {currentTime.toLocaleTimeString()}
              </div>
              <div className="text-xs text-muted-foreground">
                {currentTime.toLocaleDateString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
