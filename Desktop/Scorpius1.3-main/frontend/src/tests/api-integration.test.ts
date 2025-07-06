import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { apiClient } from "../lib/api-client";
import { ActionMapper } from "../utils/actionMapper";

// Mock API client
vi.mock("../lib/api-client");

describe("API Integration Tests", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  describe("Scanner API Integration", () => {
    it("should call scanContract API when scan button is clicked", async () => {
      const mockScanResult = { scan_id: "test-123", status: "started" };
      vi.mocked(apiClient.scanContract).mockResolvedValue(mockScanResult);

      const result = await ActionMapper.scanContract("0x123...", {
        scanType: "quick",
      });

      expect(apiClient.scanContract).toHaveBeenCalledWith("0x123...", {
        scanType: "quick",
      });
      expect(result).toEqual(mockScanResult);
    });

    it("should handle upload and scan functionality", async () => {
      const mockFile = new File(["contract code"], "test.sol", {
        type: "text/plain",
      });
      const mockUploadResult = { scan_id: "upload-123", status: "uploaded" };

      vi.mocked(apiClient.uploadAndScan).mockResolvedValue(mockUploadResult);

      const result = await ActionMapper.uploadAndScanFile(mockFile);

      expect(apiClient.uploadAndScan).toHaveBeenCalledWith(mockFile);
      expect(result).toEqual(mockUploadResult);
    });
  });

  describe("Honeypot API Integration", () => {
    it("should call detectHoneypot API", async () => {
      const mockDetectionResult = {
        detection_id: "detect-123",
        status: "detecting",
      };
      vi.mocked(apiClient.detectHoneypot).mockResolvedValue(
        mockDetectionResult,
      );

      const result = await ActionMapper.detectHoneypot("0x456...");

      expect(apiClient.detectHoneypot).toHaveBeenCalledWith("0x456...");
      expect(result).toEqual(mockDetectionResult);
    });

    it("should call analyzeHoneypot API", async () => {
      const mockAnalysisResult = {
        analysis_id: "analyze-123",
        status: "completed",
      };
      vi.mocked(apiClient.analyzeHoneypot).mockResolvedValue(
        mockAnalysisResult,
      );

      const result = await ActionMapper.analyzeHoneypot("0x789...");

      expect(apiClient.analyzeHoneypot).toHaveBeenCalledWith("0x789...");
      expect(result).toEqual(mockAnalysisResult);
    });
  });

  describe("Bridge API Integration", () => {
    it("should call getBridgeQuote API", async () => {
      const mockQuote = { estimatedFee: "0.01", feeCurrency: "ETH" };
      vi.mocked(apiClient.getBridgeQuote).mockResolvedValue(mockQuote);

      const result = await ActionMapper.getBridgeQuote(
        "ethereum",
        "bsc",
        "100",
        "USDC",
      );

      expect(apiClient.getBridgeQuote).toHaveBeenCalledWith(
        "ethereum",
        "bsc",
        "100",
        "USDC",
      );
      expect(result).toEqual(mockQuote);
    });

    it("should call initiateBridgeTransfer API", async () => {
      const mockTransfer = { transfer_id: "transfer-123", status: "initiated" };
      vi.mocked(apiClient.initiateBridgeTransfer).mockResolvedValue(
        mockTransfer,
      );

      const result = await ActionMapper.initiateBridgeTransfer(
        "ethereum",
        "bsc",
        "100",
        "USDC",
      );

      expect(apiClient.initiateBridgeTransfer).toHaveBeenCalledWith(
        "ethereum",
        "bsc",
        "100",
        "USDC",
      );
      expect(result).toEqual(mockTransfer);
    });
  });

  describe("Wallet API Integration", () => {
    it("should call checkWallet API", async () => {
      const mockWalletCheck = { risk_score: 75, approvals: 5 };
      vi.mocked(apiClient.checkWallet).mockResolvedValue(mockWalletCheck);

      const result = await ActionMapper.checkWallet("0xabc...");

      expect(apiClient.checkWallet).toHaveBeenCalledWith("0xabc...");
      expect(result).toEqual(mockWalletCheck);
    });

    it("should call revokeApproval API", async () => {
      const mockRevoke = { success: true, tx_hash: "0x123..." };
      vi.mocked(apiClient.revokeApproval).mockResolvedValue(mockRevoke);

      const result = await ActionMapper.revokeApproval(
        "0xabc...",
        "0xtoken...",
        "0xspender...",
      );

      expect(apiClient.revokeApproval).toHaveBeenCalledWith(
        "0xabc...",
        "0xtoken...",
        "0xspender...",
      );
      expect(result).toEqual(mockRevoke);
    });
  });

  describe("Analytics API Integration", () => {
    it("should call getAnalytics API with time range", async () => {
      const mockAnalytics = { totalValue: "1M", threats: 100 };
      vi.mocked(apiClient.getAnalytics).mockResolvedValue(mockAnalytics);

      const result = await ActionMapper.getAnalytics("24h");

      expect(apiClient.getAnalytics).toHaveBeenCalledWith("24h");
      expect(result).toEqual(mockAnalytics);
    });
  });

  describe("Settings API Integration", () => {
    it("should call updateSystemConfig API", async () => {
      const mockConfig = { theme: "dark", notifications: true };
      const mockUpdateResult = { success: true };
      vi.mocked(apiClient.updateSystemConfig).mockResolvedValue(
        mockUpdateResult,
      );

      const result = await ActionMapper.updateSystemConfig(mockConfig);

      expect(apiClient.updateSystemConfig).toHaveBeenCalledWith(mockConfig);
      expect(result).toEqual(mockUpdateResult);
    });
  });

  describe("Error Handling", () => {
    it("should handle API errors gracefully", async () => {
      const mockError = new Error("API Error");
      vi.mocked(apiClient.scanContract).mockRejectedValue(mockError);

      await expect(ActionMapper.scanContract("0x123...")).rejects.toThrow(
        "API Error",
      );
    });
  });
});
