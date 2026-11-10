"use client";

import * as React from "react";
import { Upload, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/toast";

const MAX_SIZE_MB = 25;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;
const ACCEPTED_TYPES = [".pdf", ".docx", ".txt"];

interface DropzoneProps {
  onFiles: (files: File[]) => void;
  disabled?: boolean;
}

const fileIcon = (name: string) => {
  const ext = name.split(".").pop()?.toLowerCase();
  switch (ext) {
    case "pdf":
      return (
        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414a1 1 0 00-.707-.293H13a2 2 0 00-2 2v4a2 2 0 01-2 2z" />
        </svg>
      );
    case "docx":
      return (
        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      );
    default:
      return <FileText className="w-6 h-6 text-gray-600" />;
  }
};

export function Dropzone({ onFiles, disabled = false }: DropzoneProps) {
  const [dragActive, setDragActive] = React.useState(false);
  const [files, setFiles] = React.useState<File[]>([]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []).filter(isAccepted);
    if (selected.length) {
      setFiles(selected);
      onFiles(selected);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const dropped = Array.from(e.dataTransfer.files).filter(isAccepted);
    if (dropped.length) {
      setFiles(dropped);
      onFiles(dropped);
    }
  };

  const isAccepted = (file: File) => {
    const ext = `.${file.name.split(".").pop()?.toLowerCase()}`;
    if (!ACCEPTED_TYPES.includes(ext)) {
      toast.error(`Unsupported file type: ${ext}`);
      return false;
    }
    if (file.size > MAX_SIZE_BYTES) {
      toast.error(`${file.name} exceeds ${MAX_SIZE_MB} MB limit`);
      return false;
    }
    return true;
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const clearFiles = () => setFiles([]);

  return (
    <div className="space-y-3">
      <div
        onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
          disabled
            ? "border-gray-300 bg-gray-50"
            : dragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 bg-white hover:border-blue-400 hover:bg-gray-50"
        }`}
      >
        <input
          type="file"
          accept={ACCEPTED_TYPES.join(",")}
          multiple
          onChange={handleInputChange}
          className="sr-only"
          disabled={disabled}
          data-testid="dropzone-input"
        />
        <div className="flex flex-col items-center justify-center gap-3 pointer-events-none">
          {dragActive ? (
            <div className="text-blue-600 font-medium">Drop files here</div>
          ) : (
            <Upload className="w-8 h-8 text-gray-400" />
          )}
          <p className="text-sm text-gray-600">
            {disabled ? "Upload disabled" : "Drag & drop files, or click to browse"}
          </p>
          <p className="text-xs text-gray-400">
            PDF, DOCX, TXT • Max {MAX_SIZE_MB} MB each
          </p>
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, i) => (
            <div key={i} className="flex items-center gap-3 px-3 py-2 rounded-lg bg-gray-50 border border-gray-200" data-testid={`dropzone-chip-${i}`}>
              {fileIcon(file.name)}
              <div className="flex-1 min-w-0">
                <div className="text-sm text-navy-900 truncate" title={file.name} data-testid="dropzone-chip-name">
                  {file.name}
                </div>
                <div className="text-xs text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </div>
              </div>
              <button
                onClick={() => removeFile(i)}
                className="text-gray-400 hover:text-red-500 transition-colors"
                aria-label={`Remove ${file.name}`}
              >
                ×
              </button>
            </div>
          ))}
          <Button variant="outline" size="sm" onClick={clearFiles} disabled={disabled}>
            Clear all
          </Button>
        </div>
      )}
    </div>
  );
}
