"""
Key improvements for RPA4YOU application:

1. Configuration Management
"""
import json
from pathlib import Path
from typing import Dict


class Config:
    """Centralized configuration management"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.settings = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file or create defaults"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)

        # Default configuration
        defaults = {
            "paths": {
                "root_folder": "B:/Apps",
                "qs_config": "B:/Transfer/RPA_Config_Files/QS/Default",
                "prod_config": "C:/Bot_Config",
                "backup_folder": "C:/Bot_Config/Backups"
            },
            "appearance": {
                "mode": "System",
                "theme": "blue"
            },
            "features": {
                "auto_backup": True,
                "backup_count": 5,
                "sync_scroll": True
            }
        }

        self._save_config(defaults)
        return defaults

    def _save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.settings

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self._save_config(self.settings)


"""
2. Improved File Operations with Error Handling
"""
import shutil
from datetime import datetime
from typing import Tuple, List


class FileManager:
    """Handle all file operations with proper error handling"""

    def __init__(self, config: Config):
        self.config = config

    def compare_files(self, file1: Path, file2: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Compare two files and return differences

        Returns:
            Tuple of (files_identical, added_lines, removed_lines)
        """
        try:
            if not file1.exists():
                raise FileNotFoundError(f"File not found: {file1}")
            if not file2.exists():
                raise FileNotFoundError(f"File not found: {file2}")

            with open(file1, 'r', encoding='utf-8') as f1:
                lines1 = f1.readlines()

            with open(file2, 'r', encoding='utf-8') as f2:
                lines2 = f2.readlines()

            import difflib
            differ = difflib.Differ()
            diff = list(differ.compare(lines1, lines2))

            added = [line[2:] for line in diff if line.startswith('+ ')]
            removed = [line[2:] for line in diff if line.startswith('- ')]

            return (len(added) == 0 and len(removed) == 0), added, removed

        except UnicodeDecodeError:
            raise ValueError(f"File encoding error. Files must be text files.")
        except Exception as e:
            raise Exception(f"Error comparing files: {str(e)}")

    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of a file with timestamp"""
        if not file_path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")

        backup_dir = Path(self.config.get('paths.backup_folder'))
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name

        shutil.copy2(file_path, backup_path)

        # Clean old backups
        self._cleanup_old_backups(file_path.stem, backup_dir)

        return backup_path

    def _cleanup_old_backups(self, base_name: str, backup_dir: Path):
        """Keep only the most recent N backups"""
        max_backups = self.config.get('features.backup_count', 5)

        backups = sorted(
            [f for f in backup_dir.glob(f"{base_name}_*") if f.is_file()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        for old_backup in backups[max_backups:]:
            old_backup.unlink()

    def safe_copy(self, source: Path, destination: Path, create_backup: bool = True) -> bool:
        """
        Safely copy a file with optional backup

        Returns:
            True if successful, False otherwise
        """
        try:
            if not source.exists():
                raise FileNotFoundError(f"Source file not found: {source}")

            # Create backup if destination exists and backup is enabled
            if destination.exists() and create_backup:
                self.create_backup(destination)

            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy2(source, destination)

            return True

        except Exception as e:
            print(f"Error copying file: {str(e)}")
            return False


"""
3. Better Thread Management
"""
import threading
import queue
from typing import Callable, Any


class TaskManager:
    """Manage background tasks with proper cancellation and result handling"""

    def __init__(self):
        self.current_task: Optional[threading.Thread] = None
        self.cancel_flag = threading.Event()
        self.result_queue = queue.Queue()

    def run_task(self, task_func: Callable, on_complete: Callable[[Any], None] = None,
                 on_error: Callable[[Exception], None] = None):
        """Run a task in background with callbacks"""

        if self.current_task and self.current_task.is_alive():
            return False  # Task already running

        self.cancel_flag.clear()

        def wrapper():
            try:
                result = task_func(self.cancel_flag)
                self.result_queue.put(('success', result))
            except Exception as e:
                self.result_queue.put(('error', e))

        self.current_task = threading.Thread(target=wrapper, daemon=True)
        self.current_task.start()

        # Monitor the task
        self._monitor_task(on_complete, on_error)

        return True

    def _monitor_task(self, on_complete, on_error):
        """Monitor task completion and execute callbacks"""

        def check_result():
            try:
                status, value = self.result_queue.get_nowait()
                if status == 'success' and on_complete:
                    on_complete(value)
                elif status == 'error' and on_error:
                    on_error(value)
            except queue.Empty:
                # Check again after 100ms
                if self.current_task and self.current_task.is_alive():
                    threading.Timer(0.1, check_result).start()

        threading.Timer(0.1, check_result).start()

    def cancel_current_task(self):
        """Signal the current task to cancel"""
        self.cancel_flag.set()

    def is_running(self) -> bool:
        """Check if a task is currently running"""
        return self.current_task is not None and self.current_task.is_alive()


"""
4. Improved UI Component with CustomTkinter
"""
import customtkinter as ctk
from typing import Optional


class BotSelector(ctk.CTkFrame):
    """Reusable bot selector component with search"""

    def __init__(self, master, bots: List[str], on_select: Callable[[str], None], **kwargs):
        super().__init__(master, **kwargs)

        self.bots = bots
        self.filtered_bots = bots.copy()
        self.on_select = on_select

        self._create_widgets()

    def _create_widgets(self):
        # Search entry
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self._on_search_changed)

        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Search for a bot...",
            textvariable=self.search_var,
            height=40
        )
        self.search_entry.pack(fill="x", padx=10, pady=(10, 5))
        self.search_entry.focus()

        # Scrollable frame for bot list
        self.scrollable = ctk.CTkScrollableFrame(self, label_text="Available Bots")
        self.scrollable.pack(fill="both", expand=True, padx=10, pady=5)

        # Bot buttons
        self.bot_buttons = []
        self._update_bot_list()

        # Keyboard navigation
        self.search_entry.bind('<Down>', lambda e: self._focus_first_bot())
        self.search_entry.bind('<Return>', lambda e: self._select_first_bot())

    def _on_search_changed(self, *args):
        """Filter bots based on search term"""
        search_term = self.search_var.get().lower()

        if search_term:
            self.filtered_bots = [bot for bot in self.bots if search_term in bot.lower()]
        else:
            self.filtered_bots = self.bots.copy()

        self._update_bot_list()

    def _update_bot_list(self):
        """Update the displayed bot list"""
        # Clear existing buttons
        for button in self.bot_buttons:
            button.destroy()
        self.bot_buttons.clear()

        # Create new buttons
        for i, bot in enumerate(self.filtered_bots):
            btn = ctk.CTkButton(
                self.scrollable,
                text=bot,
                command=lambda b=bot: self.on_select(b),
                anchor="w",
                height=35
            )
            btn.pack(fill="x", pady=2)
            self.bot_buttons.append(btn)

            # Keyboard navigation
            btn.bind('<Down>', lambda e, idx=i: self._focus_next_bot(idx))
            btn.bind('<Up>', lambda e, idx=i: self._focus_prev_bot(idx))

    def _focus_first_bot(self):
        if self.bot_buttons:
            self.bot_buttons[0].focus()

    def _select_first_bot(self):
        if self.filtered_bots:
            self.on_select(self.filtered_bots[0])

    def _focus_next_bot(self, current_idx):
        if current_idx < len(self.bot_buttons) - 1:
            self.bot_buttons[current_idx + 1].focus()

    def _focus_prev_bot(self, current_idx):
        if current_idx > 0:
            self.bot_buttons[current_idx - 1].focus()
        else:
            self.search_entry.focus()


"""
5. Logger Implementation
"""
import logging
from pathlib import Path


def setup_logger(name: str, log_file: str = "rpa4you.log", level=logging.INFO):
    """Setup application logger"""

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


"""
6. Example of Improved Main Application Structure
"""


class RPA4YOU_Improved(ctk.CTk):
    """Improved version with better architecture"""

    def __init__(self):
        super().__init__()

        # Initialize components
        self.config = Config()
        self.file_manager = FileManager(self.config)
        self.task_manager = TaskManager()
        self.logger = setup_logger('RPA4YOU')

        # Load saved appearance settings
        appearance = self.config.get('appearance.mode', 'System')
        theme = self.config.get('appearance.theme', 'blue')

        ctk.set_appearance_mode(appearance)
        ctk.set_default_color_theme(theme)

        # Configure window
        self.title("RPA4YOU - Developed by RPA Team")
        self.geometry("1200x900")

        # Bind cleanup on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create UI
        self._setup_ui()

        self.logger.info("Application started")

    def _setup_ui(self):
        """Setup the user interface"""
        # Create main layout
        # ... (sidebar, main frame, etc.)
        pass

    def on_closing(self):
        """Cleanup before closing"""
        # Cancel any running tasks
        if self.task_manager.is_running():
            self.task_manager.cancel_current_task()

        # Save current state
        self.logger.info("Application closing")

        self.destroy()

# Additional improvements to implement:
# - Input validation for file paths
# - Progress indicators for long operations
# - Undo/Redo functionality for config changes
# - Better error messages with suggested actions
# - Keyboard shortcuts help dialog
# - Recent files/bots list
# - Export functionality for comparisons
# - Settings dialog for configuration
# - Async file operations with asyncio
# - Unit tests for core functionality