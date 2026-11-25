export interface SubtitleStyle {
  preset: string;
  font_family: string;
  font_size: number;
  font_color: string;
  background_color: string;
  background_opacity: number;
  alignment: 'left' | 'center' | 'right';
  position_x: number;
  position_y: number;
}

export interface SubtitleSegment {
  id: string;
  start: number; // seconds
  end: number;   // seconds
  text: string;
  // UI positioning (normalized) – optional, not persisted to backend
  position_x?: number;
  position_y?: number;
}

/**
 * Parse VTT‑style subtitle text into segments.
 * Expected format per line: "00:00:05.000 --> 00:00:10.000\nSubtitle text"
 * Returns an array of segments. Lines that cannot be parsed are ignored.
 */
export function parseVtt(subtitles: string): SubtitleSegment[] {
  const lines = subtitles.split(/\r?\n/).filter(Boolean);
  const segments: SubtitleSegment[] = [];
  let i = 0;
  while (i < lines.length) {
    const timeLine = lines[i].trim();
    const match = timeLine.match(/(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})/);
    if (match && i + 1 < lines.length) {
      const start = toSeconds(match[1]);
      const end = toSeconds(match[2]);
      const text = lines[i + 1];
      segments.push({
        id: `${i}`,
        start,
        end,
        text,
      });
      i += 2; // consume timestamp and text line
    } else {
      // Not a timestamp line; skip
      i++;
    }
  }
  return segments;
}

function toSeconds(ts: string): number {
  const [h, m, s] = ts.split(":");
  return Number(h) * 3600 + Number(m) * 60 + Number(s);
}
