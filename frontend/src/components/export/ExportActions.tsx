import React, { useState } from "react";
import axios from "axios";

interface ExportActionsProps {
  videoUrl: string;
  subtitles: string;
}

export default function ExportActions({ videoUrl, subtitles }: ExportActionsProps) {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState("");

  const handleExport = async () => {
    if (!videoUrl) return;
    setExporting(true);
    setError("");
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/export",
        { video_url: videoUrl, subtitles },
        { responseType: "blob" }
      );
      const blob = new Blob([response.data], { type: "text/vtt" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "captions.vtt";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError("Export failed. Please try again.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-gray-50">
      <h2 className="text-lg font-medium text-gray-700 mb-2">Export</h2>
      <button
        onClick={handleExport}
        disabled={exporting || !videoUrl}
        className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
      >
        {exporting ? "Exporting…" : "Download Captions"}
      </button>
      {error && <p className="mt-2 text-red-600">{error}</p>}
    </div>
  );
}
