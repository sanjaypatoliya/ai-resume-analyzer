import { render, screen } from "@testing-library/react";
import { UploadZone } from "../../components/UploadZone";

describe("UploadZone", () => {
  const noop = () => {};

  it("renders upload prompt when no file selected", () => {
    render(
      <UploadZone
        onFileSelected={noop}
        uploading={false}
        progress={0}
        fileName={null}
      />
    );
    expect(screen.getByText(/Drag & drop your resume PDF/i)).toBeInTheDocument();
    expect(screen.getByText(/PDF only, max 10MB/i)).toBeInTheDocument();
  });

  it("shows fileName when a file has been selected", () => {
    render(
      <UploadZone
        onFileSelected={noop}
        uploading={false}
        progress={0}
        fileName="my-resume.pdf"
      />
    );
    expect(screen.getByText("my-resume.pdf")).toBeInTheDocument();
  });

  it("shows upload progress bar when uploading", () => {
    render(
      <UploadZone
        onFileSelected={noop}
        uploading={true}
        progress={60}
        fileName="resume.pdf"
      />
    );
    expect(screen.getByText("Uploading...")).toBeInTheDocument();
    expect(screen.getByText("60%")).toBeInTheDocument();
  });

  it("does not show progress bar when not uploading", () => {
    render(
      <UploadZone
        onFileSelected={noop}
        uploading={false}
        progress={0}
        fileName={null}
      />
    );
    expect(screen.queryByText("Uploading...")).not.toBeInTheDocument();
  });
});
