import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
  ComposedChart,
} from "recharts";
import { cn } from "@/lib/utils";

// Enhanced Area Chart with Gradient
export const EnhancedAreaChart = ({
  data,
  dataKey,
  color = "#3b82f6",
  className,
  showGrid = true,
  showTooltip = true,
  animate = true,
}: {
  data: any[];
  dataKey: string;
  color?: string;
  className?: string;
  showGrid?: boolean;
  showTooltip?: boolean;
  animate?: boolean;
}) => {
  const gradientId = `gradient-${dataKey}`;

  return (
    <motion.div
      initial={animate ? { opacity: 0, y: 20 } : {}}
      animate={animate ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6 }}
      className={cn("w-full h-full", className)}
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
        >
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.8} />
              <stop offset="95%" stopColor={color} stopOpacity={0.1} />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          {showGrid && (
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth={0.5}
            />
          )}
          <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          {showTooltip && (
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(0, 0, 0, 0.9)",
                border: `1px solid ${color}`,
                borderRadius: "8px",
                fontSize: "12px",
                boxShadow: `0 0 20px ${color}40`,
              }}
              labelStyle={{ color: "#fff" }}
            />
          )}
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={3}
            fill={`url(#${gradientId})`}
            filter="url(#glow)"
            animationDuration={2000}
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

// Enhanced Line Chart with Multiple Lines
export const EnhancedLineChart = ({
  data,
  lines,
  className,
  showGrid = true,
  showBrush = false,
}: {
  data: any[];
  lines: { dataKey: string; color: string; name?: string }[];
  className?: string;
  showGrid?: boolean;
  showBrush?: boolean;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className={cn("w-full h-full", className)}
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
        >
          <defs>
            {lines.map((line) => (
              <filter key={`glow-${line.dataKey}`} id={`glow-${line.dataKey}`}>
                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            ))}
          </defs>
          {showGrid && (
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.1)"
            />
          )}
          <XAxis
            dataKey="time"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(0, 0, 0, 0.9)",
              border: "1px solid rgba(255,255,255,0.2)",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
          <Legend />
          {lines.map((line, index) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              stroke={line.color}
              strokeWidth={2}
              name={line.name || line.dataKey}
              dot={{ fill: line.color, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, fill: line.color, strokeWidth: 0 }}
              filter={`url(#glow-${line.dataKey})`}
              animationDuration={2000}
              animationDelay={index * 200}
            />
          ))}
          {showBrush && <Brush dataKey="time" height={30} stroke="#8884d8" />}
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

// Enhanced Radial Progress Chart
export const EnhancedRadialChart = ({
  data,
  className,
  innerRadius = 60,
  outerRadius = 100,
}: {
  data: { name: string; value: number; color: string }[];
  className?: string;
  innerRadius?: number;
  outerRadius?: number;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, rotate: -90 }}
      animate={{ opacity: 1, rotate: 0 }}
      transition={{ duration: 0.8 }}
      className={cn("w-full h-full", className)}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius={innerRadius}
          outerRadius={outerRadius}
          data={data}
          startAngle={90}
          endAngle={-270}
        >
          <defs>
            {data.map((entry, index) => (
              <linearGradient
                key={index}
                id={`gradient-${index}`}
                x1="0"
                y1="0"
                x2="1"
                y2="1"
              >
                <stop offset="0%" stopColor={entry.color} stopOpacity={1} />
                <stop offset="100%" stopColor={entry.color} stopOpacity={0.6} />
              </linearGradient>
            ))}
          </defs>
          <RadialBar
            dataKey="value"
            cornerRadius={5}
            fill={(entry, index) => `url(#gradient-${index})`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(0, 0, 0, 0.9)",
              border: "1px solid rgba(255,255,255,0.2)",
              borderRadius: "8px",
            }}
          />
        </RadialBarChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

// Enhanced Composed Chart (Bar + Line)
export const EnhancedComposedChart = ({
  data,
  bars,
  lines,
  className,
}: {
  data: any[];
  bars: { dataKey: string; color: string; name?: string }[];
  lines: { dataKey: string; color: string; name?: string }[];
  className?: string;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={cn("w-full h-full", className)}
    >
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
        >
          <defs>
            {[...bars, ...lines].map((item, index) => (
              <linearGradient
                key={index}
                id={`composedGradient-${index}`}
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop offset="5%" stopColor={item.color} stopOpacity={0.8} />
                <stop offset="95%" stopColor={item.color} stopOpacity={0.3} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(0, 0, 0, 0.9)",
              border: "1px solid rgba(255,255,255,0.2)",
              borderRadius: "8px",
            }}
          />
          <Legend />
          {bars.map((bar, index) => (
            <Bar
              key={bar.dataKey}
              dataKey={bar.dataKey}
              fill={`url(#composedGradient-${index})`}
              name={bar.name || bar.dataKey}
              radius={[4, 4, 0, 0]}
            />
          ))}
          {lines.map((line, index) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              stroke={line.color}
              strokeWidth={3}
              name={line.name || line.dataKey}
              dot={{ fill: line.color, strokeWidth: 2, r: 4 }}
            />
          ))}
        </ComposedChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

// Enhanced Donut Chart
export const EnhancedDonutChart = ({
  data,
  className,
  innerRadius = 50,
  outerRadius = 100,
}: {
  data: { name: string; value: number; color: string }[];
  className?: string;
  innerRadius?: number;
  outerRadius?: number;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className={cn("w-full h-full relative", className)}
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <defs>
            {data.map((entry, index) => (
              <linearGradient
                key={index}
                id={`donutGradient-${index}`}
                x1="0"
                y1="0"
                x2="1"
                y2="1"
              >
                <stop offset="0%" stopColor={entry.color} stopOpacity={1} />
                <stop offset="100%" stopColor={entry.color} stopOpacity={0.6} />
              </linearGradient>
            ))}
          </defs>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={innerRadius}
            outerRadius={outerRadius}
            paddingAngle={2}
            dataKey="value"
            animationDuration={1500}
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={`url(#donutGradient-${index})`}
                stroke={entry.color}
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(0, 0, 0, 0.9)",
              border: "1px solid rgba(255,255,255,0.2)",
              borderRadius: "8px",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

// Real-time Chart with Live Data
export const RealTimeChart = ({
  data,
  dataKey,
  color = "#00ff88",
  className,
  maxDataPoints = 50,
}: {
  data: any[];
  dataKey: string;
  color?: string;
  className?: string;
  maxDataPoints?: number;
}) => {
  const displayData = data.slice(-maxDataPoints);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={cn("w-full h-full", className)}
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={displayData}>
          <defs>
            <linearGradient id="realTimeGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.8} />
              <stop offset="95%" stopColor={color} stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke="transparent"
            fill="url(#realTimeGradient)"
          />
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  );
};
