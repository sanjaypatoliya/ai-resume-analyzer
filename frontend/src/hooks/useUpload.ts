import { useState } from "react";
import apiClient from "../api/client";
import type { UploadResponse } from "../types";

interface UploadState {
  uploading: boolean;
  progress: number;
  s3Key: string | null;
  error: string | null;
}

export function useUpload() {
  const [state, setState] = useState<UploadState>({
    uploading: false,
    progress: 0,
    s3Key: null,
    error: null,
  });

  const upload = async (file: File): Promise<string | null> => {
    setState({ uploading: true, progress: 0, s3Key: null, error: null });

    try {
      // Step 1 — get presigned URL
      const { data } = await apiClient.post<UploadResponse>("/upload", {
        file_name: file.name,
        content_type: file.type || "application/pdf",
      });

      // Step 2 — upload directly to S3 via presigned POST
      // All fields from the presigned response MUST be included before the file
      const formData = new FormData();
      Object.entries(data.upload_fields).forEach(([k, v]) => formData.append(k, v));
      formData.append("file", file);

      await axios_put(data.upload_url, formData, (progress) => {
        setState((prev) => ({ ...prev, progress }));
      });

      setState((prev) => ({ ...prev, uploading: false, progress: 100, s3Key: data.s3_key }));
      return data.s3_key;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setState((prev) => ({ ...prev, uploading: false, error: message }));
      return null;
    }
  };

  const reset = () => setState({ uploading: false, progress: 0, s3Key: null, error: null });

  return { ...state, upload, reset };
}

async function axios_put(
  url: string,
  formData: FormData,
  onProgress: (pct: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100));
    };
    xhr.onload = () => (xhr.status < 300 ? resolve() : reject(new Error(`S3 upload failed: ${xhr.status}`)));
    xhr.onerror = () => reject(new Error("Network error during upload"));
    xhr.send(formData);
  });
}
