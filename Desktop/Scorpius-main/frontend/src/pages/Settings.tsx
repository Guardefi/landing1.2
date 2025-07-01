import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import {
  Settings,
  Save,
  RefreshCw,
  Bell,
  Shield,
  Network,
  Key,
  Database,
  Wallet,
  Eye,
  EyeOff,
  CheckCircle,
  AlertTriangle,
  Copy,
  Download,
  Upload,
  Trash2,
  Brain,
  MessageSquare,
  Globe,
  Cpu,
  Lock,
  Activity,
  BarChart3,
} from "lucide-react";
import { StorageManager, SystemConfig } from "@/lib/storage";

const Settings = () => {
  const [config, setConfig] = useState<SystemConfig>(
    StorageManager.getSystemConfig(),
  );
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    // Load config from storage first (immediate)
    const savedConfig = StorageManager.getSystemConfig();
    setConfig(savedConfig);

    // Then try to sync with backend
    const syncWithBackend = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/system/config`,
        );
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data) {
            // Merge backend config with local config
            const mergedConfig = { ...savedConfig, ...data.data };
            setConfig(mergedConfig);
            StorageManager.setSystemConfig(mergedConfig);
          }
        }
      } catch (error) {
        console.warn("Backend config sync failed, using local config:", error);
      }
    };

    syncWithBackend();
  }, []);

  const handleConfigChange = (key: keyof SystemConfig, value: any) => {
    setConfig((prev) => ({
      ...prev,
      [key]: value,
    }));
    setHasChanges(true);
  };

  const handlePluginChange = (
    plugin: keyof SystemConfig["plugins"],
    enabled: boolean,
  ) => {
    setConfig((prev) => ({
      ...prev,
      plugins: {
        ...prev.plugins,
        [plugin]: enabled,
      },
    }));
    setHasChanges(true);
  };

  const toggleSecret = (field: string) => {
    setShowSecrets((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard`);
  };

  const saveConfiguration = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage
      StorageManager.setSystemConfig(config);

      // Optionally sync with backend
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/system/config`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(config),
          },
        );

        if (response.ok) {
          toast.success("Configuration saved and synced with backend");
        } else {
          toast.success("Configuration saved locally (backend sync failed)");
        }
      } catch (error) {
        toast.success("Configuration saved locally (backend unavailable)");
      }

      setHasChanges(false);
    } catch (error) {
      toast.error("Failed to save configuration");
    } finally {
      setIsSaving(false);
    }
  };

  const resetToDefaults = () => {
    const defaultConfig = StorageManager.getSystemConfig();
    setConfig(defaultConfig);
    setHasChanges(true);
    toast.info("Configuration reset to defaults");
  };

  const exportConfiguration = () => {
    const data = StorageManager.exportData();
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `scorpius-config-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Configuration exported");
  };

  const importConfiguration = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result as string;
        if (StorageManager.importData(data)) {
          const importedConfig = StorageManager.getSystemConfig();
          setConfig(importedConfig);
          setHasChanges(false);
          toast.success("Configuration imported successfully");
        } else {
          toast.error("Failed to import configuration");
        }
      } catch (error) {
        toast.error("Invalid configuration file");
      }
    };
    reader.readAsText(file);
  };

  const clearAllData = () => {
    if (
      confirm(
        "Are you sure you want to clear all data? This action cannot be undone.",
      )
    ) {
      StorageManager.clearAllData();
      const defaultConfig = StorageManager.getSystemConfig();
      setConfig(defaultConfig);
      setHasChanges(false);
      toast.success("All data cleared");
    }
  };

  const SecretInput = ({
    label,
    value,
    onChange,
    placeholder,
    field,
  }: {
    label: string;
    value: string;
    onChange: (value: string) => void;
    placeholder: string;
    field: string;
  }) => (
    <div className="space-y-2">
      <Label className="text-sm font-medium">{label}</Label>
      <div className="relative">
        <Input
          type={showSecrets[field] ? "text" : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="pr-20"
        />
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => toggleSecret(field)}
            className="h-6 w-6 p-0"
          >
            {showSecrets[field] ? (
              <EyeOff className="h-3 w-3" />
            ) : (
              <Eye className="h-3 w-3" />
            )}
          </Button>
          {value && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(value, label)}
              className="h-6 w-6 p-0"
            >
              <Copy className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <PageLayout>
      <PageHeader
        title="System Configuration"
        description="Configure API keys, RPC endpoints, notifications, and system settings"
        icon={Settings}
        iconGradient="from-blue-500 to-purple-600"
      />

      <div className="space-y-6">
        {/* Quick Actions Bar */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Badge variant={hasChanges ? "destructive" : "secondary"}>
                  {hasChanges ? "Unsaved Changes" : "Saved"}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Configuration is automatically persisted locally
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="file"
                  accept=".json"
                  onChange={importConfiguration}
                  className="hidden"
                  id="import-config"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    document.getElementById("import-config")?.click()
                  }
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Import
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={exportConfiguration}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
                <Button variant="outline" size="sm" onClick={resetToDefaults}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button
                  onClick={saveConfiguration}
                  disabled={!hasChanges || isSaving}
                  className="bg-gradient-to-r from-blue-500 to-purple-600"
                >
                  {isSaving ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Configuration
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="ai-apis" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger
              value="ai-apis"
              className="flex items-center space-x-2"
            >
              <Brain className="h-4 w-4" />
              <span className="hidden sm:inline">AI APIs</span>
            </TabsTrigger>
            <TabsTrigger value="rpc" className="flex items-center space-x-2">
              <Globe className="h-4 w-4" />
              <span className="hidden sm:inline">RPC URLs</span>
            </TabsTrigger>
            <TabsTrigger value="wallet" className="flex items-center space-x-2">
              <Wallet className="h-4 w-4" />
              <span className="hidden sm:inline">Wallet</span>
            </TabsTrigger>
            <TabsTrigger
              value="notifications"
              className="flex items-center space-x-2"
            >
              <Bell className="h-4 w-4" />
              <span className="hidden sm:inline">Notifications</span>
            </TabsTrigger>
            <TabsTrigger
              value="plugins"
              className="flex items-center space-x-2"
            >
              <Cpu className="h-4 w-4" />
              <span className="hidden sm:inline">Plugins</span>
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              <span className="hidden sm:inline">System</span>
            </TabsTrigger>
          </TabsList>

          {/* AI API Keys Tab */}
          <TabsContent value="ai-apis">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5" />
                  <span>AI API Keys</span>
                </CardTitle>
                <CardDescription>
                  Configure API keys for AI-powered analysis and security
                  scanning
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <Alert>
                  <Shield className="h-4 w-4" />
                  <AlertDescription>
                    API keys are stored locally and encrypted. They are never
                    sent to external servers unless explicitly configured.
                  </AlertDescription>
                </Alert>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <SecretInput
                    label="OpenAI API Key"
                    value={config.openaiApiKey}
                    onChange={(value) =>
                      handleConfigChange("openaiApiKey", value)
                    }
                    placeholder="sk-..."
                    field="openaiApiKey"
                  />

                  <SecretInput
                    label="Anthropic API Key"
                    value={config.anthropicApiKey}
                    onChange={(value) =>
                      handleConfigChange("anthropicApiKey", value)
                    }
                    placeholder="sk-ant-..."
                    field="anthropicApiKey"
                  />

                  <SecretInput
                    label="Slither API Key"
                    value={config.slitherApiKey}
                    onChange={(value) =>
                      handleConfigChange("slitherApiKey", value)
                    }
                    placeholder="slither_..."
                    field="slitherApiKey"
                  />

                  <SecretInput
                    label="MythX API Key"
                    value={config.mythxApiKey}
                    onChange={(value) =>
                      handleConfigChange("mythxApiKey", value)
                    }
                    placeholder="mythx_..."
                    field="mythxApiKey"
                  />

                  <SecretInput
                    label="Manticore API Key"
                    value={config.mantecoreApiKey}
                    onChange={(value) =>
                      handleConfigChange("mantecoreApiKey", value)
                    }
                    placeholder="manticore_..."
                    field="mantecoreApiKey"
                  />

                  <SecretInput
                    label="Mythril API Key"
                    value={config.mythrilApiKey}
                    onChange={(value) =>
                      handleConfigChange("mythrilApiKey", value)
                    }
                    placeholder="mythril_..."
                    field="mythrilApiKey"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* RPC URLs Tab */}
          <TabsContent value="rpc">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Globe className="h-5 w-5" />
                  <span>RPC Endpoints</span>
                </CardTitle>
                <CardDescription>
                  Configure blockchain RPC endpoints for multi-chain support
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Ethereum RPC URL</Label>
                    <Input
                      value={config.ethereumRpc}
                      onChange={(e) =>
                        handleConfigChange("ethereumRpc", e.target.value)
                      }
                      placeholder="https://mainnet.infura.io/v3/YOUR_KEY"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Polygon RPC URL</Label>
                    <Input
                      value={config.polygonRpc}
                      onChange={(e) =>
                        handleConfigChange("polygonRpc", e.target.value)
                      }
                      placeholder="https://polygon-mainnet.infura.io/v3/YOUR_KEY"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>BSC RPC URL</Label>
                    <Input
                      value={config.bscRpc}
                      onChange={(e) =>
                        handleConfigChange("bscRpc", e.target.value)
                      }
                      placeholder="https://bsc-dataseed.binance.org/"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Arbitrum RPC URL</Label>
                    <Input
                      value={config.arbitrumRpc}
                      onChange={(e) =>
                        handleConfigChange("arbitrumRpc", e.target.value)
                      }
                      placeholder="https://arb1.arbitrum.io/rpc"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Optimism RPC URL</Label>
                    <Input
                      value={config.optimismRpc}
                      onChange={(e) =>
                        handleConfigChange("optimismRpc", e.target.value)
                      }
                      placeholder="https://mainnet.optimism.io"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Avalanche RPC URL</Label>
                    <Input
                      value={config.avalancheRpc}
                      onChange={(e) =>
                        handleConfigChange("avalancheRpc", e.target.value)
                      }
                      placeholder="https://api.avax.network/ext/bc/C/rpc"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Wallet Configuration Tab */}
          <TabsContent value="wallet">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Wallet className="h-5 w-5" />
                  <span>Wallet Configuration</span>
                </CardTitle>
                <CardDescription>
                  Configure wallet settings for transaction signing and real
                  trading
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Security Warning:</strong> Private keys are stored
                    locally and encrypted. Never share your private key with
                    anyone.
                  </AlertDescription>
                </Alert>

                <div className="space-y-6">
                  <SecretInput
                    label="Private Key"
                    value={config.privateKey}
                    onChange={(value) =>
                      handleConfigChange("privateKey", value)
                    }
                    placeholder="0x..."
                    field="privateKey"
                  />

                  <div className="space-y-2">
                    <Label>Wallet Address</Label>
                    <div className="relative">
                      <Input
                        value={config.walletAddress}
                        onChange={(e) =>
                          handleConfigChange("walletAddress", e.target.value)
                        }
                        placeholder="0x..."
                        className="pr-10"
                      />
                      {config.walletAddress && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            copyToClipboard(
                              config.walletAddress,
                              "Wallet Address",
                            )
                          }
                          className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>

                  {config.privateKey && config.walletAddress && (
                    <Alert>
                      <CheckCircle className="h-4 w-4" />
                      <AlertDescription>
                        Wallet configuration is complete. You can now perform
                        real transactions.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bell className="h-5 w-5" />
                  <span>Notification Settings</span>
                </CardTitle>
                <CardDescription>
                  Configure notification channels for alerts and reports
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-6">
                  {/* Email Notifications */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-base">Email Notifications</Label>
                        <p className="text-sm text-muted-foreground">
                          Receive alerts via email
                        </p>
                      </div>
                      <Switch
                        checked={config.emailNotifications}
                        onCheckedChange={(checked) =>
                          handleConfigChange("emailNotifications", checked)
                        }
                      />
                    </div>
                    {config.emailNotifications && (
                      <div className="space-y-2">
                        <Label>Email Address</Label>
                        <Input
                          type="email"
                          value={config.emailAddress}
                          onChange={(e) =>
                            handleConfigChange("emailAddress", e.target.value)
                          }
                          placeholder="your@email.com"
                        />
                      </div>
                    )}
                  </div>

                  <Separator />

                  {/* Slack Configuration */}
                  <div className="space-y-4">
                    <Label className="text-base">Slack Integration</Label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <SecretInput
                        label="Slack Webhook URL"
                        value={config.slackWebhook}
                        onChange={(value) =>
                          handleConfigChange("slackWebhook", value)
                        }
                        placeholder="https://hooks.slack.com/services/..."
                        field="slackWebhook"
                      />
                      <div className="space-y-2">
                        <Label>Slack Channel</Label>
                        <Input
                          value={config.slackChannel}
                          onChange={(e) =>
                            handleConfigChange("slackChannel", e.target.value)
                          }
                          placeholder="#security-alerts"
                        />
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Telegram Configuration */}
                  <div className="space-y-4">
                    <Label className="text-base">Telegram Integration</Label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <SecretInput
                        label="Telegram Bot Token"
                        value={config.telegramBotToken}
                        onChange={(value) =>
                          handleConfigChange("telegramBotToken", value)
                        }
                        placeholder="1234567890:ABCdefGHI..."
                        field="telegramBotToken"
                      />
                      <div className="space-y-2">
                        <Label>Telegram Chat ID</Label>
                        <Input
                          value={config.telegramChatId}
                          onChange={(e) =>
                            handleConfigChange("telegramChatId", e.target.value)
                          }
                          placeholder="-1001234567890"
                        />
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Discord Configuration */}
                  <div className="space-y-4">
                    <Label className="text-base">Discord Integration</Label>
                    <SecretInput
                      label="Discord Webhook URL"
                      value={config.discordWebhook}
                      onChange={(value) =>
                        handleConfigChange("discordWebhook", value)
                      }
                      placeholder="https://discord.com/api/webhooks/..."
                      field="discordWebhook"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Plugins Tab */}
          <TabsContent value="plugins">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Cpu className="h-5 w-5" />
                  <span>Security Analysis Plugins</span>
                </CardTitle>
                <CardDescription>
                  Enable or disable security analysis tools and plugins
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(config.plugins).map(([plugin, enabled]) => (
                    <div
                      key={plugin}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div>
                        <Label className="text-base capitalize">{plugin}</Label>
                        <p className="text-sm text-muted-foreground">
                          {plugin === "slither" &&
                            "Static analysis security framework"}
                          {plugin === "mythx" &&
                            "Professional security analysis"}
                          {plugin === "manticore" &&
                            "Symbolic execution engine"}
                          {plugin === "mythril" && "Security analysis tool"}
                          {plugin === "echidna" && "Property-based fuzzer"}
                        </p>
                      </div>
                      <Switch
                        checked={enabled}
                        onCheckedChange={(checked) =>
                          handlePluginChange(
                            plugin as keyof SystemConfig["plugins"],
                            checked,
                          )
                        }
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* System Settings Tab */}
          <TabsContent value="system">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>System Settings</span>
                </CardTitle>
                <CardDescription>
                  Configure system behavior, performance, and advanced options
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-6">
                  {/* System Toggles */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-base">Auto Scan</Label>
                        <p className="text-sm text-muted-foreground">
                          Automatically scan new contracts
                        </p>
                      </div>
                      <Switch
                        checked={config.autoScan}
                        onCheckedChange={(checked) =>
                          handleConfigChange("autoScan", checked)
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-base">
                          Real-time Monitoring
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          Monitor mempool in real-time
                        </p>
                      </div>
                      <Switch
                        checked={config.realTimeMonitoring}
                        onCheckedChange={(checked) =>
                          handleConfigChange("realTimeMonitoring", checked)
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-base">Advanced Logging</Label>
                        <p className="text-sm text-muted-foreground">
                          Enable detailed system logs
                        </p>
                      </div>
                      <Switch
                        checked={config.advancedLogging}
                        onCheckedChange={(checked) =>
                          handleConfigChange("advancedLogging", checked)
                        }
                      />
                    </div>
                  </div>

                  <Separator />

                  {/* Performance Settings */}
                  <div className="space-y-4">
                    <Label className="text-base">Performance Settings</Label>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>API Rate Limit (requests/minute)</Label>
                        <Input
                          type="number"
                          value={config.apiRateLimit}
                          onChange={(e) =>
                            handleConfigChange(
                              "apiRateLimit",
                              parseInt(e.target.value) || 100,
                            )
                          }
                          min={1}
                          max={1000}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Max Concurrent Scans</Label>
                        <Input
                          type="number"
                          value={config.maxConcurrentScans}
                          onChange={(e) =>
                            handleConfigChange(
                              "maxConcurrentScans",
                              parseInt(e.target.value) || 3,
                            )
                          }
                          min={1}
                          max={10}
                        />
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Danger Zone */}
                  <div className="space-y-4 p-4 border-2 border-red-200 rounded-lg bg-red-50">
                    <div className="flex items-center space-x-2 text-red-600">
                      <AlertTriangle className="h-5 w-5" />
                      <Label className="text-base font-semibold">
                        Danger Zone
                      </Label>
                    </div>
                    <p className="text-sm text-red-600">
                      These actions will permanently delete all your data and
                      cannot be undone.
                    </p>
                    <Button
                      variant="destructive"
                      onClick={clearAllData}
                      className="w-full"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Clear All Data
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </PageLayout>
  );
};

export default Settings;
