import { useRef, useState } from 'react';
import { toPlayable } from '../utils/video';

/**
 * Plays either an uploaded video (type "UPLOAD": a short-lived signed link, played in <video>)
 * or an external link (YouTube, Vimeo, Google Drive, direct .mp4).
 * onExpired is called if an uploaded video's link has expired so the page can fetch a fresh one.
 */
export default function VideoPlayer({ url, type, title, onEnded, onExpired }) {
  const lastRefresh = useRef(0);
  const [failedUrl, setFailedUrl] = useState(null);

  // A signed link may have expired (e.g. the tab was left open for hours): ask for a fresh one,
  // but only once a minute so a genuinely broken file can't cause a reload loop.
  const handleError = () => {
    if (onExpired && Date.now() - lastRefresh.current > 60_000) {
      lastRefresh.current = Date.now();
      onExpired();
    } else {
      setFailedUrl(url);
    }
  };

  if (type === 'UPLOAD' && url && failedUrl === url) {
    return (
      <div className="video-frame video-empty">
        <p>This video couldn't be played. Reload the page, and if it keeps happening, tell your instructor.</p>
      </div>
    );
  }
  if (type === 'UPLOAD' && url) {
    return (
      <div className="video-frame">
        <video
          key={url}
          src={url}
          controls
          playsInline
          preload="metadata"
          controlsList="nodownload"
          onContextMenu={(e) => e.preventDefault()}
          onEnded={onEnded}
          onError={handleError}
          title={title}
        />
      </div>
    );
  }
  const playable = toPlayable(url);
  if (!playable) {
    return (
      <div className="video-frame video-empty">
        <p>This video link can't be played here.</p>
        {url && <a href={url} target="_blank" rel="noreferrer" className="btn btn-outline btn-sm">Open video in a new tab</a>}
      </div>
    );
  }
  return (
    <div className="video-frame">
      {playable.type === 'iframe' ? (
        <iframe
          key={playable.src}
          src={playable.src}
          title={title || 'Lesson video'}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
          allowFullScreen
          referrerPolicy="strict-origin-when-cross-origin"
        />
      ) : (
        <video key={playable.src} src={playable.src} controls playsInline controlsList="nodownload" onEnded={onEnded} />
      )}
    </div>
  );
}
