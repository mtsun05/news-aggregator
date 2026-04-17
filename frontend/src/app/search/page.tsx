"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

type DetailLevel = "quick" | "summary" | "detailed";

const DEMO_MODE = true;

const DEMO_RESPONSE = `## Left Perspective

**AP News** reports on the economic impact, noting rising consumer costs and supply chain disruptions affecting American businesses.

**CNN** emphasizes the humanitarian concerns and diplomatic fallout, with experts warning of long-term consequences for international relations.

## Center Perspective

**BBC News** provides a balanced overview, presenting both the administration's rationale and critics' counterarguments. The outlet notes bipartisan disagreement on the approach.

**Reuters** focuses on market reactions, reporting mixed signals from investors and economists on the policy's effectiveness.

## Right Perspective

**Fox News** highlights the administration's position, framing the policy as necessary for national security and economic independence.

**The American Conservative** offers a nuanced take, supporting the goal but questioning the implementation timeline.`;

const detailLevels: { value: DetailLevel; label: string }[] = [
  { value: "quick", label: "Quick" },
  { value: "summary", label: "Summary" },
  { value: "detailed", label: "Detailed" },
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [detailLevel, setDetailLevel] = useState<DetailLevel>("summary");
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.SubmitEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMessage = query.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setQuery("");
    setIsLoading(true);

    if (DEMO_MODE) {
      await new Promise((resolve) => setTimeout(resolve, 5000));
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: DEMO_RESPONSE },
      ]);
      setIsLoading(false);
      return;
    }

    try {
      const request = {
        query: userMessage,
        detail: detailLevel,
      };

      const res = await fetch("/api/news/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer ?? "No response received." },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] max-w-3xl mx-auto w-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
              Search the news
            </h1>
            <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
              Ask about any topic to see left, center, and right perspectives.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                    msg.role === "user"
                      ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                      : "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100 prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-li:my-0.5 prose-ol:my-1"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-zinc-100 px-4 py-3 text-sm text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400 animate-pulse">
                  Searching...
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-zinc-200 bg-white px-4 py-4 dark:border-zinc-800 dark:bg-black">
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          {/* Detail level selector */}
          <div className="flex items-center justify-center gap-1 rounded-full bg-zinc-100 p-1 self-center dark:bg-zinc-800">
            {detailLevels.map((level) => (
              <button
                key={level.value}
                type="button"
                onClick={() => setDetailLevel(level.value)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                  detailLevel === level.value
                    ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-700 dark:text-zinc-100"
                    : "text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
                }`}
              >
                {level.label}
              </button>
            ))}
          </div>

          {/* Text input */}
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about a news topic..."
              className="flex-1 rounded-full border border-zinc-300 bg-white px-4 py-3 text-sm outline-none focus:border-zinc-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:focus:border-zinc-500"
            />
            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="rounded-full bg-zinc-900 p-3 text-white transition-colors hover:not-disabled:bg-zinc-700 disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:not-disabled:bg-zinc-300"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="h-4 w-4"
              >
                <path d="M3.105 2.288a.75.75 0 0 0-.826.95l1.414 4.926A1.5 1.5 0 0 0 5.135 9.25h6.115a.75.75 0 0 1 0 1.5H5.135a1.5 1.5 0 0 0-1.442 1.086l-1.414 4.926a.75.75 0 0 0 .826.95 28.11 28.11 0 0 0 15.095-7.907.75.75 0 0 0 0-.992A28.11 28.11 0 0 0 3.105 2.288Z" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
