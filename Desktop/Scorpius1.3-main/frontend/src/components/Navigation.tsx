import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTeamChat, useNotifications } from "@/hooks";
import { Link, useLocation } from "react-router-dom";
import {
  Shield,
  Brain,
  Globe,
  BarChart3,
  Cpu,
  Activity,
  Search,
  Settings,
  Menu,
  X,
  ChevronRight,
  Zap,
  Monitor,
  Target,
  FileText,
  User,
  LogOut,
  ChevronDown,
  Bell,
  MessageCircle,
  AlertTriangle,
  CheckCircle,
  Clock,
  Send,
  Users,
  Slack,
  MessageSquare,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

interface NavigationProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const Navigation = ({ isOpen, setIsOpen }: NavigationProps) => {
  const location = useLocation();
  const [activeModule, setActiveModule] = useState("");
  const [chatMessage, setChatMessage] = useState("");

  // Real API hooks
  const { data: teamChatData, sendMessage } = useTeamChat();
  const { data: notificationsData, markAsRead: markNotificationsAsRead } =
    useNotifications();

  // Safely extract data with defaults
  const chatMessages = teamChatData?.messages || [];
  const unreadMessages = teamChatData?.unreadCount || 0;
  const notifications = notificationsData?.notifications || [];
  const unreadNotifications = notificationsData?.unreadCount || 0;

  const handleSendMessage = async () => {
    if (chatMessage.trim()) {
      try {
        await sendMessage(chatMessage.trim());
        setChatMessage("");
      } catch (error) {
        console.error("Failed to send message:", error);
        // Fallback: still clear the input for better UX
        setChatMessage("");
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Transform chat messages for display
  const displayChatMessages = chatMessages.map((msg) => ({
    id: msg.id,
    user: msg.sender || "Unknown",
    avatar: (msg.sender || "U")
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase(),
    message: msg.text || "",
    time: new Date(msg.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
    online: true, // Default to online for simplicity
  }));

  // Transform notifications for display
  const displayNotifications = notifications.map((notif) => ({
    id: notif.id,
    type: notif.type,
    title: notif.title,
    message: notif.message,
    time: notif.time,
    read: notif.read,
    source: notif.source,
    icon:
      notif.type === "security"
        ? AlertTriangle
        : notif.type === "slack"
          ? Slack
          : notif.type === "telegram"
            ? MessageSquare
            : CheckCircle,
    color:
      notif.type === "security"
        ? "text-red-500"
        : notif.type === "slack"
          ? "text-purple-500"
          : notif.type === "telegram"
            ? "text-blue-500"
            : "text-green-500",
  }));

  const navigationItems = [
    {
      id: "overview",
      label: "Command Center",
      icon: Activity,
      path: "/",
      description: "System overview and metrics",
      color: "cyan",
    },
    {
      id: "scanner",
      label: "Vulnerability Scanner",
      icon: Search,
      path: "/scanner",
      description: "AI-powered security analysis",
      color: "red",
    },

    {
      id: "security",
      label: "Security Operations",
      icon: Shield,
      path: "/security/elite",
      description: "Threat detection & response",
      color: "orange",
    },
    {
      id: "trading",
      label: "AI Trading Engine",
      icon: Brain,
      path: "/trading/ai",
      description: "Automated trading strategies",
      color: "green",
    },
    {
      id: "bridge",
      label: "Bridge Network",
      icon: Globe,
      path: "/bridge/network",
      description: "Cross-chain operations",
      color: "purple",
    },
    {
      id: "analytics",
      label: "Analytics Platform",
      icon: BarChart3,
      path: "/analytics/enterprise",
      description: "Business intelligence",
      color: "blue",
    },
    {
      id: "computing",
      label: "Computing Cluster",
      icon: Cpu,
      path: "/computing/cluster",
      description: "Distributed processing",
      color: "cyan",
    },
    {
      id: "monitoring",
      label: "Grafana Monitoring",
      icon: Activity,
      path: "/monitoring/grafana",
      description: "Real-time dashboards & metrics",
      color: "amber",
    },
    {
      id: "mempool",
      label: "Mempool Monitor",
      icon: Monitor,
      path: "/mempool/monitor",
      description: "Real-time transaction monitoring",
      color: "purple",
    },
    {
      id: "simulation",
      label: "Simulation Sandbox",
      icon: Target,
      path: "/simulation",
      description: "Attack simulation testing",
      color: "red",
    },
    {
      id: "subscription",
      label: "Subscription",
      icon: Zap,
      path: "/subscription",
      description: "Manage your plan and usage",
      color: "yellow",
    },
    {
      id: "reports",
      label: "Enterprise Reports",
      icon: FileText,
      path: "/reports/enterprise",
      description: "Security audit reporting system",
      color: "indigo",
    },
  ];

  const getColorClasses = (color: string, isActive: boolean) => {
    const colors = {
      cyan: {
        bg: isActive ? "bg-cyan-500/20" : "hover:bg-cyan-500/10",
        border: isActive ? "border-cyan-400/50" : "border-cyan-400/20",
        text: isActive ? "text-cyan-400" : "text-cyan-400/70",
        glow: isActive ? "shadow-cyan-500/20" : "",
      },
      red: {
        bg: isActive ? "bg-red-500/20" : "hover:bg-red-500/10",
        border: isActive ? "border-red-400/50" : "border-red-400/20",
        text: isActive ? "text-red-400" : "text-red-400/70",
        glow: isActive ? "shadow-red-500/20" : "",
      },
      orange: {
        bg: isActive ? "bg-orange-500/20" : "hover:bg-orange-500/10",
        border: isActive ? "border-orange-400/50" : "border-orange-400/20",
        text: isActive ? "text-orange-400" : "text-orange-400/70",
        glow: isActive ? "shadow-orange-500/20" : "",
      },
      green: {
        bg: isActive ? "bg-green-500/20" : "hover:bg-green-500/10",
        border: isActive ? "border-green-400/50" : "border-green-400/20",
        text: isActive ? "text-green-400" : "text-green-400/70",
        glow: isActive ? "shadow-green-500/20" : "",
      },
      purple: {
        bg: isActive ? "bg-purple-500/20" : "hover:bg-purple-500/10",
        border: isActive ? "border-purple-400/50" : "border-purple-400/20",
        text: isActive ? "text-purple-400" : "text-purple-400/70",
        glow: isActive ? "shadow-purple-500/20" : "",
      },
      blue: {
        bg: isActive ? "bg-blue-500/20" : "hover:bg-blue-500/10",
        border: isActive ? "border-blue-400/50" : "border-blue-400/20",
        text: isActive ? "text-blue-400" : "text-blue-400/70",
        glow: isActive ? "shadow-blue-500/20" : "",
      },
      amber: {
        bg: isActive ? "bg-amber-500/20" : "hover:bg-amber-500/10",
        border: isActive ? "border-amber-400/50" : "border-amber-400/20",
        text: isActive ? "text-amber-400" : "text-amber-400/70",
        glow: isActive ? "shadow-amber-500/20" : "",
      },
    };
    return colors[color as keyof typeof colors] || colors.cyan;
  };

  useEffect(() => {
    const currentItem = navigationItems.find((item) =>
      item.path === "/"
        ? location.pathname === "/"
        : location.pathname.startsWith(item.path),
    );
    if (currentItem) {
      setActiveModule(currentItem.id);
    }
  }, [location.pathname]);

  return (
    <>
      {/* Top Header Bar */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 left-0 right-0 z-40 h-12 glass border-b border-cyan-400/20"
      >
        <div className="flex items-center justify-between h-full px-4">
          {/* Left Side - Menu and Chat */}
          <div className="flex items-center space-x-2">
            {/* Menu Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-lg border border-cyan-400/30 hover:bg-cyan-500/10 transition-all"
            >
              <AnimatePresence mode="wait">
                {isOpen ? (
                  <motion.div
                    key="close"
                    initial={{ rotate: -90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: 90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <X size={16} className="text-cyan-400" />
                  </motion.div>
                ) : (
                  <motion.div
                    key="menu"
                    initial={{ rotate: 90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: -90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Menu size={16} className="text-cyan-400" />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>

            {/* Team Chat Button */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative p-2 rounded-lg border border-cyan-400/30 hover:bg-cyan-500/10 transition-all"
                >
                  <MessageCircle size={16} className="text-cyan-400" />
                  {unreadMessages > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                      {unreadMessages}
                    </span>
                  )}
                </motion.button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-80">
                <div className="p-3 border-b">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">Security Team Chat</h3>
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-xs text-muted-foreground">
                        4 online
                      </span>
                    </div>
                  </div>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {displayChatMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className="p-3 hover:bg-muted/50 border-b last:border-b-0"
                    >
                      <div className="flex items-start space-x-3">
                        <div className="relative">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white text-xs font-semibold">
                            {msg.avatar}
                          </div>
                          {msg.online && (
                            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-background"></div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium">
                              {msg.user}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {msg.time}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">
                            {msg.message}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-3 border-t">
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      placeholder="Type a message..."
                      value={chatMessage}
                      onChange={(e) => setChatMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="flex-1 px-3 py-2 text-sm bg-muted rounded-lg border focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    />
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleSendMessage}
                      disabled={!chatMessage.trim()}
                      className="p-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Send size={14} />
                    </motion.button>
                  </div>
                </div>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Header Title */}
          <div className="flex items-center space-x-2">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              className="text-cyan-400"
            >
              <path
                d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
              />
            </svg>
            <span className="text-xl font-semibold text-white ml-2">
              <h1>Scorpius </h1>
            </span>
          </div>

          {/* Right Side - Notifications and Profile */}
          <div className="flex items-center space-x-2">
            {/* Notifications Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative p-2 rounded-lg border border-cyan-400/30 hover:bg-cyan-500/10 transition-all"
                  onClick={() =>
                    markNotificationsAsRead(
                      displayNotifications
                        .filter((n) => !n.read)
                        .map((n) => n.id),
                    )
                  }
                >
                  <Bell size={16} className="text-cyan-400" />
                  {unreadNotifications > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                      {unreadNotifications}
                    </span>
                  )}
                </motion.button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <div className="p-3 border-b">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">Notifications</h3>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-muted-foreground">
                        {unreadNotifications} unread
                      </span>
                    </div>
                  </div>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {displayNotifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-3 hover:bg-muted/50 border-b last:border-b-0 ${
                        !notification.read ? "bg-cyan-500/5" : ""
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div
                          className={`p-2 rounded-lg ${
                            notification.type === "security"
                              ? "bg-red-500/10"
                              : notification.type === "slack"
                                ? "bg-purple-500/10"
                                : notification.type === "telegram"
                                  ? "bg-blue-500/10"
                                  : "bg-green-500/10"
                          }`}
                        >
                          <notification.icon
                            className={`h-4 w-4 ${notification.color}`}
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium">
                              {notification.title}
                            </p>
                            {!notification.read && (
                              <div className="w-2 h-2 bg-cyan-500 rounded-full"></div>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">
                            {notification.message}
                          </p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-muted-foreground">
                              {notification.time}
                            </span>
                            <div className="flex items-center space-x-1">
                              {notification.source === "Slack" && (
                                <Slack className="h-3 w-3 text-purple-500" />
                              )}
                              {notification.source === "Telegram" && (
                                <MessageSquare className="h-3 w-3 text-blue-500" />
                              )}
                              <span className="text-xs text-muted-foreground">
                                {notification.source}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-3 border-t">
                  <button className="w-full text-sm text-cyan-500 hover:text-cyan-400 transition-colors">
                    View all notifications
                  </button>
                </div>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Profile Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center space-x-2 p-2 rounded-lg border border-cyan-400/30 hover:bg-cyan-500/10 transition-all"
                >
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                    <User className="h-3 w-3 text-white" />
                  </div>
                  <ChevronDown className="h-3 w-3 text-cyan-400" />
                </motion.button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <div className="px-3 py-2">
                  <p className="text-sm font-medium">Admin User</p>
                  <p className="text-xs text-muted-foreground">
                    admin@scorpius.dev
                  </p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/settings" className="flex items-center">
                    <Settings className="h-4 w-4 mr-2" />
                    Settings
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-red-600 focus:text-red-600">
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </motion.header>

      {/* Navigation Sidebar */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Mobile Overlay */}
            {isOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsOpen(false)}
                className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
              />
            )}

            {/* Sidebar */}
            <motion.aside
              initial={{ x: -320, opacity: 0 }}
              animate={{
                x: 0,
                opacity: 1,
              }}
              exit={{ x: -320, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed left-0 top-12 h-[calc(100vh-3rem)] w-80 z-50 glass border-r border-cyan-400/20 overflow-hidden"
            >
              {/* Header */}
              <div className="p-6 border-b border-cyan-400/20">
                <motion.div
                  className="flex items-center space-x-3"
                  initial={{ y: -20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 glow-cyan">
                    <Shield className="h-6 w-6 text-white" />
                  </div>
                  <AnimatePresence>
                    {isOpen && (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.2 }}
                      >
                        <h1 className="text-xl font-bold text-white">
                          Scorpius X
                        </h1>
                        <p className="text-xs text-gray-400">
                          Enterprise Command Center
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </div>

              {/* Navigation Items */}
              <div className="p-4 space-y-2 overflow-y-auto h-full pb-20">
                {navigationItems.map((item, index) => {
                  const isActive = activeModule === item.id;
                  const colorClasses = getColorClasses(item.color, isActive);
                  const isExpanded = isOpen;

                  return (
                    <motion.div
                      key={item.id}
                      initial={{ x: -50, opacity: 0 }}
                      animate={{
                        x: 0,
                        opacity: 1,
                        transition: { delay: isExpanded ? 0.1 * index : 0 },
                      }}
                      transition={{
                        duration: 0.3,
                        delay: isExpanded ? 0.1 * index : 0,
                        type: "spring",
                        stiffness: 300,
                        damping: 25,
                      }}
                    >
                      <Link
                        to={item.path}
                        onClick={() => setIsOpen(false)}
                        className={`
                          group relative flex items-center ${isExpanded ? "p-4" : "p-3 justify-center"} rounded-xl border transition-all duration-200
                          ${colorClasses.bg} ${colorClasses.border} ${colorClasses.glow}
                          ${isActive ? "shadow-lg" : "hover:shadow-md"}
                        `}
                      >
                        <div
                          className={`p-2 rounded-lg ${colorClasses.bg} border ${colorClasses.border}`}
                        >
                          <item.icon
                            className={`h-4 w-4 ${colorClasses.text}`}
                          />
                        </div>

                        <AnimatePresence>
                          {isExpanded && (
                            <motion.div
                              className="ml-3 flex-1"
                              initial={{ opacity: 0, width: 0 }}
                              animate={{ opacity: 1, width: "auto" }}
                              exit={{ opacity: 0, width: 0 }}
                              transition={{ duration: 0.2, delay: 0.1 }}
                            >
                              <div
                                className={`font-medium ${colorClasses.text} group-hover:text-white transition-colors whitespace-nowrap`}
                              >
                                {item.label}
                              </div>
                              <div className="text-xs text-gray-500 group-hover:text-gray-400 transition-colors whitespace-nowrap">
                                {item.description}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>

                        <AnimatePresence>
                          {isExpanded && (
                            <motion.div
                              initial={{ opacity: 0, scale: 0 }}
                              animate={{ opacity: 1, scale: 1 }}
                              exit={{ opacity: 0, scale: 0 }}
                              transition={{ duration: 0.2, delay: 0.15 }}
                            >
                              <ChevronRight
                                className={`h-4 w-4 ${colorClasses.text} group-hover:text-white transition-all ${
                                  isActive ? "translate-x-1" : ""
                                }`}
                              />
                            </motion.div>
                          )}
                        </AnimatePresence>

                        {/* Active indicator */}
                        {isActive && (
                          <motion.div
                            layoutId="activeIndicator"
                            className={`absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-${item.color}-400 to-${item.color}-600 rounded-r-full`}
                            transition={{
                              type: "spring",
                              damping: 25,
                              stiffness: 300,
                            }}
                          />
                        )}

                        {/* Scan line effect for active item */}
                        {isActive && (
                          <motion.div
                            className="absolute inset-0 rounded-xl overflow-hidden"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                          >
                            <div className="scan-line opacity-30" />
                          </motion.div>
                        )}
                      </Link>
                    </motion.div>
                  );
                })}

                {/* Settings at bottom */}
                <motion.div
                  initial={{ x: -50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.1 * navigationItems.length }}
                  className="pt-4 mt-4 border-t border-cyan-400/20"
                >
                  <Link
                    to="/settings"
                    onClick={() => setIsOpen(false)}
                    className={`group flex items-center ${isOpen ? "p-4" : "p-3 justify-center"} rounded-xl border border-gray-600/30 hover:bg-gray-600/10 hover:border-gray-400/50 transition-all duration-200`}
                  >
                    <div className="p-2 rounded-lg bg-gray-600/20 border border-gray-500/30">
                      <Settings className="h-4 w-4 text-gray-400" />
                    </div>
                    <AnimatePresence>
                      {isOpen && (
                        <motion.div
                          className="ml-3 flex-1"
                          initial={{ opacity: 0, width: 0 }}
                          animate={{ opacity: 1, width: "auto" }}
                          exit={{ opacity: 0, width: 0 }}
                          transition={{ duration: 0.2, delay: 0.1 }}
                        >
                          <div className="font-medium text-gray-400 group-hover:text-white transition-colors whitespace-nowrap">
                            Settings
                          </div>
                          <div className="text-xs text-gray-600 group-hover:text-gray-500 transition-colors whitespace-nowrap">
                            System configuration
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </Link>
                </motion.div>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default Navigation;
