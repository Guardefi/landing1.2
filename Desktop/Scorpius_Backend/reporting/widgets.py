"""
Enterprise Reporting Widget System
==================================

Extensible widget system for report components including heatmaps, call graphs,
opcode histograms, timelines, and custom visualizations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# Visualization libraries
try:
    import plotly.express as px
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


@dataclass
class WidgetConfig:
    """Widget configuration"""

    widget_type: str
    title: str
    description: str
    data_requirements: list[str]
    config_schema: dict[str, Any]
    default_config: dict[str, Any]


class BaseWidget(ABC):
    """
    Base class for all report widgets.

    All widgets must implement the render method and provide configuration.
    """

    def __init__(self, widget_id: str, config: dict[str, Any]):
        """
        Initialize widget.

        Args:
            widget_id: Unique widget identifier
            config: Widget configuration
        """
        self.widget_id = widget_id
        self.config = config

    @abstractmethod
    def render(self, data: dict[str, Any], **kwargs) -> str:
        """
        Render widget to HTML.

        Args:
            data: Widget data
            **kwargs: Additional rendering options

        Returns:
            HTML representation of widget
        """
        pass

    @abstractmethod
    def get_config_schema(self) -> dict[str, Any]:
        """
        Get widget configuration schema.

        Returns:
            JSON schema for widget configuration
        """
        pass

    def validate_data(self, data: dict[str, Any]) -> bool:
        """
        Validate widget data.

        Args:
            data: Data to validate

        Returns:
            True if data is valid
        """
        return True

    def get_dependencies(self) -> list[str]:
        """
        Get required dependencies for this widget.

        Returns:
            List of dependency names
        """
        return []


class HeatmapWidget(BaseWidget):
    """
    Risk heatmap widget showing vulnerability distribution.
    """

    def render(self, data: dict[str, Any], **kwargs) -> str:
        """Render risk heatmap"""
        if not PLOTLY_AVAILABLE:
            return self._render_fallback(data)

        # Extract heatmap data
        vulnerabilities = data.get("vulnerabilities", [])

        # Create severity vs function matrix
        functions = list({v.get("function_name", "unknown") for v in vulnerabilities})
        severities = ["critical", "high", "medium", "low"]

        # Build matrix
        matrix = []
        labels = []

        for severity in severities:
            row = []
            row_labels = []
            for function in functions:
                count = len(
                    [
                        v
                        for v in vulnerabilities
                        if v.get("severity", "").lower() == severity
                        and v.get("function_name") == function
                    ]
                )
                row.append(count)
                row_labels.append(f"{function}<br>{severity}: {count}")
            matrix.append(row)
            labels.append(row_labels)

        # Create heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=matrix,
                x=functions,
                y=severities,
                text=labels,
                texttemplate="%{text}",
                colorscale="Reds",
                showscale=True,
            )
        )

        fig.update_layout(
            title=self.config.get("title", "Vulnerability Risk Heatmap"),
            xaxis_title="Functions",
            yaxis_title="Severity",
            height=400,
            font={"size": 12},
        )

        # Convert to HTML
        plot_html = fig.to_html(
            include_plotlyjs="cdn", div_id=f"heatmap_{self.widget_id}"
        )

        return f"""
        <div class="widget heatmap-widget" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Risk Heatmap')}</h3>
                <p class="widget-description">{self.config.get('description', '')}</p>
            </div>
            <div class="widget-content">
                {plot_html}
            </div>
        </div>
        """

    def _render_fallback(self, data: dict[str, Any]) -> str:
        """Fallback rendering without Plotly"""
        vulnerabilities = data.get("vulnerabilities", [])
        severity_counts = {}

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "unknown").lower()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        rows = []
        for severity, count in severity_counts.items():
            rows.append(
                f"<tr><td class='severity-{severity}'>{severity.title()}</td><td>{count}</td></tr>"
            )

        return f"""
        <div class="widget heatmap-widget fallback" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Vulnerability Summary')}</h3>
            </div>
            <div class="widget-content">
                <table class="vulnerability-summary">
                    <thead>
                        <tr><th>Severity</th><th>Count</th></tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def get_config_schema(self) -> dict[str, Any]:
        """Get configuration schema for heatmap widget"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "default": "Risk Heatmap"},
                "description": {"type": "string", "default": ""},
                "colorscale": {"type": "string", "default": "Reds"},
                "height": {"type": "integer", "default": 400},
            },
        }


class CallGraphWidget(BaseWidget):
    """
    Function call graph visualization widget.
    """

    def render(self, data: dict[str, Any], **kwargs) -> str:
        """Render call graph"""
        if not PLOTLY_AVAILABLE or not NETWORKX_AVAILABLE:
            return self._render_fallback(data)

        # Extract call graph data
        call_graph = data.get("call_graph", {})
        vulnerabilities = data.get("vulnerabilities", [])

        # Create network graph
        G = nx.DiGraph()

        # Add nodes and edges
        for caller, callees in call_graph.items():
            G.add_node(caller)
            for callee in callees:
                G.add_edge(caller, callee)

        # Calculate layout
        pos = nx.spring_layout(G, k=3, iterations=50)

        # Create node colors based on vulnerability counts
        node_colors = []
        for node in G.nodes():
            vuln_count = len([v for v in vulnerabilities if v.get("function_name") == node])
            if vuln_count >= 3:
                node_colors.append("red")
            elif vuln_count >= 1:
                node_colors.append("orange")
            else:
                node_colors.append("lightblue")

        # Extract coordinates
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        edge_x = []
        edge_y = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Create Plotly traces
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=list(G.nodes()),
            textposition="top center",
            marker=dict(
                showscale=True,
                colorscale='YlOrRd',
                reversescale=True,
                color=node_colors,
                size=15,
                line_width=2
            )
        )

        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=self.config.get("title", "Function Call Graph"),
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[
                    dict(
                        text="Red nodes have multiple vulnerabilities",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor="left", yanchor="bottom",
                        font=dict(color="gray", size=12)
                    )
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=500
            )
        )

        plot_html = fig.to_html(
            include_plotlyjs="cdn", div_id=f"callgraph_{self.widget_id}"
        )

        return f"""
        <div class="widget callgraph-widget" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Function Call Graph')}</h3>
                <p class="widget-description">{self.config.get('description', '')}</p>
            </div>
            <div class="widget-content">
                {plot_html}
            </div>
        </div>
        """

    def _render_fallback(self, data: dict[str, Any]) -> str:
        """Fallback rendering without graph libraries"""
        call_graph = data.get("call_graph", {})
        
        rows = []
        for caller, callees in call_graph.items():
            callees_str = ", ".join(callees) if callees else "None"
            rows.append(f"<tr><td>{caller}</td><td>{callees_str}</td></tr>")

        return f"""
        <div class="widget callgraph-widget fallback" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Function Call Graph')}</h3>
            </div>
            <div class="widget-content">
                <table class="call-graph-table">
                    <thead>
                        <tr><th>Function</th><th>Calls</th></tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def get_config_schema(self) -> dict[str, Any]:
        """Get configuration schema for call graph widget"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "default": "Function Call Graph"},
                "description": {"type": "string", "default": ""},
                "layout_algorithm": {"type": "string", "default": "spring"},
                "height": {"type": "integer", "default": 500},
            },
        }


class MetricsWidget(BaseWidget):
    """
    Key metrics and statistics widget.
    """

    def render(self, data: dict[str, Any], **kwargs) -> str:
        """Render metrics dashboard"""
        vulnerabilities = data.get("vulnerabilities", [])

        # Calculate key metrics
        total_vulns = len(vulnerabilities)
        critical_vulns = len([v for v in vulnerabilities if v.get("severity", "").lower() == "critical"])
        high_vulns = len([v for v in vulnerabilities if v.get("severity", "").lower() == "high"])
        
        unique_functions = len(set(v.get("function_name", "") for v in vulnerabilities))
        avg_risk_score = sum(v.get("risk_score", 0) for v in vulnerabilities) / max(total_vulns, 1)

        return f"""
        <div class="widget metrics-widget" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Key Metrics')}</h3>
            </div>
            <div class="widget-content">
                <div class="metrics-grid">
                    <div class="metric-card critical">
                        <div class="metric-value">{critical_vulns}</div>
                        <div class="metric-label">Critical Vulns</div>
                    </div>
                    <div class="metric-card high">
                        <div class="metric-value">{high_vulns}</div>
                        <div class="metric-label">High Vulns</div>
                    </div>
                    <div class="metric-card total">
                        <div class="metric-value">{total_vulns}</div>
                        <div class="metric-label">Total Vulns</div>
                    </div>
                    <div class="metric-card functions">
                        <div class="metric-value">{unique_functions}</div>
                        <div class="metric-label">Affected Functions</div>
                    </div>
                    <div class="metric-card risk">
                        <div class="metric-value">{avg_risk_score:.1f}</div>
                        <div class="metric-label">Avg Risk Score</div>
                    </div>
                </div>
            </div>
        </div>
        """

    def get_config_schema(self) -> dict[str, Any]:
        """Get configuration schema for metrics widget"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "default": "Key Metrics"},
                "show_percentages": {"type": "boolean", "default": False},
            },
        }


