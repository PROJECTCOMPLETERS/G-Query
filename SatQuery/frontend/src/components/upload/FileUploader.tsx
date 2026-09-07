import { useEffect, useRef, useState } from "react";

interface FileUploaderProps {
  file: File | null;
  onFileSelect: (file: File | null) => void;
}

const MAX_FILE_SIZE = 50 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "tif", "tiff"];

const FileUploader = ({
  file,
  onFileSelect,
}: FileUploaderProps) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState("");
  const [previewUrl, setPreviewUrl] = useState("");

  useEffect(() => {
    if (!file || /\.(tif|tiff)$/i.test(file.name)) {
      setPreviewUrl("");
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  const handleFile = (selectedFile?: File) => {
    if (!selectedFile) return;

    const extension = selectedFile.name
      .split(".")
      .pop()
      ?.toLowerCase();

    if (
      !extension ||
      !ALLOWED_EXTENSIONS.includes(extension)
    ) {
      setError(
        "Only JPG, PNG and GeoTIFF files are supported."
      );
      onFileSelect(null);
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setError("File size must be below 50 MB.");
      onFileSelect(null);
      return;
    }

    setError("");
    onFileSelect(selectedFile);
  };

  const removeFile = () => {
    onFileSelect(null);
    setError("");

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const formatFileSize = (size: number) => {
    if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`;
    }

    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="file-uploader">
      <input
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.tif,.tiff,image/jpeg,image/png,image/tiff"
        hidden
        onChange={(event) =>
          handleFile(event.target.files?.[0])
        }
      />

      <button
        type="button"
        className="attach-btn"
        title="Attach satellite image"
        aria-label="Attach satellite image"
        onClick={() => inputRef.current?.click()}
      >
        ＋
      </button>

      {file && (
        <div className="selected-file">
          {previewUrl ? (
            <img
              src={previewUrl}
              alt="Selected satellite"
              className="selected-file-preview"
            />
          ) : (
            <div className="selected-file-icon">🛰️</div>
          )}

          <div className="selected-file-details">
            <strong>{file.name}</strong>
            <span>{formatFileSize(file.size)}</span>
          </div>

          <button
            type="button"
            className="remove-file-btn"
            onClick={removeFile}
            aria-label="Remove selected file"
          >
            ×
          </button>
        </div>
      )}

      {error && <p className="file-error">{error}</p>}
    </div>
  );
};

export default FileUploader;