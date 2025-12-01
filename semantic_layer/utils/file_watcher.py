"""File watcher for hot reload."""

import asyncio
from pathlib import Path
from typing import Callable, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    # Create a dummy base class when watchdog is not available
    class FileSystemEventHandler:
        pass


if WATCHDOG_AVAILABLE:
    class ModelFileHandler(FileSystemEventHandler):
        """Handler for model file changes."""

        def __init__(self, callback: Callable[[Path], None]):
            """Initialize handler."""
            self.callback = callback

        def on_modified(self, event):
            """Handle file modification."""
            if not event.is_directory and event.src_path.endswith(('.yaml', '.yml')):
                self.callback(Path(event.src_path))
else:
    # Dummy class when watchdog is not available
    class ModelFileHandler:
        """Dummy handler when watchdog is not available."""
        
        def __init__(self, callback: Callable[[Path], None]):
            """Initialize dummy handler."""
            pass


class FileWatcher:
    """Watches model files for changes."""

    def __init__(self, directory: str, callback: Callable[[Path], None]):
        """Initialize file watcher."""
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError(
                "File watcher not available. Install with: pip install watchdog"
            )
        self.directory = Path(directory)
        self.callback = callback
        self.observer: Optional[Observer] = None

    def start(self) -> None:
        """Start watching files."""
        if self.observer:
            return

        self.observer = Observer()
        handler = ModelFileHandler(self.callback)
        self.observer.schedule(handler, str(self.directory), recursive=True)
        self.observer.start()

    def stop(self) -> None:
        """Stop watching files."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
