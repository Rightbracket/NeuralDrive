# 07a: Web Design System

This document serves as the comprehensive visual design specification for the NeuralDrive web interface. It acts as a companion to 07-web-interface.md, defining the aesthetic framework that unifies Open WebUI, GPU Hot, and the custom system panel into a single, cohesive experience.

## Section 1: Design Principles

- **Terminal Aesthetic**: The interface honors its Linux roots with high contrast, sharp edges, and monospaced data points while maintaining modern usability.
- **Information Density**: Users need to see system health, GPU metrics, and model status at a glance without excessive scrolling.
- **Accessibility First**: High color contrast ratios and clear focus states ensure the "hacker" look doesn't compromise readability.
- **Consistent with TUI**: The web interface feels like a visual evolution of the local terminal interface, using the same color language and structural logic.

## Section 2: Color Palette

NeuralDrive uses a strict dark-mode palette optimized for OLED and high-end displays.

| Token | Hex | Purpose |
| :--- | :--- | :--- |
| `--nd-bg-page` | #0A0A0A | Main background (pitch black) |
| `--nd-bg-card` | #141414 | Card and elevated surface background |
| `--nd-bg-surface` | #1F1F1F | Hover states and active menu items |
| `--nd-border-subtle` | #2E2E2E | Default component borders |
| `--nd-accent-primary` | #F59E0B | Amber: Primary actions, highlights, active states |
| `--nd-accent-secondary`| #10B981 | Green: Success, healthy status, running services |
| `--nd-error` | #EF4444 | Red: Critical errors, stopped services |
| `--nd-warning` | #F97316 | Orange: Resource warnings, pending states |
| `--nd-text-primary` | #FFFFFF | Primary body text and headers |
| `--nd-text-secondary` | #A1A1AA | Secondary descriptions and labels |
| `--nd-text-muted` | #52525B | Tertiary info, disabled states, and timestamps |

## Section 3: Typography

- **Body Stack**: Inter, system-ui, -apple-system, sans-serif. Used for all UI labels and general prose.
- **Data Stack**: JetBrains Mono, ui-monospace, SFMono-Regular, monospace. Used for metrics, logs, model IDs, and system paths.

| Size | Value | Weight | Usage |
| :--- | :--- | :--- | :--- |
| **xs** | 12px | 400/500 | Captions, small labels |
| **sm** | 14px | 400/500 | Body text, input labels |
| **md** | 16px | 500/600 | Buttons, navigation links |
| **lg** | 20px | 600 | Card titles, section headers |
| **xl** | 24px | 700 | Page titles |
| **2xl** | 32px | 800 | Hero metrics |

## Section 4: Spacing & Layout

- **Base Unit**: 4px grid system.
- **Spacing Scale**: 4, 8, 12, 16, 24, 32, 48, 64.
- **Border Radius**:
  - `2px`: Buttons and small inputs (sharp look).
  - `4px`: Cards and modals.
- **Shadows**:
  - `Subtle`: 0 1px 3px rgba(0,0,0,0.5) for cards.
  - `Medium`: 0 4px 12px rgba(0,0,0,0.8) for dropdowns.
  - `Heavy`: 0 12px 32px rgba(0,0,0,0.9) for modals.

## Section 5: Component Library

