import { mentorTitle } from "@/lib/mentors";

export function RichText({ text }: { text: string }) {
  const segments = text.trim().split(/(```[\s\S]*?```)/g).filter(Boolean);
  return (
    <>
      {segments.map((segment, index) => {
        if (segment.startsWith("```")) {
          const code = segment.slice(3, -3).replace(/^\w*\n/, "").replace(/\n$/, "");
          return <pre key={index}><code>{code}</code></pre>;
        }
        return segment.split(/\n{2,}/).filter(Boolean).map((block, blockIndex) => {
          const lines = block.split("\n").filter((line) => line.length > 0);
          if (lines.length > 0 && lines.every((line) => /^[-*]\s+/.test(line))) {
            return <ul key={`${index}-${blockIndex}`}>{lines.map((line, lineIndex) => <li key={lineIndex}>{inline(line.replace(/^[-*]\s+/, ""))}</li>)}</ul>;
          }
          if (lines.length > 0 && lines.every((line) => /^\d+\.\s+/.test(line))) {
            return <ol key={`${index}-${blockIndex}`}>{lines.map((line, lineIndex) => <li key={lineIndex}>{inline(line.replace(/^\d+\.\s+/, ""))}</li>)}</ol>;
          }
          return <p key={`${index}-${blockIndex}`}>{inline(block)}</p>;
        });
      })}
    </>
  );
}

function inline(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("`") && part.endsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
    return <span key={index}>{part}</span>;
  });
}

export function AgentBadge({ agent }: { agent?: string }) {
  if (!agent) return null;
  return <span className={`agent-pill agent-${agent}`}>{mentorTitle(agent)}</span>;
}
