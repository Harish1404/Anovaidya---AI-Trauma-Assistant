"use client";

import React from "react";
import type { ChatMessage } from "@/types/chat_schema";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="flex justify-center my-2 animate-message-enter">
        <div className="bg-[var(--med-bubble-system)] text-[var(--med-bubble-system-fg)] rounded-lg px-4 py-2 text-xs text-center max-w-md">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3 animate-message-enter`}
    >
      {/* Avatar for bot */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-[var(--med-primary)] flex items-center justify-center text-white text-xs font-bold mr-2 mt-1 shrink-0">
          A
        </div>
      )}

      <div
        className={`
          max-w-[80%] sm:max-w-[75%] px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap break-words
          ${
            isUser
              ? "bg-[var(--med-bubble-user)] text-[var(--med-bubble-user-fg)] rounded-2xl rounded-br-sm"
              : "bg-[var(--med-bubble-bot)] text-[var(--med-bubble-bot-fg)] border border-[var(--med-border)] rounded-2xl rounded-bl-sm"
          }
        `}
      >
        <MessageContent content={message.content} />
      </div>
    </div>
  );
}

/** Simple markdown-like rendering for bold text and line breaks */
function MessageContent({ content }: { content: string }) {
  // Split by newlines and render each line
  const lines = content.split("\n");

  return (
    <div className="space-y-1">
      {lines.map((line, i) => (
        <p key={i} className={line.trim() === "" ? "h-2" : ""}>
          {renderInline(line)}
        </p>
      ))}
    </div>
  );
}

/** Handle **bold** and *italic* */
function renderInline(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  // Match **bold** or *italic*
  const regex = /\*\*(.+?)\*\*|\*(.+?)\*/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    // Text before the match
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    if (match[1]) {
      // **bold**
      parts.push(
        <strong key={match.index} className="font-semibold">
          {match[1]}
        </strong>
      );
    } else if (match[2]) {
      // *italic*
      parts.push(
        <em key={match.index} className="italic">
          {match[2]}
        </em>
      );
    }
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : [text];
}
