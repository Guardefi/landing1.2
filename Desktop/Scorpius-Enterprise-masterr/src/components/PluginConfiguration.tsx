import { useState } from "react";
import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Settings, Package, Plus, Trash2 } from "lucide-react";

interface Plugin {
  id: string;
  name: string;
  enabled: boolean;
  description?: string;
  version?: string;
  isCustom?: boolean;
}

interface CustomPluginRow {
  id: string;
  name: string;
  enabled: boolean;
  isEditing: boolean;
}

const predefinedPlugins: Plugin[] = [
  {
    id: "slither",
    name: "Slither",
    enabled: true,
    description: "Static analysis framework for Solidity",
    version: "0.10.0",
  },
  {
    id: "manticore",
    name: "Manticore",
    enabled: true,
    description: "Symbolic execution tool for analysis of smart contracts",
    version: "0.3.7",
  },
  {
    id: "mythx",
    name: "MythX",
    enabled: false,
    description: "Security analysis platform for Ethereum smart contracts",
    version: "1.4.24",
  },
  {
    id: "mythril",
    name: "Mythril",
    enabled: true,
    description: "Security analysis tool for EVM bytecode",
    version: "0.24.8",
  },
  {
    id: "echidna",
    name: "Echidna",
    enabled: false,
    description: "Fast smart contract fuzzer",
    version: "2.2.3",
  },
  {
    id: "scorpius-ai",
    name: "Scorpius AI",
    enabled: true,
    description: "AI-powered vulnerability detection and analysis",
    version: "2.1.0",
  },
];

export const PluginConfiguration = () => {
  const [plugins, setPlugins] = useState<Plugin[]>(predefinedPlugins);
  const [useAllPlugins, setUseAllPlugins] = useState(false);
  const [customPlugins, setCustomPlugins] = useState<CustomPluginRow[]>([
    { id: "custom-1", name: "", enabled: false, isEditing: true },
    { id: "custom-2", name: "", enabled: false, isEditing: true },
    { id: "custom-3", name: "", enabled: false, isEditing: true },
  ]);

  const handlePluginToggle = (pluginId: string) => {
    setPlugins((prev) =>
      prev.map((plugin) =>
        plugin.id === pluginId
          ? { ...plugin, enabled: !plugin.enabled }
          : plugin,
      ),
    );
  };

  const handleUseAllPluginsToggle = () => {
    const newUseAllState = !useAllPlugins;
    setUseAllPlugins(newUseAllState);

    // Enable/disable all plugins based on "Use all plugins" state
    setPlugins((prev) =>
      prev.map((plugin) => ({ ...plugin, enabled: newUseAllState })),
    );

    setCustomPlugins((prev) =>
      prev.map((custom) => ({ ...custom, enabled: newUseAllState })),
    );
  };

  const handleCustomPluginNameChange = (id: string, name: string) => {
    setCustomPlugins((prev) =>
      prev.map((custom) => (custom.id === id ? { ...custom, name } : custom)),
    );
  };

  const handleCustomPluginToggle = (id: string) => {
    setCustomPlugins((prev) =>
      prev.map((custom) =>
        custom.id === id ? { ...custom, enabled: !custom.enabled } : custom,
      ),
    );
  };

  const addCustomPluginRow = () => {
    const newId = `custom-${Date.now()}`;
    setCustomPlugins((prev) => [
      ...prev,
      { id: newId, name: "", enabled: false, isEditing: true },
    ]);
  };

  const removeCustomPluginRow = (id: string) => {
    setCustomPlugins((prev) => prev.filter((custom) => custom.id !== id));
  };

  const getEnabledCount = () => {
    const enabledPredefined = plugins.filter((p) => p.enabled).length;
    const enabledCustom = customPlugins.filter(
      (c) => c.enabled && c.name.trim(),
    ).length;
    return enabledPredefined + enabledCustom;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <Card className="glass border border-purple-400/30">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-purple-400">
            <Package className="h-5 w-5" />
            <span>Plugin Configuration</span>
            <Badge
              variant="outline"
              className="border-purple-400 text-purple-400"
            >
              {getEnabledCount()} enabled
            </Badge>
          </CardTitle>
          <CardDescription>
            Configure security analysis plugins for vulnerability scanning
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Use All Plugins Toggle */}
          <div className="flex items-center justify-between p-4 glass border border-purple-400/20 rounded-lg">
            <div className="flex items-center space-x-3">
              <Settings className="h-5 w-5 text-purple-400" />
              <div>
                <Label className="text-white font-medium">
                  Use All Plugins
                </Label>
                <p className="text-sm text-gray-400">
                  Enable or disable all plugins at once
                </p>
              </div>
            </div>
            <Switch
              checked={useAllPlugins}
              onCheckedChange={handleUseAllPluginsToggle}
              className="data-[state=checked]:bg-purple-500"
            />
          </div>

          {/* Plugin Table */}
          <div className="border border-gray-600/30 rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="border-gray-600/30 hover:bg-gray-800/50">
                  <TableHead className="text-gray-300">Plugin Name</TableHead>
                  <TableHead className="text-gray-300">Description</TableHead>
                  <TableHead className="text-gray-300">Version</TableHead>
                  <TableHead className="text-gray-300 text-center">
                    Enabled
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {/* Predefined Plugins */}
                {plugins.map((plugin) => (
                  <TableRow
                    key={plugin.id}
                    className="border-gray-600/30 hover:bg-gray-800/50"
                  >
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <div className="font-medium text-white">
                          {plugin.name}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm text-gray-400">
                        {plugin.description}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className="border-gray-500 text-gray-300"
                      >
                        v{plugin.version}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      <Switch
                        checked={plugin.enabled}
                        onCheckedChange={() => handlePluginToggle(plugin.id)}
                        className="data-[state=checked]:bg-cyan-500"
                      />
                    </TableCell>
                  </TableRow>
                ))}

                {/* Separator Row */}
                <TableRow className="border-gray-600/50">
                  <TableCell colSpan={4} className="py-2">
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 h-px bg-gray-600/50" />
                      <span className="text-xs text-gray-500 font-medium">
                        CUSTOM PLUGINS
                      </span>
                      <div className="flex-1 h-px bg-gray-600/50" />
                    </div>
                  </TableCell>
                </TableRow>

                {/* Custom Plugin Rows */}
                {customPlugins.map((custom) => (
                  <TableRow
                    key={custom.id}
                    className="border-gray-600/30 hover:bg-gray-800/50"
                  >
                    <TableCell>
                      <Input
                        value={custom.name}
                        onChange={(e) =>
                          handleCustomPluginNameChange(
                            custom.id,
                            e.target.value,
                          )
                        }
                        placeholder="Enter plugin name..."
                        className="glass border-gray-600/50 text-white placeholder-gray-500 focus:border-cyan-400"
                      />
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-gray-500">
                        Custom plugin
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className="border-gray-600 text-gray-500"
                      >
                        custom
                      </Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex items-center justify-center space-x-2">
                        <Switch
                          checked={custom.enabled}
                          onCheckedChange={() =>
                            handleCustomPluginToggle(custom.id)
                          }
                          disabled={!custom.name.trim()}
                          className="data-[state=checked]:bg-cyan-500"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeCustomPluginRow(custom.id)}
                          className="h-8 w-8 p-0 text-gray-500 hover:text-red-400 hover:bg-red-500/10"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Add Custom Plugin Button */}
          <div className="flex justify-center">
            <Button
              variant="outline"
              onClick={addCustomPluginRow}
              className="border-gray-600/50 text-gray-400 hover:bg-gray-800/50 hover:text-white hover:border-gray-500"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Custom Plugin
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};