- **Buttons**:
  - `Primary`: Amber background (#F59E0B), black text.
  - `Secondary`: Ghost style with #2E2E2E border, white text.
  - `Danger`: Red background (#EF4444), white text.
- **Cards**: Dark background (#141414), subtle border (#2E2E2E). Optional top header bar with a 1px amber or green accent line.
- **Inputs**: Dark background (#0A0A0A), #2E2E2E border. On focus, border transitions to Amber. Error states use a Red border.
- **Tables**: Row shading alternates between #0A0A0A and #141414. Headers are sticky with #1F1F1F background.
- **Badges/Pills**:
  - `Running`: Green text/border, subtle green glow.
  - `Stopped`: Gray text/border.
  - `Error`: Red text/border.
  - `Loading`: Amber text/border with a subtle pulse animation.
- **Modals**: Semi-transparent dark overlay (#000000cc). Centered card with explicit close button in top right and action footer.
- **Toasts**: Slide-in from top-right. 4px color-coded left border (Green/Red/Amber). Auto-dismiss after 5 seconds.
- **Progress Bars**: Amber fill on a #1F1F1F track. Indeterminate state uses a traveling amber pulse.
- **Sidebar**: Darkest background (#0A0A0A). Active items show an Amber left border (3px width). Icons are paired with labels in collapsible groups.

## Section 6: Iconography

Using the Lucide Icon set for consistency and clarity.

- **Dashboard**: LayoutDashboard
- **Models**: Brain
- **GPU Metrics**: Cpu
- **Services**: Server
- **Storage**: HardDrive
- **Network**: Globe
- **Logs**: ScrollText
- **Settings**: Settings
- **Chat**: MessageSquare

## Section 7: Open WebUI Theming — Constraints & Options

Open WebUI's community license **does not** provide CSS injection, custom sidebar links, or white-labeling. The Open WebUI name and logo must remain visible (per their license terms). NeuralDrive customizes within these boundaries.

### What We Can Do (Community Version)

| Mechanism | Effect |
| :--- | :--- |
| `WEBUI_NAME="NeuralDrive"` | Changes the application title throughout the UI |
| `STATIC_DIR=/etc/neuraldrive/webui-static/` | Mount custom favicon and PWA icons |
| `ENABLE_EASTER_EGGS=False` | Hides novelty themes for a cleaner look |
| `WEBUI_BANNERS` env var | Display system-level announcements (info/success/warning/error) |
| Built-in dark mode | Enable via user settings; Open WebUI ships with a solid dark theme |
| Rich UI embeds | Tools and Actions can render custom HTML iframes inside chat |
| Feature toggles | Disable unused features (voice, image gen, community sharing) |

### What Requires Enterprise License or Fork

| Capability | Constraint |
| :--- | :--- |
| Custom CSS injection | Not available in community version |
| Logo replacement in sidebar | Enterprise license required |
| Custom color palette / accent colors | Enterprise license required |
| Custom sidebar navigation links | No mechanism; requires frontend fork |
| Removal of Open WebUI branding | Enterprise license (or ≤50 users exemption) |

### Recommended Approach

1. **Minimal branding**: Use `WEBUI_NAME`, custom favicon, and banners. Accept Open WebUI's native dark theme as-is. It is already dark and clean — close enough to our design system.
2. **System Panel carries the brand**: The NeuralDrive System Panel (our custom app) is where the full design system applies — amber/green palette, custom sidebar, terminal aesthetic.
3. **Evaluate Enterprise license** during development if deeper Open WebUI branding is needed. Contact `sales@openwebui.com`.
4. **Fork as last resort**: Forking gives full control but creates a maintenance burden against upstream updates.

### Design System Applicability

The design system defined in Sections 1–6 above applies **fully** to the NeuralDrive System Panel and **partially** to Open WebUI (limited to what the configuration options allow). Open WebUI's built-in dark mode provides a reasonably consistent visual pairing without custom CSS.

## Section 8: NeuralDrive Branding

- **System Panel**: Full branding — NeuralDrive logo in sidebar header, custom favicon, amber accent throughout.
- **Open WebUI**: Limited branding — `WEBUI_NAME="NeuralDrive"` in title bar, custom favicon via `STATIC_DIR`, Open WebUI logo and attribution remain visible per license.
- **Page Titles**: System Panel uses "NeuralDrive — [Page Name]". Open WebUI displays "NeuralDrive" (via WEBUI_NAME).
- **Shared Identity**: Both apps share the same favicon and dark-mode aesthetic to feel related despite different levels of customization control.
