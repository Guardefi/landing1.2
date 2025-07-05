import { cn } from "@/lib/utils";

interface PageLayoutProps {
  children: React.ReactNode;
  className?: string;
  variant?:
    | "default"
    | "security"
    | "trading"
    | "bridge"
    | "analytics"
    | "computing"
    | "monitoring";
}

export const PageLayout = ({
  children,
  className,
  variant = "default",
}: PageLayoutProps) => {
  const getVariantStyles = () => {
    switch (variant) {
      case "security":
        return "bg-gradient-to-br from-slate-50 via-red-50 to-orange-50 dark:from-slate-900 dark:via-red-900/20 dark:to-orange-900/20";
      case "trading":
        return "bg-gradient-to-br from-slate-50 via-green-50 to-emerald-50 dark:from-slate-900 dark:via-green-900/20 dark:to-emerald-900/20";
      case "bridge":
        return "bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-900 dark:via-blue-900/20 dark:to-cyan-900/20";
      case "analytics":
        return "bg-gradient-to-br from-slate-50 via-indigo-50 to-purple-50 dark:from-slate-900 dark:via-indigo-900/20 dark:to-purple-900/20";
      case "computing":
        return "bg-gradient-to-br from-slate-50 via-violet-50 to-purple-50 dark:from-slate-900 dark:via-violet-900/20 dark:to-purple-900/20";
      case "monitoring":
        return "bg-gradient-to-br from-slate-50 via-amber-50 to-yellow-50 dark:from-slate-900 dark:via-amber-900/20 dark:to-yellow-900/20";
      default:
        return "bg-gradient-to-br from-slate-50 via-slate-100 to-slate-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900";
    }
  };

  return (
    <div className={cn("min-h-screen", getVariantStyles(), className)}>
      <div className="container mx-auto px-6 py-4 space-y-6">{children}</div>
    </div>
  );
};
