"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useChatStore } from "@/store/useChatStore";
import { getUserSessions, getSessionHistory, deleteSession } from "@/services/chat";
import { SeverityBadge } from "@/components/chat/SeverityBadge";
import { Button } from "@/components/ui/button";
import { Plus, Trash2, MessageSquare, Loader2 } from "lucide-react";
import { toast } from "sonner";
import type { SessionSummary } from "@/types/chat_schema";

export function HistorySidebar() {
  const {
    userId,
    sessionId,
    loadSession,
    startNewSession,
    setSidebarOpen,
  } = useChatStore();

  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getUserSessions(userId);
      setSessions(data);
    } catch {
      // Silently ignore — history may not be available yet
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  async function handleLoadSession(sid: string) {
    try {
      const history = await getSessionHistory(sid);
      loadSession(sid, history.messages, history.severity_score);
      setSidebarOpen(false);
    } catch {
      toast.error("Failed to load session history.");
    }
  }

  async function handleDeleteSession(
    e: React.MouseEvent,
    sid: string
  ) {
    e.stopPropagation();
    try {
      await deleteSession(sid);
      setSessions((prev) => prev.filter((s) => s.session_id !== sid));
      toast.success("Session deleted");
    } catch {
      toast.error("Failed to delete session.");
    }
  }

  function handleNewChat() {
    startNewSession();
    setSidebarOpen(false);
  }

  /** Relative time helper */
  function relativeTime(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    if (days === 1) return "Yesterday";
    return `${days}d ago`;
  }

  return (
    <div className="flex flex-col h-full bg-[var(--sidebar)] text-[var(--sidebar-foreground)]">
      {/* Header */}
      <div className="px-4 py-4 border-b border-[var(--sidebar-border)]">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-heading font-semibold text-base">
            Consultations
          </h2>
        </div>
        <Button
          onClick={handleNewChat}
          className="w-full bg-[var(--sidebar-primary)] text-[var(--sidebar-primary-foreground)] hover:opacity-90 text-sm"
          size="sm"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Consultation
        </Button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto chat-scroll px-2 py-2 space-y-1">
        {loading && (
          <div className="flex justify-center py-8">
            <Loader2 className="w-5 h-5 animate-spin text-[var(--sidebar-primary)]" />
          </div>
        )}

        {!loading && sessions.length === 0 && (
          <div className="text-center py-8 text-sm opacity-60">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-40" />
            No past consultations
          </div>
        )}

        {sessions.map((session) => (
          <div
            key={session.session_id}
            onClick={() => handleLoadSession(session.session_id)}
            className={`
              w-full text-left rounded-lg px-3 py-3 text-sm transition-colors group cursor-pointer
              ${
                session.session_id === sessionId
                  ? "bg-[var(--sidebar-accent)] text-[var(--sidebar-accent-foreground)]"
                  : "hover:bg-[var(--sidebar-accent)]/50"
              }
            `}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                handleLoadSession(session.session_id);
              }
            }}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="truncate font-medium flex-1">
                {session.chief_complaint}
              </p>
              <button
                onClick={(e) => handleDeleteSession(e, session.session_id)}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-[var(--sidebar-border)]"
                title="Delete session"
                aria-label="Delete session"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="flex items-center gap-2 mt-1">
              {session.severity_score !== null && (
                <SeverityBadge score={session.severity_score} className="text-[10px]" />
              )}
              <span className="text-[10px] opacity-60">
                {relativeTime(session.updated_at)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

