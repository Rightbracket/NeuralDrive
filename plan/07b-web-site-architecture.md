# 07b: Web Site Architecture & Navigation

This document defines the information architecture and navigation patterns for the NeuralDrive web interface. It builds on the infrastructure requirements in 07-web-interface.md and the visual identity established in 07a-design-system.md. The specifications here provide the structure for the detailed page designs in 07c-page-designs.

# Section 1: Application Map

NeuralDrive presents two distinct web applications to the user, served via a Caddy reverse proxy for a unified security model.

1. Open WebUI (Port 3000, Proxy :443): A third-party chat interface for model interaction, RAG document management, and user authentication. We customize this via environment variables and feature toggles (`WEBUI_NAME`, `STATIC_DIR`, feature flags). CSS injection and white-labeling are not available in the community version (see 07a §7 for constraints).
2. NeuralDrive System Panel (Port 3001, Proxy :8443/system/): A custom-built FastAPI application for hardware monitoring, service management, and low-level system administration. We have full control over this application's code and design.

GPU Hot (Port 1312, Proxy :8443/monitor/) provides the real-time telemetry data displayed within the System Panel's monitoring views.

# Section 2: Sitemap

Open WebUI (:443)
├── /login (Initial entry point)
├── / (Chat — primary interaction)
├── /models (Model management and library)
├── /documents (RAG data ingestion)
├── /admin (Open WebUI user/system settings)
└── /settings (Personal preferences)

NeuralDrive System Panel (:8443/system/)
├── /system/ (Dashboard — overall health and resource summary)
├── /system/gpu (Real-time GPU telemetry and performance)
├── /system/services (Ollama, Caddy, and background service status)
├── /system/storage (Disk usage and model weights management)
├── /system/network (Hostname, IP, and security configuration)
├── /system/logs (Real-time system and service log streaming)
├── /system/api-keys (Management of system-level access tokens)
└── /system/about (Version info, documentation, and support)

# Section 3: Navigation Design

The System Panel uses a persistent navigation shell to maintain context while switching between administrative tasks.

Sidebar Navigation
- Fixed left sidebar at 240px width.
- Collapses to a 56px icon-only rail on smaller screens.
- Top: NeuralDrive logotype (links to Dashboard).
- Center: Vertical list of navigation items with descriptive icons.
- Bottom: "Open Chat" action button with an external link icon, pointing to the Open WebUI root.

Header Bar
- Fixed at top of the viewport.
- Dynamic page title based on current route.
- Breadcrumb trail for nested navigation.
- System status badge: Hostname/IP address and a live health indicator (green/amber/red pulse).
- Quick actions: System reboot and shutdown triggers (with confirmation).

# Section 4: Page Shell Layout

┌─────────┬──────────────────────────────────────────┐
│ SIDEBAR │ HEADER BAR                               │
│         ├──────────────────────────────────────────┤
│ Logo    │                                          │
│ ─────── │            MAIN CONTENT                  │
│ Nav     │                                          │
│ Items   │            (Scrollable area)             │
│         │                                          │
│         │                                          │
│ ─────── │                                          │
│ Chat →  │                                          │
└─────────┴──────────────────────────────────────────┘

# Section 5: User Roles & Permissions

The System Panel is restricted to administrative users. General users created within Open WebUI do not have access to hardware-level controls.

| Role | Open WebUI Access | System Panel Access | Notes |
| :--- | :--- | :--- | :--- |
| Admin | Full Access | Full Access | First-boot user and designated admins. |
| User | Chat, Models, RAG | No Access | Limited to LLM interaction only. |

# Section 6: Responsive Breakpoints

The System Panel layout adapts to the viewer's screen size to ensure administrative tools remain accessible on mobile devices.

| Device | Breakpoint | Sidebar Behavior | Content |
| :--- | :--- | :--- | :--- |
| Desktop | ≥1024px | Expanded (240px) | Full width |
| Tablet | 768-1023px | Collapsed (56px) | Full width |
| Mobile | <768px | Hidden (Hamburger) | Stacked components |

Open WebUI handles its own responsive logic; our customizations must respect its existing breakpoint system.

# Section 7: URL Structure & Routing

The System Panel is a single-page application (SPA) using client-side routing, served behind the /system/ base path.

Key API Dependencies (from 08-api-services.md)
- /system/gpu → GET /api/v1/hardware/gpu (via GPU Hot)
- /system/services → GET/POST /api/v1/services/status
- /system/storage → GET /api/v1/system/disk
- /system/logs → WebSocket /api/v1/system/logs/stream

# Section 8: Cross-Application Navigation

Movement between applications is handled via explicit UI entry points to bridge the port gap.

From Open WebUI to System Panel:
- Open WebUI's community version does not support custom sidebar links or JS injection. Instead, NeuralDrive uses these approaches:
  - A `WEBUI_BANNERS` announcement with a link to the System Panel URL (persistent, dismissible).
  - An Open WebUI **Action Function** (plugin) that adds a "System Panel" button to the chat message toolbar, opening `:8443/system/` in a new tab.
  - Documentation in the first-boot welcome message directing admins to the System Panel URL.
- If Enterprise license is acquired, a proper sidebar link becomes possible.

From System Panel to Open WebUI:
- The persistent "Open Chat" button in the sidebar provides an immediate return path.
- Model references in the storage view link directly to the specific model's interaction page in Open WebUI.

Authentication Context:
- The two applications use separate authentication systems.
- Open WebUI manages its own JWT-based sessions (user accounts, login).
- The System Panel validates requests using the master API key located at `/etc/neuraldrive/api.key`.
- Admin access to the System Panel requires the API key (displayed during first-boot and available via the TUI). This is intentionally separate from Open WebUI user accounts — system administration is a higher privilege level.
