"""
Enterprise Reporting Themes
===========================

Theme management system for customizable report styling and branding.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# from pydantic import BaseModel, Field  # Not currently used


@dataclass
class ColorPalette:
    """Color palette for theme styling"""
    
    primary: str = "#1f2937"
    secondary: str = "#4b5563"
    accent: str = "#3b82f6"
    success: str = "#10b981"
    warning: str = "#f59e0b"
    danger: str = "#ef4444"
    info: str = "#06b6d4"
    light: str = "#f9fafb"
    dark: str = "#111827"
    text_primary: str = "#111827"
    text_secondary: str = "#6b7280"
    text_muted: str = "#9ca3af"
    background: str = "#ffffff"
    surface: str = "#f8fafc"
    border: str = "#e5e7eb"


@dataclass
class Typography:
    """Typography configuration for themes"""
    
    font_family: str = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    heading_font: str = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    monospace_font: str = "JetBrains Mono, Monaco, Consolas, Liberation Mono, Courier New, monospace"
    base_size: str = "14px"
    scale_ratio: float = 1.2
    line_height: float = 1.6
    letter_spacing: str = "0.025em"


@dataclass
class Spacing:
    """Spacing configuration for themes"""
    
    base_unit: int = 4  # 4px base unit
    xs: str = "4px"
    sm: str = "8px"
    md: str = "16px"
    lg: str = "24px"
    xl: str = "32px"
    xxl: str = "48px"


@dataclass
class BorderRadius:
    """Border radius configuration"""
    
    none: str = "0"
    sm: str = "4px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    full: str = "9999px"


@dataclass
class Shadows:
    """Shadow configuration"""
    
    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    xl: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"


@dataclass
class ThemeConfig:
    """Complete theme configuration"""
    
    name: str
    display_name: str
    description: str = ""
    version: str = "1.0.0"
    author: str = "Scorpius Security"
    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    border_radius: BorderRadius = field(default_factory=BorderRadius)
    shadows: Shadows = field(default_factory=Shadows)
    custom_css: str = ""
    
    def to_css_vars(self) -> str:
        """Generate CSS custom properties from theme configuration"""
        vars_list = []
        
        # Colors
        vars_list.extend([
            f"--color-primary: {self.colors.primary};",
            f"--color-secondary: {self.colors.secondary};",
            f"--color-accent: {self.colors.accent};",
            f"--color-success: {self.colors.success};",
            f"--color-warning: {self.colors.warning};",
            f"--color-danger: {self.colors.danger};",
            f"--color-info: {self.colors.info};",
            f"--color-light: {self.colors.light};",
            f"--color-dark: {self.colors.dark};",
            f"--color-text-primary: {self.colors.text_primary};",
            f"--color-text-secondary: {self.colors.text_secondary};",
            f"--color-text-muted: {self.colors.text_muted};",
            f"--color-background: {self.colors.background};",
            f"--color-surface: {self.colors.surface};",
            f"--color-border: {self.colors.border};",
        ])
        
        # Typography
        vars_list.extend([
            f"--font-family: {self.typography.font_family};",
            f"--font-heading: {self.typography.heading_font};",
            f"--font-monospace: {self.typography.monospace_font};",
            f"--font-size-base: {self.typography.base_size};",
            f"--line-height: {self.typography.line_height};",
            f"--letter-spacing: {self.typography.letter_spacing};",
        ])
        
        # Spacing
        vars_list.extend([
            f"--spacing-xs: {self.spacing.xs};",
            f"--spacing-sm: {self.spacing.sm};",
            f"--spacing-md: {self.spacing.md};",
            f"--spacing-lg: {self.spacing.lg};",
            f"--spacing-xl: {self.spacing.xl};",
            f"--spacing-xxl: {self.spacing.xxl};",
        ])
        
        # Border radius
        vars_list.extend([
            f"--radius-sm: {self.border_radius.sm};",
            f"--radius-md: {self.border_radius.md};",
            f"--radius-lg: {self.border_radius.lg};",
            f"--radius-xl: {self.border_radius.xl};",
            f"--radius-full: {self.border_radius.full};",
        ])
        
        # Shadows
        vars_list.extend([
            f"--shadow-sm: {self.shadows.sm};",
            f"--shadow-md: {self.shadows.md};",
            f"--shadow-lg: {self.shadows.lg};",
            f"--shadow-xl: {self.shadows.xl};",
        ])
        
        return "\n".join([f"  {var}" for var in vars_list])
    
    def to_css(self) -> str:
        """Generate complete CSS from theme configuration"""
        css_vars = self.to_css_vars()
        
        base_css = f"""
