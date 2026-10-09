export type TopicProgress = {
  topic: string;
  attempts: number;
  avg_score: number;
};

export function ProgressList({ topics }: { topics: TopicProgress[] }) {
  if (topics.length === 0) {
    return <p className="muted">No quiz scores yet. Finish a quiz and they will show up here.</p>;
  }
  return (
    <ul className="progress-list">
      {topics.map((topic) => (
        <li key={topic.topic}>
          <div className="progress-meta">
            <strong>{topic.topic}</strong>
            <span>{topic.avg_score}% · {topic.attempts} {topic.attempts === 1 ? "attempt" : "attempts"}</span>
          </div>
          <div className="bar" aria-hidden="true">
            <span style={{ width: `${Math.max(0, Math.min(100, topic.avg_score))}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}
