export type JobStatus = "queued" | "processing" | "completed" | "failed";

export interface ProcessingJob {
  id: string;
  status: JobStatus;
  document_id: string | null;
  task_id: string | null;
  error: string | null;
}

export interface SubtitleSegment {
  id: string;
  start: number;
  end: number;
  text: string;
}

export interface SubtitleStyle {
  preset: string;
  font_family: string;
  font_size: number;
  font_color: string;
  background_color: string;
  background_opacity: number;
  alignment: "left" | "center" | "right";
  position_x: number;
  position_y: number;
}

export interface SubtitleDocument {
  id: string;
  segments: SubtitleSegment[];
  style: SubtitleStyle;
}
