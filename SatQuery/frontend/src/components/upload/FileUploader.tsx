import { useRef, useState } from "react";

interface FileUploaderProps {
  onFileSelect: (file: File | null) => void;
}

const FileUploader = ({ onFileSelect }: FileUploaderProps) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState("");

  const handleFile = (file: File | undefined) => {
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please upload an image file.");
      return;
    }

    setFileName(file.name);
    onFileSelect(file);
  };

  return (
    <div className="upload-box">
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        hidden
        onChange={(e) => handleFile(e.target.files?.[0])}
      />

      <button
        className="upload-btn"
        onClick={() => inputRef.current?.click()}
      >
        📁 Upload Satellite Image
      </button>

      {fileName && (
        <div className="file-name">
          ✓ {fileName}
        </div>
      )}
    </div>
  );
};

export default FileUploader;