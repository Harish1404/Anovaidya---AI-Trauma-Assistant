/** Roles for chat messages */
export type MessageRole = "user" | "assistant" | "system";

/** A single chat message displayed in the UI */
export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp?: string;
}

/** Request payload sent to POST /api/chat/ */
export interface ChatRequest {
  message: string;
  user_id: string;
  session_id: string;
}

/** Response payload from POST /api/chat/ */
export interface ChatResponse {
  response: string;
  severity_score: number | null;
  doctors_recommended: DoctorInfo[];
  report_ready: boolean;
  report_download_url: string | null;
  next_action: NextAction;
}

/** Possible next_action values from the backend */
export type NextAction =
  | "continue"
  | "continue_conversation"
  | "ask_location"
  | "escalate_to_doctor"
  | "show_doctors"
  | "select_doctor"
  | "ask_email"
  | "complete";

/** Doctor / facility info returned from the doctor_finder node */
export interface DoctorInfo {
  full_name: string;
  specialization: string;
  hospital_name: string;
  clinic_address: string;
  experience_years?: number;
  is_available?: boolean | null;
  distance_km?: number | string;
  rating?: number | null;
  user_ratings_total?: number;
  place_id?: string;
  email?: string;
  phone?: string;
}

/** Session summary from GET /api/history/sessions/:userId */
export interface SessionSummary {
  session_id: string;
  updated_at: string;
  severity_score: number | null;
  chief_complaint: string;
}

/** Full session history from GET /api/history/chat/:sessionId */
export interface SessionHistoryResponse {
  session_id: string;
  user_id: string;
  messages: ChatMessage[];
  severity_score: number | null;
}
