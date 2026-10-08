/**
 * Turns whatever URL the admin pasted into something playable:
 *  - YouTube (watch, youtu.be, shorts, embed, live)  -> { type: 'iframe', src }
 *  - Vimeo                                            -> { type: 'iframe', src }
 *  - Google Drive file links                          -> { type: 'iframe', src }
 *  - anything else (mp4/webm/...)                     -> { type: 'video', src }
 */
export function toPlayable(url) {
  if (!url) return null;
  let u;
  try { u = new URL(url.trim()); } catch { return null; }
  const host = u.hostname.replace(/^www\.|^m\./, '');

  if (host === 'youtu.be') {
    const id = u.pathname.slice(1).split('/')[0];
    return id ? yt(id) : null;
  }
  if (host.endsWith('youtube.com') || host.endsWith('youtube-nocookie.com')) {
    const v = u.searchParams.get('v');
    if (v) return yt(v);
    const m = u.pathname.match(/^\/(embed|shorts|live|v)\/([\w-]{6,})/);
    if (m) return yt(m[2]);
    return null;
  }
  if (host === 'vimeo.com' || host === 'player.vimeo.com') {
    const m = u.pathname.match(/(\d{6,})/);
    return m ? { type: 'iframe', src: `https://player.vimeo.com/video/${m[1]}` } : null;
  }
  if (host === 'drive.google.com') {
    const m = u.pathname.match(/\/file\/d\/([\w-]+)/);
    return m ? { type: 'iframe', src: `https://drive.google.com/file/d/${m[1]}/preview` } : null;
  }
  return { type: 'video', src: u.toString() };
}

function yt(id) {
  return { type: 'iframe', src: `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}?rel=0&modestbranding=1` };
}
