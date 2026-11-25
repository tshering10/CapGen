"use client";
import { DragEvent, useEffect, useRef, useState } from "react";

import {
  addSubtitleSegment,
  createTranscriptionJob,
  deleteSubtitleSegment,
  downloadSrt,
  getSubtitleDocument,
  getTranscriptionJob,
  mergeSubtitleSegment,
  renderVideo,
  splitSubtitleSegment,
  updateSubtitleStyle,
  updateSubtitleText,
  updateSubtitleTimestamps,
} from "@/lib/api";
import type { ProcessingJob, SubtitleDocument } from "@/types/api";
import type { SubtitleSegment } from "@/types/subtitles";
import VideoPreview from "@/components/preview/VideoPreview";

export default function Home() {
  const fileInput = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [video, setVideo] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState("");
  const [language, setLanguage] = useState("");
  const [job, setJob] = useState<ProcessingJob | null>(null);
  const [document, setDocument] = useState<SubtitleDocument | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [activeSegmentId, setActiveSegmentId] = useState<string | null>(null);
  const [selectedSegmentId, setSelectedSegmentId] = useState<string | null>(null);

  // Poll transcription job status
  useEffect(() => {
    if (!job || !["queued", "processing"].includes(job.status)) return;
    const timer = window.setInterval(async () => {
      try {
        const latest = await getTranscriptionJob(job.id);
        setJob(latest);
        if (latest.status === "completed" && latest.document_id) {
          setDocument(await getSubtitleDocument(latest.document_id));
          window.clearInterval(timer);
        }
        if (latest.status === "failed") {
          setError(latest.error ?? "Transcription failed.");
          window.clearInterval(timer);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Could not check transcription.");
      }
    }, 2000);
    return () => window.clearInterval(timer);
  }, [job]);

  function selectFile(file?: File) {
    if (!file) return;
    if (!/\.(mp4|mov|m4v|mkv|avi|webm)$/i.test(file.name)) {
      setError("Choose an MP4, MOV, M4V, MKV, AVI, or WebM video.");
      return;
    }
    setError("");
    setJob(null);
    setDocument(null);
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    setVideoUrl(URL.createObjectURL(file));
    setVideo(file);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    selectFile(event.dataTransfer.files[0]);
  }

  async function generate() {
    if (!video) {
      setError("Choose a video first.");
      return;
    }
    setBusy(true);
    setError("");
    setDocument(null);
    try {
      setJob(await createTranscriptionJob(video, language || null));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function editText(segmentId: string, text: string) {
    if (!document) return;
    setDocument({
      ...document,
      segments: document.segments.map((s) => (s.id === segmentId ? { ...s, text } : s)),
    });
  }

  async function saveText(segmentId: string, text: string) {
    if (!document) return;
    try {
      setDocument(await updateSubtitleText(document.id, segmentId, text));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Text update failed.");
    }
  }

  async function saveTimestamps(segmentId: string, field: "start" | "end", value: number) {
    if (!document) return;
    const seg = document.segments.find((s) => s.id === segmentId);
    if (!seg) return;
    try {
      setDocument(
        await updateSubtitleTimestamps(
          document.id,
          segmentId,
          field === "start" ? value : seg.start,
          field === "end" ? value : seg.end,
        ),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Timestamp update failed.");
    }
  }

  async function removeSegment(segmentId: string) {
    if (!document) return;
    try {
      setDocument(await deleteSubtitleSegment(document.id, segmentId));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed.");
    }
  }

  async function splitSegment(segmentId: string) {
    if (!document) return;
    const seg = document.segments.find((s) => s.id === segmentId);
    if (!seg) return;
    const mid = seg.start + (seg.end - seg.start) / 2;
    try {
      setDocument(await splitSubtitleSegment(document.id, segmentId, mid));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Split failed.");
    }
  }

  async function mergeSegment(segmentId: string, index: number) {
    if (!document || !document.segments[index + 1]) return;
    try {
      setDocument(
        await mergeSubtitleSegment(document.id, segmentId, document.segments[index + 1].id),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Merge failed.");
    }
  }

  async function addSegment() {
    if (!document) return;
    const last = document.segments.at(-1);
    const start = last?.end ?? 0;
    try {
      setDocument(
        await addSubtitleSegment(document.id, { start, end: start + 2, text: "" }),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not add subtitle.");
    }
  }

  async function applyStyle(preset: string) {
    if (!document) return;
    try {
      setDocument(
        await updateSubtitleStyle(document.id, { ...document.style, preset: preset.toLowerCase() }),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Style update failed.");
    }
  }

  async function exportSrt() {
    if (!document) return;
    try {
      await downloadSrt(document.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "SRT export failed.");
    }
  }

  async function exportVideo() {
    if (!document || !video) return;
    setBusy(true);
    try {
      await renderVideo(document.id, video);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Video export failed.");
    } finally {
      setBusy(false);
    }
  }

  const handleActiveChange = (segment: SubtitleSegment | null) => {
    setActiveSegmentId(segment?.id ?? null);
  };

  const status =
    job?.status === "processing"
      ? "Processing"
      : job?.status === "completed"
        ? "Completed"
        : job?.status === "failed"
          ? "Failed"
          : job?.status === "queued"
            ? "Queued"
            : "Waiting";

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-5 py-8 text-white">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-lg font-semibold">CapGen</h1>
        {job && (
          <span className={`text-sm ${job.status === "completed" ? "text-[#10B981]" : "text-[#94A3B8]"}`}>
            {status}
          </span>
        )}
      </header>

      <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
        <div>
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
            className="flex min-h-64 items-center justify-center rounded-xl border border-dashed border-[#434960] bg-[#14161F]"
          >
            {videoUrl ? (
              <VideoPreview
                src={videoUrl}
                segments={document ? document.segments : []}
                videoRef={videoRef}
                style={document?.style}
                selectedSegmentId={selectedSegmentId}
                onSelectSegment={setSelectedSegmentId}
                onStyleChange={(nextStyle) => {
                  if (!document) return;
                  setDocument({ ...document, style: nextStyle });
                }}
                onPositionCommit={(nextStyle) => {
                  if (!document) return;
                  void updateSubtitleStyle(document.id, nextStyle)
                    .then(setDocument)
                    .catch((e: unknown) =>
                      setError(e instanceof Error ? e.message : "Style update failed."),
                    );
                }}
                onActiveChange={handleActiveChange}
              />
            ) : (
              <div className="px-6 text-center">
                <p className="font-medium">Drop a short-form video here</p>
                <p className="mt-1 text-sm text-[#94A3B8]">MP4, MOV, M4V, MKV, AVI, or WebM</p>
                <button
                  type="button"
                  onClick={() => fileInput.current?.click()}
                  className="mt-5 rounded-lg bg-[#6366F1] px-4 py-2 text-sm font-medium"
                >
                  Choose video
                </button>
                <input
                  ref={fileInput}
                  type="file"
                  accept="video/mp4,video/quicktime,video/webm,video/x-matroska"
                  className="hidden"
                  onChange={(e) => selectFile(e.target.files?.[0])}
                />
              </div>
            )}
          </div>

          {video && (
            <div className="mt-3 flex items-center justify-between text-sm">
              <span className="truncate text-[#94A3B8]">{video.name}</span>
              <button
                type="button"
                onClick={() => {
                  if (videoUrl) URL.revokeObjectURL(videoUrl);
                  setVideoUrl("");
                  setVideo(null);
                  setJob(null);
                  setDocument(null);
                }}
                className="ml-4 text-[#94A3B8] hover:text-white"
              >
                Remove
              </button>
            </div>
          )}
        </div>

        <aside className="rounded-xl border border-[#2A2E3D] bg-[#14161F] p-4">
          <label className="block text-sm text-[#94A3B8]">
            Spoken language
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="mt-2 h-10 w-full rounded-lg border border-[#2A2E3D] bg-[#1B1E28] px-3 text-sm text-white"
            >
              <option value="">Auto-detect</option>
              <option value="en">English</option>
              <option value="ne">Nepali</option>
              <option value="hi">Hindi</option>
            </select>
          </label>
          <button
            type="button"
            onClick={generate}
            disabled={!video || busy || job?.status === "processing"}
            className="mt-4 h-11 w-full rounded-lg bg-[#6366F1] text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
          >
            {job?.status === "processing" ? "Processing..." : "Generate subtitles"}
          </button>
          {error && <p className="mt-3 text-sm text-[#F59E0B]">{error}</p>}
        </aside>
      </section>

      {document && (
        <section className="mt-6 rounded-xl border border-[#2A2E3D] bg-[#14161F] p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h2 className="font-medium">Subtitles</h2>
            <div className="flex gap-2">
              <button type="button" onClick={addSegment} className="rounded-lg border border-[#434960] px-3 py-2 text-sm">Add</button>
              <select
                value={document.style.preset}
                onChange={(e) => applyStyle(e.target.value)}
                className="rounded-lg border border-[#434960] bg-[#1B1E28] px-3 py-2 text-sm"
              >
                <option value="classic">Classic</option>
                <option value="bold">Bold</option>
                <option value="dynamic">Dynamic</option>
                <option value="highlight">Highlight</option>
              </select>
              <button type="button" onClick={exportSrt} className="rounded-lg border border-[#434960] px-3 py-2 text-sm">SRT</button>
              <button type="button" onClick={exportVideo} disabled={busy} className="rounded-lg bg-[#10B981] px-3 py-2 text-sm font-semibold disabled:opacity-50">MP4</button>
            </div>
          </div>
          <div className="space-y-2">
            {document.segments.map((segment, idx) => (
              <div
                key={segment.id}
                className={`grid gap-2 rounded-lg border border-[#2A2E3D] p-3 md:grid-cols-[86px_86px_1fr_auto] ${
                  selectedSegmentId === segment.id
                    ? "bg-[#222638] ring-1 ring-[#6366F1]"
                    : activeSegmentId === segment.id
                      ? "bg-[#1B1E28]"
                      : ""
                }`}
                onClick={() => {
                  setSelectedSegmentId(segment.id);
                  if (videoRef.current) videoRef.current.currentTime = segment.start;
                }}
              >
                <input
                  aria-label="Start time"
                  type="number"
                  step="0.1"
                  value={segment.start}
                  onChange={(e) => saveTimestamps(segment.id, "start", Number(e.target.value))}
                  className="rounded border border-[#2A2E3D] bg-[#1B1E28] px-2 py-2 text-sm"
                />
                <input
                  aria-label="End time"
                  type="number"
                  step="0.1"
                  value={segment.end}
                  onChange={(e) => saveTimestamps(segment.id, "end", Number(e.target.value))}
                  className="rounded border border-[#2A2E3D] bg-[#1B1E28] px-2 py-2 text-sm"
                />
                <input
                  value={segment.text}
                  onChange={(e) => editText(segment.id, e.target.value)}
                  onBlur={(e) => saveText(segment.id, e.target.value)}
                  className="min-w-0 rounded border border-[#2A2E3D] bg-[#1B1E28] px-3 py-2 text-sm"
                />
                <div className="flex items-center gap-1">
                  <button type="button" onClick={() => splitSegment(segment.id)} className="px-2 py-2 text-sm text-[#94A3B8] hover:text-white">Split</button>
                  {idx < document.segments.length - 1 && (
                    <button type="button" onClick={() => mergeSegment(segment.id, idx)} className="px-2 py-2 text-sm text-[#94A3B8] hover:text-white">Merge</button>
                  )}
                  <button type="button" onClick={() => removeSegment(segment.id)} className="px-2 py-2 text-sm text-[#94A3B8] hover:text-[#F59E0B]">Delete</button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
