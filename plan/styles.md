# Anovaidya UI Style Guide & Design System

This document outlines the visual tokens, component styling, and design guidelines for the Anovaidya (TraumaAI) platform. The theme is designed to provide a calm, reassuring, and professional medical interface, reducing stress and anxiety for users dealing with trauma.

---

## 🎨 Palette Foundation

The health palette is built on three core colours that work together psychologically:
*   **Teal (The Anchor):** Signals balance, clinical clarity, and mental calm. Humans instinctively read teal as a "safe medical environment" — it sits between the trust of blue and the vitality of green.
*   **Green (Vitality & Progress):** Used for positive states, confirmations, health indicators, and anything that means "you are okay."
*   **Cream / Warm White (Breathing Room):** Pure white feels sterile and cold for a medical app people use during stress or illness. Cream keeps the interface warm and human.

---

## 🔧 Complete Token System

### Light Mode CSS Variables

```css
:root {
  /* Surfaces */
  --med-bg:              #F5FAF7;   /* teal-tinted off-white — base page bg */
  --med-surface:         #FFFFFF;   /* cards, panels, chat bubbles */
  --med-surface-alt:     #E1F5EE;   /* teal-50 — hover states, subtle fills */
  --med-surface-warm:    #FAEEDA;   /* cream — for human/empathy moments */

  /* Brand */
  --med-primary:         #0F6E56;   /* teal-600 — primary actions, nav */
  --med-primary-light:   #1D9E75;   /* teal-400 — hover, secondary brand */
  --med-accent:          #3B6D11;   /* green-600 — success, vitals positive */
  --med-accent-light:    #639922;   /* green-400 — progress bars, indicators */

  /* Text */
  --med-text-primary:    #085041;   /* teal-800 — headings, strong content */
  --med-text-secondary:  #0F6E56;   /* teal-600 — body, labels */
  --med-text-muted:      #5DCAA5;   /* teal-200 — placeholders, hints */
  --med-text-on-brand:   #FFFFFF;   /* text on teal backgrounds */

  /* Borders */
  --med-border:          #9FE1CB;   /* teal-100 — default borders */
  --med-border-strong:   #1D9E75;   /* teal-400 — focused states */

  /* Semantic */
  --med-success:         #3B6D11;   /* green-600 */
  --med-success-bg:      #EAF3DE;   /* green-50 */
  --med-warning:         #854F0B;   /* amber-600 */
  --med-warning-bg:      #FAEEDA;   /* amber-50 */
  --med-danger:          #A32D2D;   /* red-600 */
  --med-danger-bg:       #FCEBEB;   /* red-50 */
  --med-info:            #085041;   /* teal-800 */
  --med-info-bg:         #E1F5EE;   /* teal-50 */

  /* Chat specific */
  --med-bubble-user:     #0F6E56;   /* user message bg */
  --med-bubble-user-fg:  #FFFFFF;
  --med-bubble-bot:      #FFFFFF;   /* bot message bg */
  --med-bubble-bot-fg:   #085041;
  --med-bubble-system:   #E1F5EE;   /* system / info message bg */
  --med-bubble-system-fg:#0F6E56;

  /* Severity indicators (triage) */
  --med-severity-low:    #639922;   /* green — routine */
  --med-severity-mid:    #BA7517;   /* amber — moderate, monitor */
  --med-severity-high:   #E24B4A;   /* red — urgent */
  --med-severity-critical:#791F1F;  /* deep red — emergency */
}
```

### Dark Mode CSS Variables

```css
.dark {
  --med-bg:              #04342C;   /* teal-900 — deep teal page bg */
  --med-surface:         #085041;   /* teal-800 — cards, panels */
  --med-surface-alt:     #0F6E56;   /* teal-600 — hover, secondary surface */
  --med-surface-warm:    #412402;   /* amber-900 — warm moments in dark */

  --med-primary:         #5DCAA5;   /* teal-200 — primary actions in dark */
  --med-primary-light:   #9FE1CB;   /* teal-100 */
  --med-accent:          #97C459;   /* green-200 */
  --med-accent-light:    #C0DD97;   /* green-100 */

  --med-text-primary:    #E1F5EE;   /* teal-50 */
  --med-text-secondary:  #9FE1CB;   /* teal-100 */
  --med-text-muted:      #5DCAA5;   /* teal-200 */
  --med-text-on-brand:   #04342C;   /* dark text on light teal buttons */

  --med-border:          #0F6E56;   /* teal-600 */
  --med-border-strong:   #5DCAA5;   /* teal-200 */

  --med-success:         #97C459;
  --med-success-bg:      #173404;
  --med-warning:         #EF9F27;
  --med-warning-bg:      #412402;
  --med-danger:          #F09595;
  --med-danger-bg:       #501313;
  --med-info:            #9FE1CB;
  --med-info-bg:         #085041;

  --med-bubble-user:     #1D9E75;
  --med-bubble-user-fg:  #E1F5EE;
  --med-bubble-bot:      #085041;
  --med-bubble-bot-fg:   #E1F5EE;
  --med-bubble-system:   #0F6E56;
  --med-bubble-system-fg:#9FE1CB;

  --med-severity-low:    #97C459;
  --med-severity-mid:    #EF9F27;
  --med-severity-high:   #F09595;
  --med-severity-critical:#F7C1C1;
}
```

