# 07d: Web Interactions & User Flows

This document specifies the dynamic behavior, user journeys, and interactive states for the NeuralDrive web interface. It serves as the behavioral companion to the design system (07a), architecture (07b), and page designs (07c), ensuring a consistent and predictable experience across the System Panel and Open WebUI.

## Section 1: User Flows

1. First-Boot Flow
- System boots from LiveCD/USB and displays the local IP address on the console.
- User opens a browser on a networked device and navigates to the provided IP.
- Open WebUI login page appears. User enters the default first-boot credentials.
- Redirected to the chat interface. A "Welcome to NeuralDrive" system message suggests pulling a model to start.
- User navigates to the Models page and initiates the first model pull.
- Once complete, the user returns to the chat, selects the model, and performs the first inference.
- Note: The System Panel is accessible at port :8443/system/ using the same API key for advanced management.

2. Daily Use Flow
- User opens the browser to the NeuralDrive IP.
- Open WebUI chat loads directly (authenticated via persistent cookie).
- User selects the desired model from the dropdown and begins chatting.
- User optionally opens the System Panel in a separate tab to monitor GPU temperatures or service health during long sessions.

3. Model Management Flow
- From Open WebUI: User browses the Models page, searches for a new model, and clicks "Pull". A progress bar tracks the download. The model automatically appears in the chat selection list upon completion.
- From System Panel: User visits the Storage page to view disk usage. To free space, the user identifies an unused model and deletes it after confirming the destructive action modal.

4. Troubleshooting Flow
- Chat interface shows a "Connection Error" or "Ollama Offline" banner.
- User opens the System Panel and navigates to the Services page.
- User identifies that the 'neuraldrive-ollama' service is stopped.
- User checks the GPU page to see if memory is exhausted or if the hardware is detected.
- User views the Logs page for specific error strings (e.g., "CUDA out of memory").
- User clicks "Restart" on the service card and waits for the success toast.

