import { renderHook, act, waitFor } from "@testing-library/react";
import { useUpload } from "../../hooks/useUpload";
import apiClient from "../../api/client";

vi.mock("../../api/client", () => ({
  default: { post: vi.fn(), get: vi.fn() },
}));

const mockPost = vi.mocked(apiClient.post);

function mockXHR(status = 200) {
  const instance = {
    open: vi.fn(),
    upload: { onprogress: null as unknown },
    onload: null as (() => void) | null,
    onerror: null as (() => void) | null,
    status,
    send: vi.fn(function (this: { onload: (() => void) | null }) {
      const self = this;
      Promise.resolve().then(() => {
        if (self.onload) self.onload();
      });
    }),
  };
  vi.stubGlobal("XMLHttpRequest", function () { return instance; });
  return instance;
}

afterEach(() => vi.restoreAllMocks());

describe("useUpload", () => {
  it("has correct initial state", () => {
    const { result } = renderHook(() => useUpload());
    expect(result.current.uploading).toBe(false);
    expect(result.current.progress).toBe(0);
    expect(result.current.s3Key).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it("uploads successfully and returns s3Key", async () => {
    mockXHR(200);
    mockPost.mockResolvedValueOnce({
      data: {
        upload_url: "https://s3.example.com/upload",
        upload_fields: { key: "uploads/abc/resume.pdf", policy: "abc123" },
        s3_key: "uploads/abc/resume.pdf",
        expires_in: 300,
      },
    });

    const { result } = renderHook(() => useUpload());
    const file = new File(["content"], "resume.pdf", { type: "application/pdf" });

    let s3Key: string | null = null;
    await act(async () => {
      s3Key = await result.current.upload(file);
    });

    await waitFor(() => expect(result.current.uploading).toBe(false));
    expect(s3Key).toBe("uploads/abc/resume.pdf");
    expect(result.current.s3Key).toBe("uploads/abc/resume.pdf");
    expect(result.current.error).toBeNull();
    expect(mockPost).toHaveBeenCalledWith("/upload", {
      file_name: "resume.pdf",
      content_type: "application/pdf",
    });
  });

  it("sets error when API call fails", async () => {
    mockPost.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useUpload());
    const file = new File(["content"], "resume.pdf", { type: "application/pdf" });

    await act(async () => {
      await result.current.upload(file);
    });

    expect(result.current.error).toBe("Network error");
    expect(result.current.s3Key).toBeNull();
  });

  it("sets error when S3 upload fails", async () => {
    mockXHR(500);
    mockPost.mockResolvedValueOnce({
      data: {
        upload_url: "https://s3.example.com/upload",
        upload_fields: {},
        s3_key: "uploads/abc/resume.pdf",
        expires_in: 300,
      },
    });

    const { result } = renderHook(() => useUpload());
    const file = new File(["content"], "resume.pdf", { type: "application/pdf" });

    await act(async () => {
      await result.current.upload(file);
    });

    await waitFor(() => expect(result.current.uploading).toBe(false));
    expect(result.current.error).toMatch(/S3 upload failed/);
  });

  it("reset() restores initial state", async () => {
    mockPost.mockRejectedValueOnce(new Error("fail"));
    const { result } = renderHook(() => useUpload());
    const file = new File(["x"], "r.pdf", { type: "application/pdf" });

    await act(async () => {
      await result.current.upload(file);
    });

    act(() => result.current.reset());
    expect(result.current.error).toBeNull();
    expect(result.current.s3Key).toBeNull();
    expect(result.current.progress).toBe(0);
  });
});
