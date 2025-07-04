import { QueryClient, QueryKey } from "@tanstack/react-query";

export const queryClient = new QueryClient();

export const cacheKeys = {
  dashboardMetrics: ["dashboard", "metrics"] as const,
  scanHistory: () => ["scanner", "history"] as const,
  honeypotHistory: () => ["honeypot", "history"] as const,
  tradingBots: ["trading", "bots"] as const,
  notificationSettings: ["notification", "settings"] as const,
  notifications: ["notifications"] as const,
  systemHealth: ["system", "health"] as const,
  systemMetrics: ["system", "metrics"] as const,
};

export function createOptimisticUpdate<TData = unknown>({
  queryKey,
  updater,
}: {
  queryKey: QueryKey;
  updater: (old: TData | undefined, ...args: any[]) => TData;
}) {
  return {
    async onMutate(...args: any[]) {
      await queryClient.cancelQueries({ queryKey });
      const previous = queryClient.getQueryData<TData>(queryKey);
      queryClient.setQueryData(queryKey, (old) => updater(old as TData, ...args));
      return { previous };
    },
    onError(_err: unknown, _vars: any, ctx: any) {
      if (ctx?.previous) {
        queryClient.setQueryData(queryKey, ctx.previous);
      }
    },
    onSettled() {
      queryClient.invalidateQueries({ queryKey });
    },
  };
}

export const invalidateRelatedQueries = {
  onScanComplete(scanId: string) {
    queryClient.invalidateQueries({ queryKey: cacheKeys.scanHistory() });
    queryClient.invalidateQueries({ queryKey: ["scan", scanId] });
  },
  onHoneypotDetection(address: string) {
    queryClient.invalidateQueries({ queryKey: cacheKeys.honeypotHistory() });
    queryClient.invalidateQueries({ queryKey: ["honeypot", address] });
  },
  onTradingBotUpdate(botId: string) {
    queryClient.invalidateQueries({ queryKey: cacheKeys.tradingBots });
    queryClient.invalidateQueries({ queryKey: ["trading", "bot", botId] });
  },
  onBridgeTransaction() {
    queryClient.invalidateQueries({ queryKey: ["bridge", "transactions"] });
    queryClient.invalidateQueries({ queryKey: cacheKeys.dashboardMetrics });
  },
};