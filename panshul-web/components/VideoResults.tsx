import type { VideoResult } from "@/components/ChatProvider";

export function VideoResults({
  videos,
  status,
}: {
  videos?: VideoResult[];
  status?: "success" | "no_results" | "unavailable" | "topic_required";
}) {
  if (status === "unavailable") {
    return <p className="video-state" role="status">Video search is temporarily unavailable. You can still ask Panshul to explain the topic here.</p>;
  }
  if (status === "topic_required") {
    return <p className="video-state" role="status">Tell Panshul which topic you want a video for.</p>;
  }
  if (status === "no_results") {
    return <p className="video-state" role="status">No matching videos were found. Try a more specific topic.</p>;
  }
  if (!videos?.length) return null;

  return (
    <section className="video-results" aria-label="YouTube video explanations">
      <h3>Video explanations</h3>
      <div className="video-results-list">
        {videos.map((video) => (
          <article className="video-result" key={video.video_id}>
            {video.thumbnail_url ? (
              <a href={video.url} target="_blank" rel="noopener noreferrer" aria-label={`Watch ${video.title} on YouTube`}>
                {/* YouTube thumbnail hosts vary; a native image avoids remote image build configuration. */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={video.thumbnail_url} alt="" loading="lazy" />
              </a>
            ) : null}
            <div className="video-result-info">
              <h4>{video.title}</h4>
              {video.channel_title ? <p>{video.channel_title}</p> : null}
              <a className="btn btn-small btn-primary" href={video.url} target="_blank" rel="noopener noreferrer">
                ▶ Watch on YouTube
              </a>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
