import { describe, it, expect, beforeEach, vi } from "vitest";
import { StorageManager, loadInitialConfig } from "./storage";

beforeEach(() => {
  const store: Record<string, string> = {};
  vi.stubGlobal("localStorage", {
    getItem: (k: string) => (k in store ? store[k] : null),
    setItem: (k: string, v: string) => {
      store[k] = String(v);
    },
    removeItem: (k: string) => {
      delete store[k];
    },
    clear: () => {
      for (const k in store) delete store[k];
    },
    key: (i: number) => Object.keys(store)[i] ?? null,
    get length() {
      return Object.keys(store).length;
    },
  });
  (globalThis.localStorage as any).clear();
});

describe("StorageManager", () => {
  it("persists system config", () => {
    StorageManager.setSystemConfig({ openaiApiKey: "key" });
    const cfg = StorageManager.getSystemConfig();
    expect(cfg.openaiApiKey).toBe("key");
  });

  it("loadInitialConfig initializes localStorage", () => {
    expect(localStorage.getItem("scorpius_config")).toBeNull();
    const cfg = loadInitialConfig();
    expect(cfg).toBeTruthy();
    expect(localStorage.getItem("scorpius_config")).not.toBeNull();
  });
});