---

## 🏛️ Where Each Colour Lives in the UI

### 🗺️ Navigation & Shell
*   **Top nav / sidebar background:** `--med-primary` (teal-600)
*   **Nav text and icons:** `--med-text-on-brand` (white)
*   **Active nav item:** `--med-surface-alt` tinted highlight with a `--med-primary-light` left border
*   **Page background:** `--med-bg` (teal-tinted off-white — *never pure white*)

### 💬 Chat Interface

| UI Element | Color and styling tokens |
| :--- | :--- |
| **User message bubble** | `--med-bubble-user` background + white text |
| **Bot / AI message bubble** | White background (`--med-bubble-bot`) + `--med-text-primary` |
| **System messages** (e.g. "Session started") | `--med-bubble-system` background |
| **Typing indicator dots** | `--med-primary-light` (animated) |
| **Timestamp text** | `--med-text-muted` |
| **Input field border** | `--med-border` &rarr; `--med-border-strong` on focus |
| **Send button** | `--med-primary` background |

### 🚨 Symptom / Severity Badges
Use these consistently so patients learn the colour language:
*   🟢 **Green badge** (`--med-severity-low`) &mdash; Routine, not urgent
*   🟡 **Amber badge** (`--med-severity-mid`) &mdash; Monitor, follow up recommended
*   🔴 **Red badge** (`--med-severity-high`) &mdash; Seek care today
*   🚨 **Deep red badge** (`--med-severity-critical`) &mdash; Emergency, go now

### 📊 Vitals & Health Data Cards
*   **Card surface:** `--med-surface` (white)
*   **Card border:** `--med-border`
*   **Positive reading (normal range):** `--med-success` text + `--med-success-bg`
*   **Out-of-range reading:** `--med-danger` text + `--med-danger-bg`
*   **Borderline reading:** `--med-warning` text + `--med-warning-bg`
*   **Progress bars** (e.g. medication adherence): `--med-accent-light` fill on `--med-surface-alt` track

### 📝 Forms (Patient intake, symptom checker)
*   **Label:** `--med-text-secondary`
*   **Input bg:** `--med-surface`
*   **Input border:** `--med-border`
*   **Focus ring:** `--med-border-strong` with 2px spread
*   **Error state:** `--med-danger` border + `--med-danger-bg` background
*   **Helper text:** `--med-text-muted`
*   **Submit / primary CTA:** `--med-primary` background

### 🔔 Alerts & Notifications
*   **Info alert:** `--med-info-bg` + `--med-info` text + teal left border
*   **Success alert:** `--med-success-bg` + `--med-success` text
*   **Warning alert:** `--med-warning-bg` + `--med-warning` text
*   **Danger / emergency alert:** `--med-danger-bg` + `--med-danger` text (add a subtle pulse animation for critical cases)

### 🩺 Doctor / Specialist Cards
*   **Card bg:** `--med-surface`
*   **Availability dot:** `--med-severity-low` (green = available now)
*   **Specialty tag:** `--med-surface-alt` bg with `--med-primary` text
*   **Rating stars:** `--med-accent-light`

---

## 🧱 Component Stylesheet

