import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  MessageSquare,
  X,
  Send,
  Users,
  Clock,
  Shield,
  Bot,
  AlertTriangle,
} from "lucide-react";

export interface ChatMessage {
  id: string;
  userId: string;
  username: string;
  avatar?: string;
  message: string;
  timestamp: Date;
  type: "message" | "system" | "alert" | "bot";
  metadata?: {
    contractAddress?: string;
    scanId?: string;
    severity?: "low" | "medium" | "high" | "critical";
  };
}

interface TeamChatProps {
  isOpen: boolean;
  onClose: () => void;
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  currentUserId: string;
  onlineUsers: string[];
}

export const TeamChat: React.FC<TeamChatProps> = ({
  isOpen,
  onClose,
  messages,
  onSendMessage,
  currentUserId,
  onlineUsers,
}) => {
  const [newMessage, setNewMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      onSendMessage(newMessage.trim());
      setNewMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case "system":
        return <Shield className="h-3 w-3 text-blue-500" />;
      case "alert":
        return <AlertTriangle className="h-3 w-3 text-red-500" />;
      case "bot":
        return <Bot className="h-3 w-3 text-green-500" />;
      default:
        return null;
    }
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed bottom-4 right-4 w-80 h-96 z-50 bg-background border border-border rounded-lg shadow-lg flex flex-col"
    >
      <CardHeader className="pb-3 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Team Chat</span>
            <Badge variant="outline" className="ml-2">
              <Users className="h-3 w-3 mr-1" />
              {onlineUsers.length}
            </Badge>
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription>
          Real-time team communication and alerts
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 p-0 flex flex-col">
        <ScrollArea className="flex-1 p-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`mb-4 ${
                  message.type === "system" ||
                  message.type === "alert" ||
                  message.type === "bot"
                    ? "text-center"
                    : message.userId === currentUserId
                      ? "ml-auto"
                      : "mr-auto"
                }`}
              >
                {message.type === "system" ||
                message.type === "alert" ||
                message.type === "bot" ? (
                  <div className="flex items-center justify-center space-x-2 text-xs text-muted-foreground">
                    {getMessageIcon(message.type)}
                    <span>{message.message}</span>
                    <span className="text-xs">
                      {formatTime(message.timestamp)}
                    </span>
                  </div>
                ) : (
                  <div
                    className={`max-w-[80%] ${
                      message.userId === currentUserId
                        ? "ml-auto bg-blue-600 text-white"
                        : "mr-auto bg-muted"
                    } rounded-lg p-3`}
                  >
                    {message.userId !== currentUserId && (
                      <div className="flex items-center space-x-2 mb-1">
                        <Avatar className="w-5 h-5">
                          <AvatarImage src={message.avatar} />
                          <AvatarFallback className="text-xs">
                            {message.username.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-xs font-medium">
                          {message.username}
                        </span>
                      </div>
                    )}

                    <p className="text-sm">{message.message}</p>

                    {message.metadata && (
                      <div className="flex items-center space-x-1 mt-2">
                        {message.metadata.contractAddress && (
                          <Badge variant="outline" className="text-xs">
                            {message.metadata.contractAddress.slice(0, 8)}...
                          </Badge>
                        )}
                        {message.metadata.severity && (
                          <Badge
                            variant={
                              message.metadata.severity === "critical" ||
                              message.metadata.severity === "high"
                                ? "destructive"
                                : "secondary"
                            }
                            className="text-xs"
                          >
                            {message.metadata.severity}
                          </Badge>
                        )}
                      </div>
                    )}

                    <div className="flex items-center justify-end mt-1">
                      <span className="text-xs opacity-70 flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </ScrollArea>

        {isTyping && (
          <div className="px-4 py-2 text-xs text-muted-foreground border-t">
            Someone is typing...
          </div>
        )}

        <div className="p-4 border-t">
          <div className="flex space-x-2">
            <Input
              placeholder="Type a message..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1"
            />
            <Button
              size="sm"
              onClick={handleSendMessage}
              disabled={!newMessage.trim()}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </motion.div>
  );
};

// Hook for managing team chat
export const useTeamChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [onlineUsers, setOnlineUsers] = useState([
    "user1",
    "user2",
    "ScorpiusBot",
  ]);
  const currentUserId = "current-user";

  const addMessage = (message: Omit<ChatMessage, "id" | "timestamp">) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
  };

  const sendMessage = (messageText: string) => {
    addMessage({
      userId: currentUserId,
      username: "You",
      message: messageText,
      type: "message",
    });
  };

  const addSystemMessage = (message: string) => {
    addMessage({
      userId: "system",
      username: "System",
      message,
      type: "system",
    });
  };

  const addAlertMessage = (
    message: string,
    metadata?: ChatMessage["metadata"],
  ) => {
    addMessage({
      userId: "system",
      username: "Security Alert",
      message,
      type: "alert",
      metadata,
    });
  };

  // Simulate receiving messages and system events
  useEffect(() => {
    // Initial system message
    addSystemMessage("Team chat initialized. Security monitoring active.");

    const interval = setInterval(() => {
      if (Math.random() > 0.9) {
        // 10% chance every 5 seconds
        const alertMessages = [
          {
            message:
              "High-severity vulnerability detected in contract 0x1234...5678",
            metadata: {
              contractAddress: "0x1234567890123456789012345678901234567890",
              severity: "high" as const,
            },
          },
          {
            message: "Scan completed successfully - no issues found",
            metadata: {
              contractAddress: "0x9876543210987654321098765432109876543210",
              severity: "low" as const,
            },
          },
          {
            message:
              "Suspicious transaction pattern detected in mempool monitoring",
          },
        ];

        const randomAlert =
          alertMessages[Math.floor(Math.random() * alertMessages.length)];
        addAlertMessage(randomAlert.message, randomAlert.metadata);
      }

      // Simulate team member messages
      if (Math.random() > 0.95) {
        // 5% chance
        const teamMessages = [
          {
            user: "Alice",
            message: "Looking into the latest vulnerability report",
          },
          { user: "Bob", message: "MythX scan results look good" },
          {
            user: "ScorpiusBot",
            message: "Real-time monitoring is operational",
            type: "bot" as const,
          },
        ];

        const randomTeamMessage =
          teamMessages[Math.floor(Math.random() * teamMessages.length)];
        addMessage({
          userId: randomTeamMessage.user.toLowerCase(),
          username: randomTeamMessage.user,
          message: randomTeamMessage.message,
          type: randomTeamMessage.type || "message",
          avatar: `https://ui-avatars.com/api/?name=${randomTeamMessage.user}&background=random`,
        });
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return {
    messages,
    onlineUsers,
    currentUserId,
    sendMessage,
    addSystemMessage,
    addAlertMessage,
  };
};
