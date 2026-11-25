import type {
  ProcessingJob,
  SubtitleDocument,
  SubtitleStyle,
} from "@/types/api";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function createTranscriptionJob(
  video: File,
  language: string | null,
): Promise<ProcessingJob> {
  const form = new FormData();
  form.append("video", video);
  if (language) form.append("language", language);

  return apiRequest<ProcessingJob>("/api/jobs/transcription", {
    method: "POST",
    body: form,
  });
}

export function getTranscriptionJob(jobId: string): Promise<ProcessingJob> {
  return apiRequest<ProcessingJob>(`/api/jobs/transcription/${jobId}`);
}

export function getSubtitleDocument(
  documentId: string,
): Promise<SubtitleDocument> {
  return apiRequest<SubtitleDocument>(
    `/api/subtitle-editor/documents/${documentId}`,
  );
}

export function addSubtitleSegment(
  documentId: string,
  segment: { start: number; end: number; text: string },
): Promise<SubtitleDocument> {
  return apiRequest<SubtitleDocument>(
    `/api/subtitle-editor/documents/${documentId}/segments`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(segment),
    },
  );
}

export function updateSubtitleText(
  documentId: string,
  segmentId: string,
  text: string,
): Promise<SubtitleDocument> {
  return apiRequest<SubtitleDocument>(
    `/api/subtitle-editor/documents/${documentId}/segments/${segmentId}/text`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    },
  );
}

export function updateSubtitleTimestamps(
  documentId: string,
  segmentId: string,
  start: number,
  end: number,
): Promise<SubtitleDocument> {
  return apiRequest<SubtitleDocument>(
    `/api/subtitle-editor/documents/${documentId}/segments/${segmentId}/timestamps`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start, end }),
    },
  );
}

export function deleteSubtitleSegment(
  documentId: string,
  segmentId: string,
): Promise<SubtitleDocument> {
  return apiRequest<SubtitleDocument>(
    `/api/subtitle-editor/documents/${documentId}/segments/${segmentId}`,
    { method: "DELETE" },
  );
}

export function splitSubtitleSegment(
  documentId: string,
  segmentId: string,
  timestamp: number,
): Promise<SubtitleDocument> {
  return apiRequest<SubtitleDocument>(
    `/api/subtitle-editor/documents/${documentId}/segments/${segmentId}/split`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ timestamp }),
    },
  );
}

export function mergeSubtitleSegment(
  documentId: string,
  segmentId: string,
  nextSegmentId: string,
): Promise<SubtitleDocument> {
  return apiRequest<SubtitleDocument>(
    `/api/subtitle-editor/documents/${documentId}/segments/${segmentId}/merge`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ next_segment_id: nextSegmentId }),
    },
  );
}

export function updateSubtitleStyle(
  documentId: string,
  style: SubtitleStyle,
): Promise<SubtitleDocument> {
  return apiRequest<SubtitleDocument>(
    `/api/subtitle-editor/documents/${documentId}/style`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(style),
    },
  );
}

export async function downloadSrt(documentId: string): Promise<void> {
  const response = await fetch(
    `${API_URL}/api/video-renderer/documents/${documentId}/srt`,
    { method: "POST" },
  );
  if (!response.ok) {
    throw new Error(await response.text() || "SRT export failed");
  }
  downloadBlob(await response.blob(), "subtitles.srt");
}

export async function renderVideo(
  documentId: string,
  video: File,
): Promise<void> {
  const form = new FormData();
  form.append("video", video);

  const response = await fetch(
    `${API_URL}/api/video-renderer/documents/${documentId}/render`,
    { method: "POST", body: form },
  );
  if (!response.ok) {
    throw new Error(await response.text() || "Video rendering failed");
  }
  downloadBlob(await response.blob(), "capgen-rendered.mp4");
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = window.document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  window.document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
