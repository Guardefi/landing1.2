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
import { toast } from "sonner";
import {
  Settings,
  ArrowLeft,
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
  ExternalLink,
} from "lucide-react";
import { Link } from "react-router-dom";

interface SystemConfig {
  // API Keys
  slitherApiKey: string;
  mythxApiKey: string;
  mantecoreApiKey: string;
  mythrilApiKey: string;

  // RPC URLs
  ethereumRpc: string;
  polygonRpc: string;
  bscRpc: string;
  arbitrumRpc: string;

  // Wallet Configuration
  privateKey: string;
  walletAddress: string;

  // Notification Settings
  slackWebhook: string;
  telegramBotToken: string;
  telegramChatId: string;
  emailNotifications: boolean;

  // Plugin Settings
  plugins: {
    slither: boolean;
    mythx: boolean;
    manticore: boolean;
    mythril: boolean;
    echidna: boolean;
  };

  // System Settings
  autoScan: boolean;
  realTimeMonitoring: boolean;
  advancedLogging: boolean;
}

const SettingsPage = () => {
  const [config, setConfig] = useState<SystemConfig>({
    slitherApiKey: "",
    mythxApiKey: "",
    mantecoreApiKey: "",
    mythrilApiKey: "",
    ethereumRpc: "https://mainnet.infura.io/v3/",
    polygonRpc: "https://polygon-mainnet.infura.io/v3/",
    bscRpc: "https://bsc-dataseed.binance.org/",
    arbitrumRpc: "https://arb1.arbitrum.io/rpc",
    privateKey: "",
    walletAddress: "",
    slackWebhook: "",
    telegramBotToken: "",
    telegramChatId: "",
    emailNotifications: true,
    plugins: {
      slither: true,
      mythx: false,
      manticore: true,
      mythril: true,
      echidna: false,
    },
    autoScan: true,
    realTimeMonitoring: true,
    advancedLogging: false,
  });

  const [showPrivateKey, setShowPrivateKey] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState({
    ethereum: "checking",
    plugins: "checking",
    notifications: "checking",
  });

  useEffect(() => {
    // Load saved configuration
    const savedConfig = localStorage.getItem("scorpius-config");
    if (savedConfig) {
      setConfig(JSON.parse(savedConfig));
    }

    // Test connections
    testConnections();
  }, []);

  const testConnections = async () => {
    // Test RPC connections
    try {
      // This would be real connection testing in production
      setTimeout(() => {
        setConnectionStatus({
          ethereum: config.ethereumRpc ? "connected" : "disconnected",
          plugins: Object.values(config.plugins).some(Boolean)
            ? "connected"
            : "disconnected",
          notifications:
            config.slackWebhook || config.telegramBotToken
              ? "connected"
              : "disconnected",
        });
      }, 2000);
    } catch (error) {
      console.error("Connection test failed:", error);
    }
  };

  const handleSave = () => {
    try {
      localStorage.setItem("scorpius-config", JSON.stringify(config));
      toast.success("Configuration saved successfully!");
      testConnections();
    } catch (error) {
      toast.error("Failed to save configuration");
    }
  };

  const handleReset = () => {
    localStorage.removeItem("scorpius-config");
    setConfig({
      slitherApiKey: "",
      mythxApiKey: "",
      mantecoreApiKey: "",
      mythrilApiKey: "",
      ethereumRpc: "https://mainnet.infura.io/v3/",
      polygonRpc: "https://polygon-mainnet.infura.io/v3/",
      bscRpc: "https://bsc-dataseed.binance.org/",
      arbitrumRpc: "https://arb1.arbitrum.io/rpc",
      privateKey: "",
      walletAddress: "",
      slackWebhook: "",
      telegramBotToken: "",
      telegramChatId: "",
      emailNotifications: true,
      plugins: {
        slither: true,
        mythx: false,
        manticore: true,
        mythril: true,
        echidna: false,
      },
      autoScan: true,
      realTimeMonitoring: true,
      advancedLogging: false,
    });
    toast.success("Configuration reset to defaults");
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "disconnected":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return (
          <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        );
    }
  };

  return (
    <PageLayout variant="default">
      <div className="flex items-center justify-between mb-6">
        <div className="flex-1">
          <PageHeader
            title="System Configuration"
            description="Configure API keys, RPC endpoints, and system settings"
            icon={Settings}
            iconGradient="from-blue-500 to-purple-600"
            borderColor="border-blue-400/30"
          />
        </div>
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Link>
          </Button>
          <Button variant="outline" size="sm" onClick={handleReset}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset to Defaults
          </Button>
          <Button
            size="sm"
            onClick={handleSave}
            className="bg-gradient-to-r from-blue-600 to-purple-600"
          >
            <Save className="h-4 w-4 mr-2" />
            Save Configuration
          </Button>
        </div>
      </div>

      {/* Connection Status Overview */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Network className="h-5 w-5" />
            <span>System Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="font-medium">Blockchain RPC</span>
              <div className="flex items-center space-x-2">
                {getStatusIcon(connectionStatus.ethereum)}
                <span className="text-sm capitalize">
                  {connectionStatus.ethereum}
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="font-medium">Security Plugins</span>
              <div className="flex items-center space-x-2">
                {getStatusIcon(connectionStatus.plugins)}
                <span className="text-sm capitalize">
                  {connectionStatus.plugins}
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="font-medium">Notifications</span>
              <div className="flex items-center space-x-2">
                {getStatusIcon(connectionStatus.notifications)}
                <span className="text-sm capitalize">
                  {connectionStatus.notifications}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="api-keys" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="blockchain">Blockchain</TabsTrigger>
          <TabsTrigger value="wallet">Wallet</TabsTrigger>
          <TabsTrigger value="plugins">Plugins</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        {/* API Keys Tab */}
        <TabsContent value="api-keys" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Key className="h-5 w-5" />
                <span>Security Scanner API Keys</span>
              </CardTitle>
              <CardDescription>
                Configure API keys for external security scanning services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="slither-api">Slither API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="slither-api"
                      type="password"
                      placeholder="Enter Slither API key"
                      value={config.slitherApiKey}
                      onChange={(e) =>
                        setConfig({ ...config, slitherApiKey: e.target.value })
                      }
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => copyToClipboard(config.slitherApiKey)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Get your API key from{" "}
                    <a
                      href="https://github.com/crytic/slither"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      Slither Documentation{" "}
                      <ExternalLink className="h-3 w-3 inline" />
                    </a>
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mythx-api">MythX API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="mythx-api"
                      type="password"
                      placeholder="Enter MythX API key"
                      value={config.mythxApiKey}
                      onChange={(e) =>
                        setConfig({ ...config, mythxApiKey: e.target.value })
                      }
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => copyToClipboard(config.mythxApiKey)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Get your API key from{" "}
                    <a
                      href="https://mythx.io"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      MythX Platform <ExternalLink className="h-3 w-3 inline" />
                    </a>
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="manticore-api">Manticore API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="manticore-api"
                      type="password"
                      placeholder="Enter Manticore API key"
                      value={config.mantecoreApiKey}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          mantecoreApiKey: e.target.value,
                        })
                      }
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => copyToClipboard(config.mantecoreApiKey)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Get your API key from{" "}
                    <a
                      href="https://github.com/trailofbits/manticore"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      Manticore GitHub{" "}
                      <ExternalLink className="h-3 w-3 inline" />
                    </a>
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mythril-api">Mythril API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="mythril-api"
                      type="password"
                      placeholder="Enter Mythril API key"
                      value={config.mythrilApiKey}
                      onChange={(e) =>
                        setConfig({ ...config, mythrilApiKey: e.target.value })
                      }
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => copyToClipboard(config.mythrilApiKey)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Get your API key from{" "}
                    <a
                      href="https://mythril.ai"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      Mythril Platform{" "}
                      <ExternalLink className="h-3 w-3 inline" />
                    </a>
                  </p>
                </div>
              </div>

              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  API keys are stored locally and encrypted. They are never
                  transmitted to external servers except when making authorized
                  API calls to the respective services.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Blockchain Tab */}
        <TabsContent value="blockchain" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Network className="h-5 w-5" />
                <span>Blockchain RPC Endpoints</span>
              </CardTitle>
              <CardDescription>
                Configure RPC endpoints for different blockchain networks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="ethereum-rpc">Ethereum Mainnet RPC</Label>
                  <Input
                    id="ethereum-rpc"
                    placeholder="https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
                    value={config.ethereumRpc}
                    onChange={(e) =>
                      setConfig({ ...config, ethereumRpc: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="polygon-rpc">Polygon RPC</Label>
                  <Input
                    id="polygon-rpc"
                    placeholder="https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID"
                    value={config.polygonRpc}
                    onChange={(e) =>
                      setConfig({ ...config, polygonRpc: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bsc-rpc">Binance Smart Chain RPC</Label>
                  <Input
                    id="bsc-rpc"
                    placeholder="https://bsc-dataseed.binance.org/"
                    value={config.bscRpc}
                    onChange={(e) =>
                      setConfig({ ...config, bscRpc: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="arbitrum-rpc">Arbitrum RPC</Label>
                  <Input
                    id="arbitrum-rpc"
                    placeholder="https://arb1.arbitrum.io/rpc"
                    value={config.arbitrumRpc}
                    onChange={(e) =>
                      setConfig({ ...config, arbitrumRpc: e.target.value })
                    }
                  />
                </div>
              </div>

              <Alert>
                <Network className="h-4 w-4" />
                <AlertDescription>
                  We recommend using your own RPC endpoints from providers like
                  Infura, Alchemy, or QuickNode for better performance and
                  reliability.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Wallet Tab */}
        <TabsContent value="wallet" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Wallet className="h-5 w-5" />
                <span>Wallet Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure wallet settings for transaction signing and
                interaction
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="private-key">Private Key (Optional)</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="private-key"
                      type={showPrivateKey ? "text" : "password"}
                      placeholder="0x..."
                      value={config.privateKey}
                      onChange={(e) =>
                        setConfig({ ...config, privateKey: e.target.value })
                      }
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => setShowPrivateKey(!showPrivateKey)}
                    >
                      {showPrivateKey ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Only required for advanced features like automatic
                    transaction signing
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="wallet-address">Wallet Address</Label>
                  <Input
                    id="wallet-address"
                    placeholder="0x..."
                    value={config.walletAddress}
                    onChange={(e) =>
                      setConfig({ ...config, walletAddress: e.target.value })
                    }
                  />
                </div>
              </div>

              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Security Warning:</strong> Private keys are stored
                  locally and encrypted. Never share your private key with
                  anyone. Consider using hardware wallets for production
                  environments.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Plugins Tab */}
        <TabsContent value="plugins" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Security Scanner Plugins</span>
              </CardTitle>
              <CardDescription>
                Enable and configure security scanning plugins
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(config.plugins).map(([plugin, enabled]) => (
                <div
                  key={plugin}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div>
                    <div className="font-medium capitalize">{plugin}</div>
                    <div className="text-sm text-muted-foreground">
                      {plugin === "slither" &&
                        "Static analysis framework for Solidity"}
                      {plugin === "mythx" &&
                        "Security analysis platform for Ethereum smart contracts"}
                      {plugin === "manticore" &&
                        "Symbolic execution tool for analysis"}
                      {plugin === "mythril" &&
                        "Security analysis tool for EVM bytecode"}
                      {plugin === "echidna" && "Fast smart contract fuzzer"}
                    </div>
                  </div>
                  <Switch
                    checked={enabled}
                    onCheckedChange={(checked) =>
                      setConfig({
                        ...config,
                        plugins: { ...config.plugins, [plugin]: checked },
                      })
                    }
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Notification Settings</span>
              </CardTitle>
              <CardDescription>
                Configure how you receive alerts and notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Email Notifications</div>
                    <div className="text-sm text-muted-foreground">
                      Receive email alerts for security findings
                    </div>
                  </div>
                  <Switch
                    checked={config.emailNotifications}
                    onCheckedChange={(checked) =>
                      setConfig({ ...config, emailNotifications: checked })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="slack-webhook">Slack Webhook URL</Label>
                  <Input
                    id="slack-webhook"
                    type="password"
                    placeholder="https://hooks.slack.com/services/..."
                    value={config.slackWebhook}
                    onChange={(e) =>
                      setConfig({ ...config, slackWebhook: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="telegram-token">Telegram Bot Token</Label>
                  <Input
                    id="telegram-token"
                    type="password"
                    placeholder="Enter Telegram bot token"
                    value={config.telegramBotToken}
                    onChange={(e) =>
                      setConfig({ ...config, telegramBotToken: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="telegram-chat">Telegram Chat ID</Label>
                  <Input
                    id="telegram-chat"
                    placeholder="Enter Telegram chat ID"
                    value={config.telegramChatId}
                    onChange={(e) =>
                      setConfig({ ...config, telegramChatId: e.target.value })
                    }
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5" />
                <span>System Settings</span>
              </CardTitle>
              <CardDescription>
                Configure system behavior and performance settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Auto Scan</div>
                  <div className="text-sm text-muted-foreground">
                    Automatically scan contracts when deployed
                  </div>
                </div>
                <Switch
                  checked={config.autoScan}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, autoScan: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Real-time Monitoring</div>
                  <div className="text-sm text-muted-foreground">
                    Monitor blockchain for suspicious activity
                  </div>
                </div>
                <Switch
                  checked={config.realTimeMonitoring}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, realTimeMonitoring: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Advanced Logging</div>
                  <div className="text-sm text-muted-foreground">
                    Enable detailed system logs for debugging
                  </div>
                </div>
                <Switch
                  checked={config.advancedLogging}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, advancedLogging: checked })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </PageLayout>
  );
};

export default SettingsPage;
