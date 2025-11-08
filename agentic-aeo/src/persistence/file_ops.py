"""
Atomic File Operations for Data Persistence

Provides safe file operations with locking to prevent data corruption
in concurrent agent execution scenarios.
"""

import fcntl
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class AtomicFileWriter:
    """
    Atomic file write operations with file locking.

    Ensures data integrity during concurrent writes by:
    1. Writing to temporary file first
    2. Acquiring exclusive lock
    3. Atomically replacing original file

    Example:
        >>> writer = AtomicFileWriter()
        >>> data = {"campaign_id": "camp_123", "status": "completed"}
        >>> writer.write_json(Path("campaign.json"), data)
    """

    def __init__(self):
        """Initialize atomic file writer"""
        pass

    def write_json(
        self,
        file_path: Path,
        data: Dict[str, Any],
        indent: int = 2,
        create_parents: bool = True,
    ) -> None:
        """
        Write JSON data atomically with file locking.

        Args:
            file_path: Target file path
            data: Dictionary to write as JSON
            indent: JSON indentation (default: 2)
            create_parents: Create parent directories if needed

        Raises:
            IOError: If file operations fail
            ValueError: If data is not JSON serializable

        Example:
            >>> writer = AtomicFileWriter()
            >>> writer.write_json(
            ...     Path(".aeo-agent-data/campaigns/camp_123/manifest.json"),
            ...     {"campaign_id": "camp_123", "status": "in_progress"}
            ... )
        """
        # Create parent directories if needed
        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file first
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp"
        )

        try:
            # Convert datetime objects to ISO format strings
            serializable_data = self._make_json_serializable(data)

            # Write JSON to temp file
            with open(temp_fd, 'w', encoding='utf-8') as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(serializable_data, f, indent=indent, ensure_ascii=False)
                    f.flush()
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Atomically replace original file
            Path(temp_path).replace(file_path)

        except Exception as e:
            # Clean up temp file on error
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass
            raise IOError(f"Failed to write JSON to {file_path}: {e}") from e

    def read_json(
        self,
        file_path: Path,
        default: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Read JSON data with file locking.

        Args:
            file_path: File to read
            default: Default value if file doesn't exist

        Returns:
            Dictionary loaded from JSON file

        Raises:
            IOError: If file read fails
            ValueError: If JSON parsing fails

        Example:
            >>> writer = AtomicFileWriter()
            >>> data = writer.read_json(
            ...     Path("campaign.json"),
            ...     default={"status": "not_found"}
            ... )
        """
        # Return default if file doesn't exist
        if not file_path.exists():
            if default is not None:
                return default
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}") from e
        except Exception as e:
            raise IOError(f"Failed to read JSON from {file_path}: {e}") from e

    def append_to_jsonl(
        self,
        file_path: Path,
        data: Dict[str, Any],
        create_parents: bool = True,
    ) -> None:
        """
        Append JSON line to JSONL file atomically.

        Useful for appending task results or log entries.

        Args:
            file_path: JSONL file path
            data: Dictionary to append as JSON line
            create_parents: Create parent directories if needed

        Example:
            >>> writer = AtomicFileWriter()
            >>> writer.append_to_jsonl(
            ...     Path("campaign_tasks.jsonl"),
            ...     {"task_id": "task_123", "status": "completed"}
            ... )
        """
        # Create parent directories if needed
        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert datetime objects to ISO format strings
        serializable_data = self._make_json_serializable(data)

        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json_line = json.dumps(serializable_data, ensure_ascii=False)
                    f.write(json_line + '\n')
                    f.flush()
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        except Exception as e:
            raise IOError(f"Failed to append to {file_path}: {e}") from e

    def read_jsonl(
        self,
        file_path: Path,
        default: Optional[list] = None,
    ) -> list[Dict[str, Any]]:
        """
        Read all lines from JSONL file.

        Args:
            file_path: JSONL file to read
            default: Default value if file doesn't exist

        Returns:
            List of dictionaries (one per line)

        Example:
            >>> writer = AtomicFileWriter()
            >>> tasks = writer.read_jsonl(Path("campaign_tasks.jsonl"))
            >>> print(f"Loaded {len(tasks)} tasks")
        """
        # Return default if file doesn't exist
        if not file_path.exists():
            if default is not None:
                return default
            return []

        try:
            lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                # Acquire shared lock
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    for line in f:
                        line = line.strip()
                        if line:
                            lines.append(json.loads(line))
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            return lines

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON line in {file_path}: {e}") from e
        except Exception as e:
            raise IOError(f"Failed to read JSONL from {file_path}: {e}") from e

    def _make_json_serializable(self, data: Any) -> Any:
        """
        Convert data to JSON-serializable format.

        Handles:
        - datetime objects → ISO format strings
        - Pydantic models → dict
        - Sets → lists

        Args:
            data: Data to convert

        Returns:
            JSON-serializable version of data
        """
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {k: self._make_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._make_json_serializable(item) for item in data]
        elif isinstance(data, set):
            return list(data)
        elif hasattr(data, 'model_dump'):
            # Pydantic model
            return self._make_json_serializable(data.model_dump())
        else:
            return data


# Singleton instance for convenience
file_writer = AtomicFileWriter()


# Convenience functions
def write_json(file_path: Path, data: Dict[str, Any], **kwargs) -> None:
    """Write JSON atomically (convenience function)"""
    file_writer.write_json(file_path, data, **kwargs)


def read_json(
    file_path: Path,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Read JSON with locking (convenience function)"""
    return file_writer.read_json(file_path, default)


def append_to_jsonl(file_path: Path, data: Dict[str, Any], **kwargs) -> None:
    """Append to JSONL atomically (convenience function)"""
    file_writer.append_to_jsonl(file_path, data, **kwargs)


def read_jsonl(
    file_path: Path,
    default: Optional[list] = None,
) -> list[Dict[str, Any]]:
    """Read JSONL file (convenience function)"""
    return file_writer.read_jsonl(file_path, default)


# Example usage
if __name__ == "__main__":
    # Test atomic writes
    test_dir = Path("/tmp/aeo_test")
    test_dir.mkdir(exist_ok=True)

    # Test JSON write/read
    json_file = test_dir / "test.json"
    test_data = {
        "campaign_id": "camp_123",
        "status": "in_progress",
        "created_at": datetime.utcnow(),
        "tasks": ["task_1", "task_2"],
    }

    print("Writing JSON...")
    write_json(json_file, test_data)

    print("Reading JSON...")
    loaded_data = read_json(json_file)
    print(f"Loaded: {loaded_data}")

    # Test JSONL append/read
    jsonl_file = test_dir / "test.jsonl"

    print("\nAppending to JSONL...")
    for i in range(3):
        append_to_jsonl(jsonl_file, {"task_id": f"task_{i}", "status": "completed"})

    print("Reading JSONL...")
    lines = read_jsonl(jsonl_file)
    print(f"Loaded {len(lines)} lines:")
    for line in lines:
        print(f"  {line}")

    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print("\nTest complete!")
