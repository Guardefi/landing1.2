import { describe, it, expect } from "vitest";
import { cn } from "./utils";

describe("cn", () => {
  it("merges conditional class names", () => {
    const result = cn("base", { active: true, hidden: false }, "end");
    expect(result).toBe("base active end");
  });

  it("deduplicates tailwind classes", () => {
    const result = cn("p-2", "p-4");
    expect(result).toBe("p-4");
  });
});
