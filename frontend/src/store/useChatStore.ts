import { create } from "zustand";
import type {
  ChatMessage,
  DoctorInfo,
  NextAction,
} from "@/types/chat_schema";

function generateId(): string {
  return crypto.randomUUID();
}

function getOrCreate(key: string): string {
  if (typeof window === "undefined") return generateId();
  const stored = localStorage.getItem(key);
  if (stored) return stored;
  const id = generateId();
  localStorage.setItem(key, id);
  return id;
}

interface ChatState {
  /* Identity — persisted in localStorage */
  userId: string;
  sessionId: string;

  /* Conversation */
  messages: ChatMessage[];
  isLoading: boolean;

  /* Backend phase state */
  phase: NextAction;
  severityScore: number | null;
  doctorList: DoctorInfo[];
  reportReady: boolean;
  reportDownloadUrl: string | null;

  /* Sidebar */
  sidebarOpen: boolean;

  /* Actions */
  addUserMessage: (content: string) => void;
  addAssistantMessage: (content: string) => void;
  setLoading: (v: boolean) => void;
  setPhase: (phase: NextAction) => void;
  setSeverity: (score: number | null) => void;
  setDoctorList: (doctors: DoctorInfo[]) => void;
  setReportReady: (v: boolean) => void;
  setReportDownloadUrl: (url: string | null) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (v: boolean) => void;
  startNewSession: () => void;
  loadSession: (sessionId: string, messages: ChatMessage[], severity: number | null) => void;
  hydrateFromLocalStorage: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  userId: "test-user",
  sessionId: "test-session",
  messages: [],
  isLoading: false,
  phase: "continue",
  severityScore: null,
  doctorList: [],
  reportReady: false,
  reportDownloadUrl: null,
  sidebarOpen: false,

  addUserMessage: (content) =>
    set((s) => ({
      messages: [...s.messages, { role: "user", content }],
    })),

  addAssistantMessage: (content) =>
    set((s) => ({
      messages: [...s.messages, { role: "assistant", content }],
    })),

  setLoading: (v) => set({ isLoading: v }),
  setPhase: (phase) => set({ phase }),
  setSeverity: (score) => set({ severityScore: score }),
  setDoctorList: (doctors) => set({ doctorList: doctors }),
  setReportReady: (v) => set({ reportReady: v }),
  setReportDownloadUrl: (url) => set({ reportDownloadUrl: url }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (v) => set({ sidebarOpen: v }),

  startNewSession: () => {
    const newSessionId = generateId();
    if (typeof window !== "undefined") {
      localStorage.setItem("anovaidya_session_id", newSessionId);
    }
    set({
      sessionId: newSessionId,
      messages: [],
      phase: "continue",
      severityScore: null,
      doctorList: [],
      reportReady: false,
      reportDownloadUrl: null,
    });
  },

  loadSession: (sessionId, messages, severity) =>
    set({
      sessionId,
      messages,
      phase: "continue",
      severityScore: severity,
      doctorList: [],
      reportReady: false,
      reportDownloadUrl: null,
    }),

  hydrateFromLocalStorage: () => {
    const userId = getOrCreate("anovaidya_user_id");
    const sessionId = getOrCreate("anovaidya_session_id");
    set({ userId, sessionId });
  },
}));
