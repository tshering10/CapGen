import React, { useRef, useState } from "react";
import axios from "axios";

interface VideoUploadProps {
  onUploadSuccess: (url: string) => void;
}

export default function VideoUpload({ onUploadSuccess }: VideoUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string>("");

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      // assume backend endpoint /upload returns {url: string}
      const response = await axios.post("http://127.0.0.1:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onUploadSuccess(response.data.url);
    } catch (err) {
      setError("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-gray-50">
      <h2 className="text-lg font-medium text-gray-700 mb-2">Upload video</h2>
      <input
        type="file"
        accept="video/*"
        ref={fileInputRef}
        disabled={uploading}
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700"
      />
      {uploading && <p className="mt-2 text-indigo-600">Uploading…</p>}
      {error && <p className="mt-2 text-red-600">{error}</p>}
    </div>
  );
}
