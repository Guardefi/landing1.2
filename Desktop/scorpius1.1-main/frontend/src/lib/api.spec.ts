import { describe, it, expect, vi } from "vitest";
import { HttpClient } from "./api";

describe("HttpClient", () => {
  const fetchMock = vi.fn();
  const client = new HttpClient({ fetchFn: fetchMock, baseUrl: "http://test" });

  it("sends GET requests", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true }), { status: 200 })
    );
    await client.get("/hello");
    expect(fetchMock).toHaveBeenCalledWith("http://test/hello", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      body: undefined,
    });
  });

  it("sends POST requests with body", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true }), { status: 200 })
    );
    await client.post("/hello", { a: 1 });
    expect(fetchMock).toHaveBeenCalledWith("http://test/hello", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ a: 1 }),
    });
  });
});