class TimelineWidget(BaseWidget):
    """
    Vulnerability timeline widget showing discovery timeline.
    """

    def render(self, data: dict[str, Any], **kwargs) -> str:
        """Render vulnerability timeline"""
        if not PLOTLY_AVAILABLE:
            return self._render_fallback(data)

        vulnerabilities = data.get("vulnerabilities", [])
        
        # Group by date
        timeline_data = {}
        for vuln in vulnerabilities:
            date = vuln.get("discovered_date", "Unknown")
            if date not in timeline_data:
                timeline_data[date] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            
            severity = vuln.get("severity", "low").lower()
            if severity in timeline_data[date]:
                timeline_data[date][severity] += 1

        dates = sorted(timeline_data.keys())
        
        # Create traces for each severity
        fig = go.Figure()
        
        for severity in ["critical", "high", "medium", "low"]:
            counts = [timeline_data[date][severity] for date in dates]
            fig.add_trace(go.Scatter(
                x=dates,
                y=counts,
                mode='lines+markers',
                name=severity.title(),
                line=dict(width=3),
                marker=dict(size=8)
            ))

        fig.update_layout(
            title=self.config.get("title", "Vulnerability Discovery Timeline"),
            xaxis_title="Date",
            yaxis_title="Vulnerability Count",
            height=400,
            hovermode='x unified'
        )

        plot_html = fig.to_html(
            include_plotlyjs="cdn", div_id=f"timeline_{self.widget_id}"
        )

        return f"""
        <div class="widget timeline-widget" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Vulnerability Timeline')}</h3>
                <p class="widget-description">{self.config.get('description', '')}</p>
            </div>
            <div class="widget-content">
                {plot_html}
            </div>
        </div>
        """

    def _render_fallback(self, data: dict[str, Any]) -> str:
        """Fallback timeline rendering"""
        vulnerabilities = data.get("vulnerabilities", [])
        
        # Simple date-based list
        timeline_items = []
        for vuln in vulnerabilities:
            date = vuln.get("discovered_date", "Unknown")
            severity = vuln.get("severity", "Unknown")
            title = vuln.get("title", "Vulnerability")
            timeline_items.append(f"""
                <div class="timeline-item severity-{severity.lower()}">
                    <span class="timeline-date">{date}</span>
                    <span class="timeline-title">{title}</span>
                    <span class="timeline-severity">{severity}</span>
                </div>
            """)

        return f"""
        <div class="widget timeline-widget fallback" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Vulnerability Timeline')}</h3>
            </div>
            <div class="widget-content">
                <div class="timeline-container">
                    {''.join(timeline_items)}
                </div>
            </div>
        </div>
        """

    def get_config_schema(self) -> dict[str, Any]:
        """Get configuration schema for timeline widget"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "default": "Vulnerability Timeline"},
                "description": {"type": "string", "default": ""},
                "height": {"type": "integer", "default": 400},
                "date_format": {"type": "string", "default": "%Y-%m-%d"},
            },
        }


class CustomChartWidget(BaseWidget):
    """
    Custom chart widget for flexible data visualization.
    """

    def render(self, data: dict[str, Any], **kwargs) -> str:
        """Render custom chart"""
        chart_type = self.config.get("chart_type", "bar")
        chart_data = data.get("chart_data", {})

        if not PLOTLY_AVAILABLE:
            return self._render_fallback(data)

        if chart_type == "bar":
            fig = px.bar(
                x=chart_data.get("labels", []),
                y=chart_data.get("values", []),
                title=self.config.get("title", "Custom Chart")
            )
        elif chart_type == "pie":
            fig = px.pie(
                values=chart_data.get("values", []),
                names=chart_data.get("labels", []),
                title=self.config.get("title", "Custom Chart")
            )
        elif chart_type == "line":
            fig = px.line(
                x=chart_data.get("x", []),
                y=chart_data.get("y", []),
                title=self.config.get("title", "Custom Chart")
            )
        else:
            # Default to bar chart
            fig = px.bar(
                x=chart_data.get("labels", []),
                y=chart_data.get("values", []),
                title=self.config.get("title", "Custom Chart")
            )

        fig.update_layout(height=self.config.get("height", 400))

        plot_html = fig.to_html(
            include_plotlyjs="cdn", div_id=f"custom_{self.widget_id}"
        )

        return f"""
        <div class="widget custom-chart-widget" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Custom Chart')}</h3>
                <p class="widget-description">{self.config.get('description', '')}</p>
            </div>
            <div class="widget-content">
                {plot_html}
            </div>
        </div>
        """

    def _render_fallback(self, data: dict[str, Any]) -> str:
        """Fallback rendering for custom charts"""
        chart_data = data.get("chart_data", {})
        labels = chart_data.get("labels", [])
        values = chart_data.get("values", [])

        rows = []
        for label, value in zip(labels, values):
            rows.append(f"<tr><td>{label}</td><td>{value}</td></tr>")

        return f"""
        <div class="widget custom-chart-widget fallback" id="{self.widget_id}">
            <div class="widget-header">
                <h3>{self.config.get('title', 'Custom Chart')}</h3>
            </div>
            <div class="widget-content">
                <table class="chart-data-table">
                    <thead>
                        <tr><th>Label</th><th>Value</th></tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def get_config_schema(self) -> dict[str, Any]:
        """Get configuration schema for custom chart widget"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "default": "Custom Chart"},
                "description": {"type": "string", "default": ""},
                "chart_type": {
                    "type": "string",
                    "enum": ["bar", "pie", "line", "scatter"],
                    "default": "bar"
                },
                "height": {"type": "integer", "default": 400},
            },
        }


class WidgetRegistry:
    """
    Registry for managing and creating widgets.
    """

    def __init__(self):
        """Initialize widget registry with built-in widgets"""
        self._widgets = {}
        self._register_builtin_widgets()

    def _register_builtin_widgets(self) -> None:
        """Register built-in widget types"""
        self.register_widget("heatmap", HeatmapWidget)
        self.register_widget("call_graph", CallGraphWidget)
        self.register_widget("metrics", MetricsWidget)
        self.register_widget("timeline", TimelineWidget)
        self.register_widget("custom_chart", CustomChartWidget)

    def register_widget(self, widget_type: str, widget_class: type[BaseWidget]) -> None:
        """
        Register a widget type.

        Args:
            widget_type: Widget type identifier
            widget_class: Widget class
        """
        self._widgets[widget_type] = widget_class

    def create_widget(self, widget_type: str, widget_id: str, config: dict[str, Any]) -> BaseWidget:
        """
        Create a widget instance.

        Args:
            widget_type: Widget type
            widget_id: Unique widget ID
            config: Widget configuration

        Returns:
            Widget instance

        Raises:
            ValueError: If widget type not found
        """
        if widget_type not in self._widgets:
            raise ValueError(f"Unknown widget type: {widget_type}")

        widget_class = self._widgets[widget_type]
        return widget_class(widget_id, config)

    def list_widget_types(self) -> list[dict[str, Any]]:
        """
        List all available widget types.

        Returns:
            List of widget type information
        """
        widget_types = []
        for widget_type, widget_class in self._widgets.items():
            # Create temporary instance to get schema
            temp_widget = widget_class("temp", {})
            schema = temp_widget.get_config_schema()
            
            widget_types.append({
                "type": widget_type,
                "name": widget_class.__name__,
                "description": widget_class.__doc__ or "",
                "config_schema": schema,
            })

        return widget_types

    def render_widget(self, widget_type: str, data: dict[str, Any], **kwargs) -> str:
        """
        Render a widget with the given data.

        Args:
            widget_type: Widget type
            data: Data to render
            **kwargs: Additional options

        Returns:
            Rendered HTML

        Raises:
            ValueError: If widget type not found
        """
        if widget_type not in self._widgets:
            raise ValueError(f"Unknown widget type: {widget_type}")

        config = kwargs.get("config", {})
        widget_id = kwargs.get("widget_id", f"widget_{widget_type}")
        
        widget = self.create_widget(widget_type, widget_id, config)
        return widget.render(data, **kwargs)

    def get_widget_dependencies(self) -> dict[str, list[str]]:
        """
        Get dependencies for all registered widgets.

        Returns:
            Dictionary mapping widget types to their dependencies
        """
        dependencies = {}
        for widget_type, widget_class in self._widgets.items():
            temp_widget = widget_class("temp", {})
            dependencies[widget_type] = temp_widget.get_dependencies()

        return dependencies
