"use client";

import { useState } from "react";

interface SubtitleEditorProps {
  videoUrl: string;
  onChange: (content: string) => void;
}

export default function SubtitleEditor({
  videoUrl,
  onChange,
}: SubtitleEditorProps) {
  const [text, setText] = useState("");

  return (
    <section className="rounded-lg border border-[#2A2E3D] bg-[#14161F] p-4">
      <h2 className="mb-2 text-lg font-medium text-white">Subtitle Editor</h2>
      <textarea
        value={text}
        onChange={(event) => {
          setText(event.target.value);
          onChange(event.target.value);
        }}
        placeholder={
          videoUrl
            ? "Edit subtitles here..."
            : "Upload a video to begin."
        }
        rows={12}
        className="w-full resize-none rounded border border-[#2A2E3D] bg-[#1B1E28] p-2 text-white focus:outline-none focus:ring-2 focus:ring-[#6366F1]"
      />
    </section>
  );
}
