import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime
import psutil
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import init, Fore, Back, Style
import humanize
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
import configparser
import json

# Initialize colorama and rich console
init()
console = Console()

class FileMonitorHandler(FileSystemEventHandler):
    """Handler for file system events."""
    def __init__(self, callback):
        self.callback = callback
    
    def on_created(self, event):
        if not event.is_directory:
            self.callback("created", event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.callback("deleted", event.src_path)

class DirectoryMonitor:
    """Main class for directory monitoring and file management."""
    def __init__(self, directory_path: str, max_files: int = 10, check_interval: int = 5):
        """Initialize the DirectoryMonitor."""
        self.directory_path = Path(directory_path)
        self.max_files = max_files
        self.check_interval = check_interval
        self.backup_path = Path("backup")
        self.stats = {
            "files_deleted": 0,
            "total_size_cleaned": 0,
            "last_cleanup": None
        }
        self.file_hashes = {}
        self.system_stats = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0
        }

        # Initialize components
        if not self.directory_path.exists():
            raise FileNotFoundError(f"Directory {directory_path} does not exist")
        
        self.load_config()
        self.setup_backup_directory()
        self.setup_watchdog()

    def _print_banner(self):
        """Print a styled initialization banner."""
        console.print("\n" + "="*60, style="bold blue")
        console.print(" Directory Monitor System ", style="bold white on blue", justify="center")
        console.print("="*60 + "\n", style="bold blue")
        
        console.print(f"📁 Monitoring Directory: ", style="bold green", end="")
        console.print(str(self.directory_path))
        console.print(f"📊 Maximum Files: ", style="bold green", end="")
        console.print(str(self.max_files))
        console.print(f"⏱️  Check Interval: ", style="bold green", end="")
        console.print(f"{self.check_interval} seconds\n")

    def load_config(self):
        """Load configuration from file."""
        try:
            config = configparser.ConfigParser()
            if os.path.exists('monitor_config.ini'):
                config.read('monitor_config.ini')
                self.max_files = config.getint('Settings', 'max_files', fallback=self.max_files)
                self.check_interval = config.getint('Settings', 'check_interval', fallback=self.check_interval)
        except Exception as e:
            console.print(f"Error loading config: {e}", style="bold red")

    def save_config(self):
        """Save current configuration to file."""
        try:
            config = configparser.ConfigParser()
            config['Settings'] = {
                'max_files': str(self.max_files),
                'check_interval': str(self.check_interval)
            }
            with open('monitor_config.ini', 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            console.print(f"Error saving config: {e}", style="bold red")

    def setup_backup_directory(self):
        """Create backup directory if it doesn't exist."""
        try:
            self.backup_path.mkdir(exist_ok=True)
        except Exception as e:
            console.print(f"Error creating backup directory: {e}", style="bold red")
            raise

    def setup_watchdog(self):
        """Setup real-time file system monitoring."""
        try:
            self.observer = Observer()
            event_handler = FileMonitorHandler(self.handle_file_event)
            directory_str = str(self.directory_path)
            self.observer.schedule(event_handler, directory_str, recursive=False)
            self.observer.start()
        except Exception as e:
            console.print(f"Error setting up watchdog: {e}", style="bold red")
            raise

    def handle_file_event(self, event_type, file_path):
        """Handle file system events."""
        try:
            if event_type == "created":
                console.print(f"📝 New file detected: {Path(file_path).name}", style="bold green")
            elif event_type == "deleted":
                console.print(f"🗑️ File deleted: {Path(file_path).name}", style="bold red")
        except Exception as e:
            console.print(f"Error handling file event: {e}", style="bold red")

    def get_file_info(self) -> list:
        """Get list of files with their creation times and sizes."""
        files = []
        try:
            for file_path in self.directory_path.glob('*'):
                if file_path.is_file():
                    try:
                        creation_time = os.path.getctime(file_path)
                        size = os.path.getsize(file_path)
                        files.append((file_path, creation_time, size))
                    except OSError as e:
                        console.print(f"Error accessing file {file_path}: {e}", style="bold red")
        except Exception as e:
            console.print(f"Error getting file info: {e}", style="bold red")
        return files

    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash of file for duplicate detection."""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            console.print(f"Error calculating hash for {file_path}: {e}", style="bold red")
            return None

    def backup_file(self, file_path):
        """Create backup of file before deletion."""
        try:
            backup_file = self.backup_path / file_path.name
            shutil.copy2(file_path, backup_file)
            console.print(f"📦 Backup created: {backup_file.name}", style="bold blue")
        except Exception as e:
            console.print(f"Backup failed for {file_path}: {e}", style="bold red")

    def update_system_stats(self):
        """Update system resource usage statistics."""
        try:
            self.system_stats["cpu_usage"] = psutil.cpu_percent()
            self.system_stats["memory_usage"] = psutil.virtual_memory().percent
            disk = psutil.disk_usage(self.directory_path)
            self.system_stats["disk_usage"] = disk.percent
        except Exception as e:
            console.print(f"Error updating system stats: {e}", style="bold red")

    def display_system_stats(self):
        """Display system resource usage."""
        try:
            table = Table(title="System Resources", show_lines=True)
            table.add_column("Resource", style="cyan")
            table.add_column("Usage", style="magenta")
            
            table.add_row("CPU", f"{self.system_stats['cpu_usage']}%")
            table.add_row("Memory", f"{self.system_stats['memory_usage']}%")
            table.add_row("Disk", f"{self.system_stats['disk_usage']}%")
            
            console.print(table)
        except Exception as e:
            console.print(f"Error displaying system stats: {e}", style="bold red")

    def display_current_files(self, files):
        """Display current files in a formatted table."""
        try:
            table = Table(title="Current Files", show_lines=True)
            table.add_column("File Name", style="cyan")
            table.add_column("Created", style="green")
            table.add_column("Size", justify="right", style="magenta")

            for file_path, creation_time, size in files:
                creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
                size_str = humanize.naturalsize(size)
                table.add_row(file_path.name, creation_date, size_str)

            console.print(table)
        except Exception as e:
            console.print(f"Error displaying files: {e}", style="bold red")

    def detect_duplicates(self):
        """Detect and report duplicate files."""
        try:
            files = self.get_file_info()
            current_hashes = {}
            duplicates = []

            for file_path, _, _ in files:
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    if file_hash in current_hashes:
                        duplicates.append((file_path, current_hashes[file_hash]))
                    else:
                        current_hashes[file_hash] = file_path

            if duplicates:
                console.print("\n🔍 Duplicate files found:", style="bold yellow")
                for file1, file2 in duplicates:
                    console.print(f"- {file1.name} ⟷ {file2.name}", style="yellow")
        except Exception as e:
            console.print(f"Error detecting duplicates: {e}", style="bold red")

    def cleanup_old_files(self):
        """Enhanced cleanup with backup and statistics."""
        try:
            files = self.get_file_info()
            
            if len(files) > self.max_files:
                files.sort(key=lambda x: x[1])
                files_to_delete = files[:len(files) - self.max_files]
                
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    for file_path, _, size in files_to_delete:
                        try:
                            self.backup_file(file_path)
                            self.stats["files_deleted"] += 1
                            self.stats["total_size_cleaned"] += size
                            self.stats["last_cleanup"] = datetime.now().isoformat()
                            file_path.unlink()
                            console.print(f"✓ Deleted: {file_path.name} ({humanize.naturalsize(size)})", style="red")
                        except Exception as e:
                            console.print(f"Error processing {file_path}: {e}", style="bold red")
        except Exception as e:
            console.print(f"Error during cleanup: {e}", style="bold red")

    def monitor(self):
        """Enhanced monitoring with all features."""
        console.print("\n🚀 Starting enhanced directory monitor...\n", style="bold green")
        self._print_banner()
        
        try:
            while True:
                self.update_system_stats()
                files = self.get_file_info()
                current_count = len(files)
                
                os.system('cls' if os.name == 'nt' else 'clear')
                self._print_banner()
                
                console.print(f"\n📈 Monitoring Statistics:", style="bold blue")
                console.print(f"Files Deleted: {self.stats['files_deleted']}")
                console.print(f"Total Space Cleaned: {humanize.naturalsize(self.stats['total_size_cleaned'])}")
                
                self.display_system_stats()
                self.display_current_files(files)
                self.detect_duplicates()
                
                if current_count > self.max_files:
                    self.cleanup_old_files()
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.observer.stop()
            self.save_config()
            console.print("\n\n👋 Monitoring stopped by user", style="bold yellow")
        except Exception as e:
            console.print(f"Error in monitor loop: {e}", style="bold red")
            raise
        finally:
            self.observer.join()

def main():
    """Main function to run the directory monitor."""
    try:
        # You can change this path to any directory you want to monitor
        directory_to_monitor = r"C:\wamp64\tmp"  # Example path
        
        
        if not os.path.exists(directory_to_monitor):
            console.print(f"❌ Directory {directory_to_monitor} does not exist!", style="bold red")
            console.print("Please create the directory or specify a different path.", style="yellow")
            sys.exit(1)
            
        monitor = DirectoryMonitor(
            directory_path=directory_to_monitor,
            max_files=1,          # Maximum number of files to keep
            check_interval=5       # Check every 5 seconds
        )
        monitor.monitor()
    except Exception as e:
        console.print(f"❌ Failed to start monitor: {e}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main()