import { describe, it, expect, vi, afterEach } from "vitest";
import { createOptimisticUpdate, queryClient } from "./react-query";

afterEach(() => {
  queryClient.clear();
});

describe("createOptimisticUpdate", () => {
  it("applies optimistic update and rolls back on error", async () => {
    const key = ["items"];
    queryClient.setQueryData(key, ["a"]);

    const handlers = createOptimisticUpdate<string[]>({
      queryKey: key,
      updater: (old = [], item: string) => [...old, item],
    });

    const ctx = await handlers.onMutate("b");
    expect(queryClient.getQueryData(key)).toEqual(["a", "b"]);

    handlers.onError(new Error("fail"), "b", ctx);
    expect(queryClient.getQueryData(key)).toEqual(["a"]);
  });
});
