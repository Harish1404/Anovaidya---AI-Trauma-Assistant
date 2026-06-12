# Anovaidya Frontend Implementation Plan & Task List

This task list outlines the steps required to build the frontend application for **Anovaidya (TraumaAI)**. It is aligned strictly with the current backend functionality (FastAPI) and design system tokens specified in `styles.md`. All planned features that do not have backend endpoints (e.g., user registration, login, JWT authentication, and message streaming) have been omitted.

---

## 📱 Responsive Layout & UX Requirements (Mobile-First to 32" Display)

To deliver production-grade UI/UX, the frontend must be designed **mobile-first** while scaling beautifully up to **32-inch monitors (4K, 2K, and ultrawides)** without losing visual density or content hierarchy.

### 🔍 Key Design Guidelines:
*   **Mobile-First Implementation:**
    *   Triage history should live in a slide-out slide-over panel (`Sheet` drawer) rather than a persistent sidebar to conserve vertical screen space.
    *   Chat input, message bubbles, and action buttons must utilize full viewport width with thumb-friendly touch targets (min `44px` height).
    *   Triage questions and severity alerts should occupy center stage, utilizing full-width bottom cards or action drawers.
*   **Large Display Scaling (Laptops to 32" Monitors):**
    *   Use a centered layout grid wrapped in a maximum width container (e.g., `max-w-5xl` for chat focus and `max-w-7xl` for full layouts) to maintain a highly readable line length (~70–80 characters) and prevent horizontal text stretching.
    *   On desktop sizes, transition the triage history panel to a persistent, collapsible sidebar layout.
    *   Ensure grids (e.g., doctor cards list) automatically transition from a single-column layout on mobile, to 2-columns on laptop, and up to 3 or 4 columns on large 32" displays.
*   **Production Component Guidelines:**
    *   **Toast System:** Use `Sonner` toasts for light/success states, network anomalies, or notification alerts.
    *   **Overlays & Dialogs:** Use responsive drawers/sheets on mobile and centered `Dialog` components on desktop.
    *   **Forms:** Enforce rigid input validation on the email address and location fields using Zod combined with `react-hook-form` to display inline warnings.

---

## 📋 Legend
- `[ ]` Pending
- `[/]` In Progress
- `[x]` Completed

---

## 🎨 Phase 1: Styling & Design System Integration

Set up the core UI styling foundations to ensure the app has a calming, premium medical aesthetic that reduces user anxiety.

- [ ] **Configure CSS Variables:** Copy light and dark mode variables from [styles.md](file:///c:/Users/haris/Documents/Projects/Anovaidya/Anovaidya---AI-Trauma-Assistant/styles.md) into `frontend/src/app/globals.css`. Ensure it integrates smoothly with Tailwind CSS v4's utility configuration.
- [ ] **Define Component Styles:** Create a utility system or Tailwind components for:
  - Primary, ghost, and emergency/action buttons.
  - Chat bubbles (`.med-bubble-user`, `.med-bubble-bot`, `.med-bubble-system`).
  - Severity level badges (Low, Moderate, High, Critical) with a pulsing keyframe animation for the critical state.
  - Vitals/health progress tracks.
  - Custom text inputs and alerts.
- [ ] **Theme Switcher:** Build a theme toggle provider to switch between light mode and dark mode (adding `.dark` class to `<html>`/`<body>`).

---

## 🛠️ Phase 2: Core API Services & Client Integration

Integrate frontend models and API clients to interact with the backend service.

- [ ] **Define Schema Types:** Populate [chat_schema.ts](file:///c:/Users/haris/Documents/Projects/Anovaidya/Anovaidya---AI-Trauma-Assistant/frontend/src/types/chat_schema.ts) with TypeScript definitions:
  - `ChatMessage` (role: `"user" | "assistant"`, content: `string`)
  - `ChatRequest` (message: `string`, user_id: `string`, session_id: `string`)
  - `ChatResponse` (response: `string`, severity_score: `number | null`, doctors_recommended: `Array<any>`, report_ready: `boolean`, next_action: `string`)
  - `SessionSummary` (session_id: `string`, updated_at: `string`, severity_score: `number | null`, chief_complaint: `string`)
- [ ] **Axios Client Configuration:** Set up the global backend API path in `frontend/src/lib/axios.ts` to forward calls through `/api` (or directly target `http://localhost:8000`).
- [ ] **State Management Store (Zustand):** Create a store to handle:
  - `user_id` — Defaults to `"test-user"` (local storage check, no login page needed).
  - `session_id` — Active session UUID (automatically generated if not active).
  - `messages` — Active array of chat messages.
  - `currentSeverity` — Latest severity score (1–5) returned by backend.
  - `nextAction` — State phase identifier (`"continue" | "ask_location" | "select_doctor" | "ask_email" | "complete"`).
  - `recommendedDoctors` — List of matching doctors returned by the finder node.
  - `isLoading` — Boolean loading state (showing typing dots while backend processes request).
- [ ] **API Service Functions:** Implement endpoints in `frontend/src/services/chat.ts`:
  - `sendChatMessage(request: ChatRequest): Promise<ChatResponse>`
  - `getUserSessions(userId: string): Promise<SessionSummary[]>`
  - `getSessionHistory(sessionId: string): Promise<ChatMessage[]>`
  - `deleteSession(sessionId: string): Promise<void>`

---

## 💬 Phase 3: Trauma Chat Interface & State Machines

Build the primary user-facing conversation container. The interface must dynamically adjust to state responses returned by the backend in the `next_action` payload.

- [ ] **Chat Container Layout:** Build the scrolling conversation window. Use a warm off-white background (`--med-bg`) to keep the interface friendly. Enforce a max-width limit on the chat wrapper to align with desktop layout rules.
- [ ] **Message Bubble Components:** Build `MessageBubble.tsx` to handle standard markdown formatting and list rendering (crucial for first-aid instruction lists).
- [ ] **Typing & Loading Indicator:** Display an animated triple-dot indicator in `--med-primary-light` while waiting for the HTTP response.
- [ ] **Dynamic Phase Widgets:**
  - **`continue` Phase:** Normal message input text box and send button.
  - **`ask_location` Phase:** Render a dedicated intake card. Display a text field for geocoding input (e.g. *"Enter address or hospital coordinates"*). Sending this inputs the address straight to the chat endpoint to invoke nearby doctors search.
  - **`select_doctor` Phase:** Render a grid of cards from the `recommendedDoctors` array. Show doctor names, specialties, distances, and contact details. Grid must scale dynamically (1 col on mobile, 2 col on tablet/laptop, 3+ col on larger desktop layouts). Include a "Select Doctor" CTA which forwards the doctor's name back to the endpoint to proceed.
  - **`ask_email` Phase:** Render an email address form showing a *"Send medical report to doctor"* request. Submitting this sends the email payload to backend to run the Brevo email dispatch node. Validate input via Zod schema.
  - **`complete` Phase:** Hide inputs and render a final summary screen with confirmation that the report has been emailed, giving an option to print or start a new chat.

---

## 🗃️ Phase 4: Session History Sidebar

Allow users to retrieve and manage their history of trauma triage sessions.

- [ ] **Responsive Sidebar Layout:**
  - **Mobile:** Triggerable slide-out panel (`Sheet` component) via menu hamburger icon.
  - **Desktop (Laptop to 32"):** Persistent sidebar that can be collapsed to narrow icon bar.
- [ ] **Session Cards:** Fetch the user's past sessions via `getUserSessions(user_id)`. Render cards with:
  - Chief complaint snippet (truncated to 60 characters).
  - Severity badge (colored according to score).
  - Human-friendly relative date (e.g. *"10 mins ago"*, *"Yesterday"*).
- [ ] **Load Session:** On selecting a card, load historical messages using `getSessionHistory(session_id)`. Update active store elements to display the archive. Smoothly dismiss mobile sheet/drawer if active.
- [ ] **Delete Session:** Add a delete icon button to the list item which calls `deleteSession(session_id)` to purge logs and checkpointer states on MongoDB. Show success notification via `Sonner` toast.

---

## ✨ Phase 5: Polish & UX Details

- [ ] **Pulsing Warning Banners:** Show high-alert notifications if severity climbs to `4` or `5`. Include emergency call shortcuts (e.g. 108 / 911).
- [ ] **Micro-animations:** Apply smooth entry transitions for incoming messages (`tw-animate-css`).
- [ ] **SEO Optimization & Title Tags:** Verify index tags, responsive meta tags, and metadata definitions in `frontend/src/app/layout.tsx`.