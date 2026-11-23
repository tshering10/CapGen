import type { SubtitleDocument } from "@/types/api";

interface SubtitleEditorProps {
  document: SubtitleDocument | null;
}

export function SubtitleEditor({ document }: SubtitleEditorProps) {
  if (!document) {
    return <p>No subtitle document loaded.</p>;
  }

  return <section aria-label="Subtitle editor">{document.segments.length} segments</section>;
}