/* {self.display_name} Theme */
:root {{
{css_vars}
}}

/* Base theme styles */
.theme-{self.name} {{
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  line-height: var(--line-height);
  letter-spacing: var(--letter-spacing);
  color: var(--color-text-primary);
  background-color: var(--color-background);
}}

.theme-{self.name} h1,
.theme-{self.name} h2,
.theme-{self.name} h3,
.theme-{self.name} h4,
.theme-{self.name} h5,
.theme-{self.name} h6 {{
  font-family: var(--font-heading);
  font-weight: 600;
  line-height: 1.3;
}}

.theme-{self.name} .text-primary {{ color: var(--color-text-primary); }}
.theme-{self.name} .text-secondary {{ color: var(--color-text-secondary); }}
.theme-{self.name} .text-muted {{ color: var(--color-text-muted); }}

.theme-{self.name} .bg-primary {{ background-color: var(--color-primary); }}
.theme-{self.name} .bg-secondary {{ background-color: var(--color-secondary); }}
.theme-{self.name} .bg-surface {{ background-color: var(--color-surface); }}

.theme-{self.name} .border {{ border-color: var(--color-border); }}

.theme-{self.name} .shadow-sm {{ box-shadow: var(--shadow-sm); }}
.theme-{self.name} .shadow-md {{ box-shadow: var(--shadow-md); }}
.theme-{self.name} .shadow-lg {{ box-shadow: var(--shadow-lg); }}

