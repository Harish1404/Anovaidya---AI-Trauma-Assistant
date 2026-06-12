"use client";

import React, { useRef, useEffect } from "react";
import { useChatStore } from "@/store/useChatStore";
import { MessageBubble } from "./MessageBubble";
import { SeverityBadge } from "./SeverityBadge";

export function ChatContainer() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const severityScore = useChatStore((s) => s.severityScore);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto chat-scroll px-4 py-6">
      <div className="max-w-4xl mx-auto space-y-1">
        {/* Welcome state */}
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full min-h-[50vh] text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-[var(--med-primary)] flex items-center justify-center text-white text-2xl font-bold shadow-lg">
              A
            </div>
            <h2 className="font-heading text-2xl font-semibold text-[var(--med-text-primary)]">
              Welcome to Anovaidya
            </h2>
            <p className="text-[var(--med-text-secondary)] max-w-md text-sm leading-relaxed">
              I&apos;m your AI trauma assistant. Describe your injury or symptoms
              and I&apos;ll guide you with first-aid advice, assess severity, and
              connect you with nearby specialists if needed.
            </p>
          </div>
        )}

        {/* Severity banner */}
        {severityScore !== null && severityScore >= 4 && (
          <div className="flex justify-center mb-4">
            <div className="bg-[var(--med-danger-bg)] border border-[var(--med-danger)]/30 rounded-xl px-4 py-3 text-center max-w-md">
              <SeverityBadge score={severityScore} />
              <p className="text-xs text-[var(--med-danger)] mt-2">
                ⚠️ Please seek medical attention. Call emergency services if needed: <strong>108</strong> / <strong>112</strong>
              </p>
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex justify-start mb-3 animate-message-enter">
            <div className="w-8 h-8 rounded-full bg-[var(--med-primary)] flex items-center justify-center text-white text-xs font-bold mr-2 mt-1 shrink-0">
              A
            </div>
            <div className="bg-[var(--med-bubble-bot)] border border-[var(--med-border)] rounded-2xl rounded-bl-sm px-5 py-4">
              <div className="flex gap-1.5">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
