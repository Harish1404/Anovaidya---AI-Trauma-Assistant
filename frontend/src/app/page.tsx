"use client";

import React, { useEffect } from "react";
import { useChatStore } from "@/store/useChatStore";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { PhaseController } from "@/components/chat/PhaseController";
import { HistorySidebar } from "@/components/layout/HistorySidebar";
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Menu, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

export default function Home() {
  const { sidebarOpen, setSidebarOpen, hydrateFromLocalStorage } =
    useChatStore();
  const { theme, setTheme } = useTheme();

  // Hydrate user/session IDs from localStorage on mount
  useEffect(() => {
    hydrateFromLocalStorage();
  }, [hydrateFromLocalStorage]);

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--med-bg)]">
      {/* ── Desktop Sidebar (hidden on mobile) ── */}
      <aside className="hidden md:flex w-72 shrink-0 border-r border-[var(--med-border)]">
        <HistorySidebar />
      </aside>

      {/* ── Main Chat Area ── */}
      <main className="flex flex-col flex-1 min-w-0">
        {/* Top Bar */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--med-border)] bg-[var(--med-surface)]">
          <div className="flex items-center gap-3">
            {/* Mobile menu trigger */}
            <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
              <SheetTrigger
                render={
                  <Button
                    variant="ghost"
                    size="icon"
                    className="md:hidden text-[var(--med-text-primary)]"
                  />
                }
              >
                <Menu className="w-5 h-5" />
              </SheetTrigger>
              <SheetContent side="left" className="p-0 w-72">
                <SheetTitle className="sr-only">Session History</SheetTitle>
                <HistorySidebar />
              </SheetContent>
            </Sheet>

            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-[var(--med-primary)] flex items-center justify-center text-white text-sm font-bold">
                A
              </div>
              <div>
                <h1 className="font-heading font-semibold text-[var(--med-text-primary)] text-sm leading-tight">
                  Anovaidya
                </h1>
                <p className="text-[10px] text-[var(--med-text-muted)] leading-tight">
                  AI Trauma Assistant
                </p>
              </div>
            </div>
          </div>

          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="text-[var(--med-text-primary)]"
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
          </Button>
        </header>

        {/* Chat messages */}
        <ChatContainer />

        {/* Smart input bar */}
        <PhaseController />
      </main>
    </div>
  );
}
