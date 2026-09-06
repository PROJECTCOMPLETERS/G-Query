from pathlib import Path


class FileStorageService:
    """Handles storing and retrieving uploaded files."""

    def __init__(self, upload_dir: str = "storage/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file_path: Path, data: bytes) -> str:
        """Save file data to the configured storage directory."""
        destination = self.upload_dir / file_path.name
        destination.write_bytes(data)
        return str(destination)

    def get_file(self, filename: str) -> Path:
        """Return the path of a stored file."""
        return self.upload_dir / filename

    def file_exists(self, filename: str) -> bool:
        """Check whether a stored file exists."""
        return self.get_file(filename).exists()

    def delete_file(self, filename: str) -> bool:
        """Delete a stored file if it exists."""
        path = self.get_file(filename)

        if not path.exists():
            return False

        path.unlink()
        return True