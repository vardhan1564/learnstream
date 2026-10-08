import { useRef, useState } from 'react';
import { toast } from 'react-toastify';
import { FiUploadCloud, FiFilm, FiRefreshCw, FiX } from 'react-icons/fi';
import api, { errorMessage } from '../../api/client';

const MAX_MB = 2048;
const ACCEPT = 'video/mp4,video/webm,video/quicktime,video/ogg,.mp4,.webm,.mov,.m4v,.ogv';

function formatSize(bytes) {
  if (bytes >= 1024 ** 3) return `${(bytes / 1024 ** 3).toFixed(2)} GB`;
  return `${Math.max(0.1, bytes / 1024 ** 2).toFixed(1)} MB`;
}

/** Reads the video's length in the browser so the admin doesn't have to type it. */
function readDurationMinutes(file) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file);
    const v = document.createElement('video');
    v.preload = 'metadata';
    v.onloadedmetadata = () => { URL.revokeObjectURL(url); resolve(Number.isFinite(v.duration) ? Math.max(1, Math.round(v.duration / 60)) : null); };
    v.onerror = () => { URL.revokeObjectURL(url); resolve(null); };
    v.src = url;
  });
}

/**
 * Uploads a lesson video to the server (stored on disk or in R2/S3, never in the database).
 * Calls onUploaded({ key, fileName, durationMinutes }) when done.
 */
export default function VideoUpload({ fileKey, fileName, onUploaded, onClear }) {
  const input = useRef(null);
  const controller = useRef(null);
  const [progress, setProgress] = useState(null);

  const pick = () => input.current?.click();

  const upload = async (file) => {
    if (!file) return;
    if (!/\.(mp4|webm|mov|m4v|ogv)$/i.test(file.name)) {
      toast.error('Choose an MP4, WebM, MOV, M4V or OGV video.');
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      toast.error(`This video is ${formatSize(file.size)}. The limit is ${MAX_MB / 1024} GB - please compress it first.`);
      return;
    }
    const durationMinutes = await readDurationMinutes(file);
    const form = new FormData();
    form.append('file', file);
    controller.current = new AbortController();
    setProgress(0);
    try {
      const { data } = await api.post('/api/admin/videos', form, {
        timeout: 0,
        signal: controller.current.signal,
        onUploadProgress: (e) => e.total && setProgress(Math.round((e.loaded / e.total) * 100)),
      });
      onUploaded({ key: data.key, fileName: data.fileName, durationMinutes });
      toast.success('Video uploaded. Save the course to publish it.');
    } catch (e) {
      if (e.code !== 'ERR_CANCELED') toast.error(errorMessage(e, 'Upload failed'));
    } finally {
      setProgress(null);
      if (input.current) input.current.value = '';
    }
  };

  return (
    <div className="video-upload">
      <input ref={input} type="file" accept={ACCEPT} hidden onChange={(e) => upload(e.target.files?.[0])} />
      {progress !== null ? (
        <div className="upload-progress">
          <div className="row small">
            <span>Uploading... {progress}%</span>
            <span className="spacer" />
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => controller.current?.abort()}><FiX /> Cancel</button>
          </div>
          <div className="progress"><div style={{ width: `${progress}%` }} /></div>
        </div>
      ) : fileKey ? (
        <div className="upload-done">
          <FiFilm />
          <span className="upload-name" title={fileName || fileKey}>{fileName || 'Uploaded video'}</span>
          <button type="button" className="btn btn-ghost btn-sm" onClick={pick}><FiRefreshCw /> Replace</button>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClear}><FiX /> Remove</button>
        </div>
      ) : (
        <button type="button" className="upload-drop" onClick={pick}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files?.[0]); }}>
          <FiUploadCloud size={22} />
          <span><strong>Choose a video</strong> or drag it here</span>
          <span className="muted small">MP4 recommended, up to {MAX_MB / 1024} GB</span>
        </button>
      )}
    </div>
  );
}