5. API Client Setup Flow
- User navigates to the API Keys page in the System Panel.
- User copies the generated API key and the base URL (http://<IP>:11434).
- User pastes these into an IDE extension or coding agent configuration.
- User runs a connection test within their client to verify successful integration.

## Section 2: Interaction Patterns

Data Refresh
- The System Panel uses polling-based updates rather than WebSockets to maintain simplicity.
- Metrics (GPU, CPU, RAM) refresh every 5 seconds.
- Service status refreshes every 10 seconds.
- Logs are fetched on-demand or when the user clicks the refresh icon.
- Each data card includes a "Last updated: Xs ago" indicator and a manual refresh button.

Streaming Responses
- Chat interactions utilize Server-Sent Events (SSE) provided by Open WebUI for real-time token streaming.
- Model pull progress is visualized via 2-second polling against the Ollama API status endpoint.

Destructive Actions
- Any action that stops services, deletes data, or restarts the system requires a confirmation modal.
- Pattern: User clicks button -> Modal appears ("Are you sure? Active connections will be dropped.") -> User clicks "Confirm" or "Cancel".
- Modals clearly state the immediate consequences of the action.

Long-Running Operations
- Actions like model pulls or service restarts show a progress bar if the duration is measurable.
- Indeterminate tasks show a spinner with descriptive status text (e.g., "Initializing GPU...").
- The trigger button is disabled during the operation to prevent duplicate requests.
- A success or error toast notification appears upon completion.

Form Submission
- Input fields validate on blur (losing focus).
- Submit buttons remain disabled until all required fields meet validation criteria.
- Success triggers a green toast notification and an in-place state update.
- Failure displays an inline error message near the relevant field.

Copy to Clipboard
- One-click copy icons are provided for API keys, URLs, and curl commands.
- A "Copied!" tooltip appears for 2 seconds at the cursor or button location upon success.

Search and Filter
- Search inputs are debounced by 300ms to reduce backend load.
- Results update in-place without page reloads.
- A "Clear" button is always present to reset filters.

Tables
- Columns are sortable by clicking headers, with an arrow icon indicating direction.
- Rows highlight on hover to assist with horizontal eye tracking.
- Action buttons (Edit, Delete, Restart) are right-aligned for consistent access.

## Section 3: Loading States

- Initial page load: Skeleton screens (gray placeholder blocks) match the expected layout to reduce perceived latency. Spinners are avoided for full-page loads.
- Metric refresh: The previous value remains visible, with a subtle fade-to-new animation once the update arrives.
- Service action: The specific button shows a small spinner, and the service status text changes to "Restarting..." or "Stopping...".
- Model pull: A dedicated progress bar shows percentage, download speed (MB/s), and estimated time remaining.
- Log fetch: Skeleton lines appear briefly before being replaced by the log text.

## Section 4: Error States

- Backend Unreachable: If the System API (:3001) is down, a full-page error overlay appears. Message: "Cannot connect to NeuralDrive system services. The server may be starting up. [Retry]"
- Ollama Down: The Dashboard displays a red "Ollama Offline" badge on GPU and Model cards. Chat interfaces show a warning banner at the top.
- GPU Unavailable: The GPU card shows "No GPU Detected — CPU Mode". Performance metrics switch to showing CPU-based inference statistics.
- Disk Full: The Storage page displays a critical amber warning banner. The "Pull Model" button is disabled with a tooltip: "Insufficient disk space".
- Auth Failure: A 403 response triggers a redirect to the login page with the message: "Session expired. Please log in again."
- Network Loss: If polling fails 3 consecutive times, a "Connection lost" banner appears at the top with an exponential backoff countdown for the next retry.
- Service Restart Failure: A red toast notification appears: "Failed to restart neuraldrive-ollama: [Error Reason]". The service row remains in an error state.
- Model Pull Failure: The progress bar turns red, and an inline error message is shown. "Retry" and "Cancel" buttons become available.

## Section 5: Notification System

Toast Notifications
- Slide in from the top-right of the viewport.
- Success (green border): Auto-dismiss after 3 seconds.
- Info (blue-gray border): Auto-dismiss after 5 seconds.
- Warning (amber border): Persistent until dismissed or condition changes.
- Error (red border): Persistent until manually dismissed by the user.
- Toasts stack up to 3 high; additional notifications are queued.

Inline Alerts
- Page-level banners for persistent system conditions (e.g., Disk Full).
- These cannot be dismissed and only disappear when the underlying issue is resolved.

Status Badges
- Small dots on the sidebar navigation items.
- Red dot on "Services" if any critical service is down.
- Amber dot on "GPU" if temperatures exceed 85°C.

Empty States
- Displayed when a page or table has no data (e.g., no logs found).
- Includes a centered illustration, a helpful message, and a primary action button (e.g., "Pull Your First Model").

## Section 6: Responsive Behavior

- Desktop: Multi-column dashboard layouts, full sidebar navigation, and hover-based tooltips.
- Tablet: Cards stack into a single column, the sidebar collapses into icons, and interactions transition from hover to tap.
- Mobile: Hamburger menu for navigation, stacked cards, and larger touch targets (minimum 44px). Primary actions (Save, Confirm) are anchored to the bottom of the screen.
- Charts: Width adjusts dynamically to the container. Mobile views show simplified versions with fewer data points and larger labels for readability.

## Section 7: Accessibility

- Color Contrast: All text elements meet a 4.5:1 ratio. Amber status text is specifically checked against the dark background for legibility.
- Keyboard Navigation: All interactive elements are focusable via the Tab key. A visible amber focus ring identifies the active element. Tab order follows a logical top-to-bottom, left-to-right flow.
- Screen Readers: Use of ARIA labels for icon-only buttons. Metrics and toasts are marked as aria-live regions to announce updates.
- Motion: The interface respects 'prefers-reduced-motion' by disabling slide/fade animations and using instant state transitions.
- Focus Management: When a modal closes, focus returns to the button that triggered it. After navigating to a new page, focus moves to the main h1 heading.

## Section 8: Performance Considerations

- Polling Budget: No more than 3 concurrent polling endpoints are active on any single page.
- Throttling: Search inputs are debounced to 300ms, window resize listeners to 150ms, and scroll events to 100ms.
- Lazy Loading: Log entries are paginated at 50 per page. The model list is loaded only when the user navigates to the management page.
- Caching: Service status is cached for 10 seconds; GPU metrics are cached for 2 seconds at the API level.
- Bundle Size: The System Panel frontend aims to remain under 200KB (gzipped) to ensure fast loading on local networks.
