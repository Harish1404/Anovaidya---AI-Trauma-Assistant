"use client";

import React, { useState, useRef, useEffect } from "react";
import { useChatStore } from "@/store/useChatStore";
import { sendChatMessage } from "@/services/chat";
import { DoctorCard } from "./DoctorCard";
import { SeverityBadge } from "./SeverityBadge";
import { Button } from "@/components/ui/button";
import { Send, MapPin, Mail, Plus, CheckCircle, Download } from "lucide-react";
import { toast } from "sonner";

export function PhaseController() {
  const {
    userId,
    sessionId,
    phase,
    isLoading,
    doctorList,
    severityScore,
    reportDownloadUrl,
    addUserMessage,
    addAssistantMessage,
    setLoading,
    setPhase,
    setSeverity,
    setDoctorList,
    setReportReady,
    setReportDownloadUrl,
    startNewSession,
  } = useChatStore();

  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [input]);

  async function handleSend(messageOverride?: string) {
    const msg = messageOverride ?? input.trim();
    if (!msg || isLoading) return;

    addUserMessage(msg);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage({
        message: msg,
        user_id: userId,
        session_id: sessionId,
      });

      addAssistantMessage(res.response);
      setPhase(res.next_action);

      if (res.severity_score !== null) {
        setSeverity(res.severity_score);
      }
      if (res.doctors_recommended && res.doctors_recommended.length > 0) {
        setDoctorList(res.doctors_recommended);
      }
      if (res.report_ready) {
        setReportReady(true);
      }
      if (res.report_download_url) {
        setReportDownloadUrl(res.report_download_url);
      }
    } catch (err) {
      console.error("Chat error:", err);
      toast.error("Failed to get a response. Please try again.");
      addAssistantMessage(
        "I'm having trouble connecting right now. Please try again in a moment."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  // ─── COMPLETE phase ───
  if (phase === "complete") {
    return (
      <div className="border-t border-[var(--med-border)] bg-[var(--med-surface)] px-4 py-6">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 bg-[var(--med-success-bg)] text-[var(--med-success)] px-4 py-2 rounded-full text-sm font-medium">
            <CheckCircle className="w-4 h-4" />
            Triage Complete
          </div>
          {severityScore !== null && (
            <div className="flex justify-center">
              <SeverityBadge score={severityScore} />
            </div>
          )}
          <p className="text-sm text-[var(--med-text-secondary)]">
            Your report has been processed. Please visit the recommended facility at your earliest convenience.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-4">
            {reportDownloadUrl && (
              <Button
                render={
                  <a href={`http://localhost:8000${reportDownloadUrl}`} download>
                    <Download className="w-4 h-4 mr-2" />
                    Download Report (.docx)
                  </a>
                }
                variant="outline"
                className="w-full sm:w-auto border-[var(--med-border)]"
              />
            )}
            <Button
              onClick={() => {
                setInput("");
                startNewSession();
              }}
              className="w-full sm:w-auto bg-[var(--med-primary)] text-[var(--med-text-on-brand)] hover:bg-[var(--med-primary-light)]"
            >
              <Plus className="w-4 h-4 mr-2" />
              Start New Consultation
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // ─── SELECT_DOCTOR phase ───
  if (phase === "select_doctor" && doctorList.length > 0) {
    return (
      <div className="border-t border-[var(--med-border)] bg-[var(--med-surface)] px-4 py-4">
        <div className="max-w-4xl mx-auto space-y-3">
          <p className="text-sm font-medium text-[var(--med-text-primary)]">
            Select a doctor to proceed:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-80 overflow-y-auto chat-scroll">
            {doctorList.map((doc, i) => (
              <DoctorCard
                key={i}
                doctor={doc}
                onSelect={(name) => handleSend(`I want to select ${name}`)}
              />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ─── Default / continue / ask_location / ask_email phases ───
  const placeholderMap: Record<string, string> = {
    continue: "Describe your injury or symptoms...",
    continue_conversation: "Describe your injury or symptoms...",
    ask_location:
      "Enter your location (e.g., Adyar, Chennai Tamilnadu)...",
    escalate_to_doctor:
      "Enter your location to find nearby specialists...",
    ask_email: "Enter your email address (e.g., yourname@gmail.com)...",
    select_doctor: "Type the doctor's name you'd like to select...",
  };

  const iconMap: Record<string, React.ReactNode> = {
    ask_location: <MapPin className="w-4 h-4" />,
    escalate_to_doctor: <MapPin className="w-4 h-4" />,
    ask_email: <Mail className="w-4 h-4" />,
  };

  const placeholder =
    placeholderMap[phase] || "Type your message...";
  const sendIcon = iconMap[phase] || <Send className="w-4 h-4" />;

  return (
    <div className="border-t border-[var(--med-border)] bg-[var(--med-surface)] px-4 py-3">
      <div className="max-w-4xl mx-auto">
        {/* Phase hint */}
        {(phase === "ask_location" || phase === "escalate_to_doctor") && (
          <div className="flex items-center gap-2 mb-2 text-xs text-[var(--med-warning)] bg-[var(--med-warning-bg)] rounded-lg px-3 py-2">
            <MapPin className="w-3.5 h-3.5" />
            Please share your location so we can find nearby specialists
          </div>
        )}
        {phase === "ask_email" && (
          <div className="flex items-center gap-2 mb-2 text-xs text-[var(--med-info)] bg-[var(--med-info-bg)] rounded-lg px-3 py-2">
            <Mail className="w-3.5 h-3.5" />
            Share your email to receive the clinical report. Type &quot;skip&quot; to skip.
          </div>
        )}

        {/* Input bar */}
        <div className="flex items-end gap-2 border border-[var(--med-border)] bg-[var(--med-bg)] rounded-2xl p-1.5 pl-4 transition-all focus-within:border-[var(--med-border-strong)] focus-within:ring-2 focus-within:ring-[var(--med-primary)]/15">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={1}
            disabled={isLoading}
            className="flex-1 resize-none bg-transparent text-[var(--med-text-primary)] placeholder:text-[var(--med-text-muted)] py-2.5 pr-2 text-sm outline-none border-0 focus:ring-0 focus:outline-none focus-visible:ring-0 disabled:opacity-50 chat-scroll overflow-y-auto"
          />
          <Button
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="h-9 w-9 rounded-xl bg-[var(--med-primary)] text-[var(--med-text-on-brand)] hover:bg-[var(--med-primary-light)] disabled:opacity-40 shrink-0 mb-0.5"
            size="icon"
          >
            {sendIcon}
          </Button>
        </div>

        <p className="text-[10px] text-[var(--med-text-muted)] text-center mt-2">
          Anovaidya provides first-aid guidance only. Always seek professional medical advice for serious injuries.
        </p>
      </div>
    </div>
  );
}
