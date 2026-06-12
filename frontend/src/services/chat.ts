import api from "@/lib/axios";
import type {
  ChatRequest,
  ChatResponse,
  SessionSummary,
  SessionHistoryResponse,
} from "@/types/chat_schema";

/**
 * Send a chat message to the trauma triage endpoint.
 */
export async function sendChatMessage(
  request: ChatRequest
): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat/", request);
  return data;
}

/**
 * Fetch all past sessions for a given user.
 */
export async function getUserSessions(
  userId: string
): Promise<SessionSummary[]> {
  const { data } = await api.get<SessionSummary[]>(
    `/history/sessions/${userId}`
  );
  return data;
}

/**
 * Fetch the full chat history for a specific session.
 */
export async function getSessionHistory(
  sessionId: string
): Promise<SessionHistoryResponse> {
  const { data } = await api.get<SessionHistoryResponse>(
    `/history/chat/${sessionId}`
  );
  return data;
}

/**
 * Delete a session's history and LangGraph checkpoints.
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await api.delete(`/history/chat/${sessionId}`);
}