```css
/* Base medical app components — all using var(--med-*) */

/* Primary button */
.med-btn {
  background-color: var(--med-primary);
  color: var(--med-text-on-brand);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  transition: background-color 0.15s ease;
}
.med-btn:hover { 
  background-color: var(--med-primary-light); 
}

/* Ghost button */
.med-btn-ghost {
  background: transparent;
  color: var(--med-primary);
  border: 1px solid var(--med-border-strong);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.875rem;
}

/* Card */
.med-card {
  background-color: var(--med-surface);
  border: 1px solid var(--med-border);
  border-radius: 12px;
  padding: 20px;
}

/* Chat bubble — user */
.med-bubble-user {
  background-color: var(--med-bubble-user);
  color: var(--med-bubble-user-fg);
  border-radius: 18px 18px 4px 18px;
  padding: 10px 16px;
  max-width: 75%;
  align-self: flex-end;
}

/* Chat bubble — bot */
.med-bubble-bot {
  background-color: var(--med-bubble-bot);
  color: var(--med-bubble-bot-fg);
  border: 1px solid var(--med-border);
  border-radius: 18px 18px 18px 4px;
  padding: 10px 16px;
  max-width: 80%;
  align-self: flex-start;
}

/* System message */
.med-bubble-system {
  background-color: var(--med-bubble-system);
  color: var(--med-bubble-system-fg);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 0.8rem;
  text-align: center;
  align-self: center;
}

/* Severity badge */
.med-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}
.med-badge-low      { background: var(--med-success-bg); color: var(--med-success); }
.med-badge-moderate { background: var(--med-warning-bg); color: var(--med-warning); }
.med-badge-high     { background: var(--med-danger-bg);  color: var(--med-danger);  }
.med-badge-critical {
  background: var(--med-danger);
  color: #fff;
  animation: critical-pulse 1.8s ease-in-out infinite;
}

@keyframes critical-pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.75; }
}

/* Input */
.med-input {
  width: 100%;
  padding: 10px 14px;
  background: var(--med-surface);
  border: 1px solid var(--med-border);
  border-radius: 8px;
  color: var(--med-text-primary);
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.med-input:focus {
  border-color: var(--med-border-strong);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--med-primary) 15%, transparent);
}
.med-input.error {
  border-color: var(--med-danger);
  background-color: var(--med-danger-bg);
}

/* Alert */
.med-alert {
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 3px solid;
  font-size: 0.875rem;
}
.med-alert-info     { background: var(--med-info-bg);    color: var(--med-info);    border-color: var(--med-primary); }
.med-alert-success  { background: var(--med-success-bg); color: var(--med-success); border-color: var(--med-success); }
.med-alert-warning  { background: var(--med-warning-bg); color: var(--med-warning); border-color: var(--med-warning); }
.med-alert-danger   { background: var(--med-danger-bg);  color: var(--med-danger);  border-color: var(--med-danger);  }

/* Progress bar (medication adherence, vitals tracking) */
.med-progress-track {
  height: 6px;
  background: var(--med-surface-alt);
  border-radius: 999px;
  overflow: hidden;
}
.med-progress-fill {
  height: 100%;
  background: var(--med-accent-light);
  border-radius: 999px;
  transition: width 0.4s ease;
}
```

---

## 🚦 Colour Do's and Don'ts

### Do 👍
*   Use cream (`--med-surface-warm`) for empathetic moments (e.g. mental health check-in screens, "how are you feeling today?") — it subconsciously reduces clinical coldness.
*   Keep severity colours consistent everywhere — once a user learns red means urgent, never use red for anything else.
*   Use green exclusively for positive health signals — never for decorative purposes.
*   Give the chat container a slightly different bg from the page (`--med-bg` page, `--med-surface` chat area) so it reads as a dedicated space.

### Don't 👎
*   Use pure `#FFFFFF` as the page background — it reads as a clinical hospital form, not a supportive health companion.
*   Use teal for danger/error states — teal is the trust anchor, mixing it with alerts breaks the semantic system.
*   Add decorative colours (purple, pink, coral) anywhere — the palette's restraint is what makes it feel medically credible.
*   Use red anywhere except severity/danger — even buttons should use teal, never red, unless the action is genuinely destructive.

---

## 🩺 Applying to Anovaidya Specifically

Since the app workflow moves from **Triage** &rarr; **Severity** &rarr; **Doctor Matching** &rarr; **Email Dispatch**, map the palette to your backend signals / states like this:

| App Stage / Node State | Color Signal | Element Mapping |
| :--- | :--- | :--- |
| **Conversation node** (gathering symptoms) | Teal surfaces, calm | `--med-surface`, `--med-primary` |
| **Severity assessment result** | Dynamic severity color scale | Badge matching severity scale |
| **Doctor matched** | Green success state | `--med-success-bg` card |
| **Email dispatched** | Info alert | `--med-info-bg` confirmation banner |
| **High severity detected (Severity 4-5)** | Danger alert with pulse | `--med-badge-critical` pulsing badge / alert |
| **No doctor available** | Warning state | `--med-alert-warning` banner |