.theme-{self.name} .rounded {{ border-radius: var(--radius-md); }}
.theme-{self.name} .rounded-lg {{ border-radius: var(--radius-lg); }}
"""
        
        if self.custom_css:
            base_css += f"\n/* Custom CSS */\n{self.custom_css}"
        
        return base_css


class ThemeManager:
    """Theme management system"""
    
    def __init__(self, themes_dir: Optional[Path] = None):
        self.themes_dir = themes_dir or Path("themes")
        self._themes: Dict[str, ThemeConfig] = {}
        self._load_builtin_themes()
        if self.themes_dir.exists():
            self._load_custom_themes()
    
    def _load_builtin_themes(self):
        """Load built-in themes"""
        
        # Dark Professional Theme
        dark_pro = ThemeConfig(
            name="dark_pro",
            display_name="Dark Professional",
            description="Professional dark theme for security reports",
            colors=ColorPalette(
                primary="#0f172a",
                secondary="#1e293b",
                accent="#3b82f6",
                success="#22c55e",
                warning="#eab308",
                danger="#ef4444",
                info="#06b6d4",
                light="#f8fafc",
                dark="#020617",
                text_primary="#f8fafc",
                text_secondary="#cbd5e1",
                text_muted="#64748b",
                background="#0f172a",
                surface="#1e293b",
                border="#334155"
            ),
            typography=Typography(
                font_family="Inter, system-ui, sans-serif",
                heading_font="Inter, system-ui, sans-serif",
                base_size="14px"
            )
        )
        
        # Light Corporate Theme
        light_corporate = ThemeConfig(
            name="light_corporate",
            display_name="Light Corporate",
            description="Clean corporate theme with professional styling",
            colors=ColorPalette(
                primary="#1f2937",
                secondary="#374151",
                accent="#2563eb",
                success="#059669",
                warning="#d97706",
                danger="#dc2626",
                info="#0284c7",
                light="#f9fafb",
                dark="#111827",
                text_primary="#111827",
                text_secondary="#4b5563",
                text_muted="#6b7280",
                background="#ffffff",
                surface="#f8fafc",
                border="#e5e7eb"
            )
        )
        
        self._themes["dark_pro"] = dark_pro
        self._themes["light_corporate"] = light_corporate
    
    def _load_custom_themes(self):
        """Load custom themes from themes directory"""
        for theme_file in self.themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                
                theme = self._parse_theme_data(theme_data)
                if theme:
                    self._themes[theme.name] = theme
            except Exception as e:
                print(f"Error loading theme {theme_file}: {e}")
    
    def _parse_theme_data(self, data: Dict) -> Optional[ThemeConfig]:
        """Parse theme data from JSON"""
        try:
            # Basic theme info
            theme = ThemeConfig(
                name=data.get("name", ""),
                display_name=data.get("display_name", ""),
                description=data.get("description", ""),
                version=data.get("version", "1.0.0"),
                author=data.get("author", ""),
                custom_css=data.get("custom_css", "")
            )
            
            # Colors
            if "colors" in data:
                colors_data = data["colors"]
                theme.colors = ColorPalette(**colors_data)
            
            # Typography
            if "typography" in data:
                typography_data = data["typography"]
                theme.typography = Typography(**typography_data)
            
            # Spacing
            if "spacing" in data:
                spacing_data = data["spacing"]
                theme.spacing = Spacing(**spacing_data)
            
            # Border radius
            if "border_radius" in data:
                radius_data = data["border_radius"]
                theme.border_radius = BorderRadius(**radius_data)
            
            # Shadows
            if "shadows" in data:
                shadows_data = data["shadows"]
                theme.shadows = Shadows(**shadows_data)
            
            return theme
        except Exception as e:
            print(f"Error parsing theme data: {e}")
            return None
    
    def get_theme(self, name: str) -> Optional[ThemeConfig]:
        """Get theme by name"""
        return self._themes.get(name)
    
    def list_themes(self) -> List[str]:
        """List all available theme names"""
        return list(self._themes.keys())
    
    def get_all_themes(self) -> Dict[str, ThemeConfig]:
        """Get all available themes"""
        return self._themes.copy()
    
    def add_theme(self, theme: ThemeConfig):
        """Add a new theme"""
        self._themes[theme.name] = theme
    
    def remove_theme(self, name: str) -> bool:
        """Remove a theme"""
        if name in self._themes:
            del self._themes[name]
            return True
        return False
    
    def save_theme(self, theme: ThemeConfig, file_path: Optional[Path] = None):
        """Save theme to file"""
        if not file_path:
            file_path = self.themes_dir / f"{theme.name}.json"
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        theme_data = {
            "name": theme.name,
            "display_name": theme.display_name,
            "description": theme.description,
            "version": theme.version,
            "author": theme.author,
            "colors": {
                "primary": theme.colors.primary,
                "secondary": theme.colors.secondary,
                "accent": theme.colors.accent,
                "success": theme.colors.success,
                "warning": theme.colors.warning,
                "danger": theme.colors.danger,
                "info": theme.colors.info,
                "light": theme.colors.light,
                "dark": theme.colors.dark,
                "text_primary": theme.colors.text_primary,
                "text_secondary": theme.colors.text_secondary,
                "text_muted": theme.colors.text_muted,
                "background": theme.colors.background,
                "surface": theme.colors.surface,
                "border": theme.colors.border,
            },
            "typography": {
                "font_family": theme.typography.font_family,
                "heading_font": theme.typography.heading_font,
                "monospace_font": theme.typography.monospace_font,
                "base_size": theme.typography.base_size,
                "scale_ratio": theme.typography.scale_ratio,
                "line_height": theme.typography.line_height,
                "letter_spacing": theme.typography.letter_spacing,
            },
            "spacing": {
                "base_unit": theme.spacing.base_unit,
                "xs": theme.spacing.xs,
                "sm": theme.spacing.sm,
                "md": theme.spacing.md,
                "lg": theme.spacing.lg,
                "xl": theme.spacing.xl,
                "xxl": theme.spacing.xxl,
            },
            "border_radius": {
                "none": theme.border_radius.none,
                "sm": theme.border_radius.sm,
                "md": theme.border_radius.md,
                "lg": theme.border_radius.lg,
                "xl": theme.border_radius.xl,
                "full": theme.border_radius.full,
            },
            "shadows": {
                "sm": theme.shadows.sm,
                "md": theme.shadows.md,
                "lg": theme.shadows.lg,
                "xl": theme.shadows.xl,
            },
            "custom_css": theme.custom_css,
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=2)
    
    def generate_css_for_theme(self, name: str) -> Optional[str]:
        """Generate CSS for a specific theme"""
        theme = self.get_theme(name)
        return theme.to_css() if theme else None
    
    def generate_all_css(self) -> str:
        """Generate CSS for all themes"""
        css_parts = []
        for theme in self._themes.values():
            css_parts.append(theme.to_css())
        return "\n\n".join(css_parts)


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance"""
    return theme_manager
