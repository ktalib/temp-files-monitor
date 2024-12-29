import os
import time
from pathlib import Path
from datetime import datetime
import logging
from colorama import init, Fore, Back, Style
import humanize
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Initialize colorama for Windows compatibility
init()

# Initialize Rich console
console = Console()

class DirectoryMonitor:
    def __init__(self, directory_path: str, max_files: int = 10, check_interval: int = 5):
        """
        Initialize the DirectoryMonitor.
        
        Args:
            directory_path (str): Path to monitor
            max_files (int): Maximum number of files to keep
            check_interval (int): How often to check directory (in seconds)
        """
        self.directory_path = Path(directory_path)
        self.max_files = max_files
        self.check_interval = check_interval
        
        # Validate directory exists
        if not self.directory_path.exists():
            raise FileNotFoundError(f"Directory {directory_path} does not exist")
        
        # Print initialization banner
        self._print_banner()

    def _print_banner(self):
        """Print a styled initialization banner."""
        console.print("\n" + "="*60, style="bold blue")
        console.print(" Directory Monitor System ", style="bold white on blue", justify="center")
        console.print("="*60 + "\n", style="bold blue")
        
        # Print configuration details
        console.print(f"📁 Monitoring Directory: ", style="bold green", end="")
        console.print(str(self.directory_path))
        console.print(f"📊 Maximum Files: ", style="bold green", end="")
        console.print(str(self.max_files))
        console.print(f"⏱️  Check Interval: ", style="bold green", end="")
        console.print(f"{self.check_interval} seconds\n")

    def get_file_info(self) -> list:
        """Get list of files with their creation times and sizes."""
        files = []
        for file_path in self.directory_path.glob('*'):
            if file_path.is_file():
                try:
                    creation_time = os.path.getctime(file_path)
                    size = os.path.getsize(file_path)
                    files.append((file_path, creation_time, size))
                except OSError as e:
                    console.print(f"Error accessing file {file_path}: {e}", style="bold red")
        return files

    def display_current_files(self, files):
        """Display current files in a formatted table."""
        table = Table(title="Current Files", show_lines=True)
        table.add_column("File Name", style="cyan")
        table.add_column("Created", style="green")
        table.add_column("Size", justify="right", style="magenta")

        for file_path, creation_time, size in files:
            creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
            size_str = humanize.naturalsize(size)
            table.add_row(file_path.name, creation_date, size_str)

        console.print(table)

    def cleanup_old_files(self):
        """Delete oldest files if count exceeds maximum."""
        files = self.get_file_info()
        
        if len(files) > self.max_files:
            # Sort files by creation time (oldest first)
            files.sort(key=lambda x: x[1])
            
            # Calculate how many files to delete
            files_to_delete = files[:len(files) - self.max_files]
            
            console.print("\n🗑️  Cleaning up old files...", style="bold yellow")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                for file_path, creation_time, size in files_to_delete:
                    try:
                        task_id = progress.add_task(f"Deleting {file_path.name}...", total=None)
                        file_path.unlink()
                        creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
                        console.print(f"✓ Deleted: {file_path.name} ({humanize.naturalsize(size)})", style="red")
                        progress.remove_task(task_id)
                    except OSError as e:
                        console.print(f"Error deleting file {file_path}: {e}", style="bold red")

    def monitor(self):
        """Start monitoring the directory."""
        console.print("\n🚀 Starting directory monitor...\n", style="bold green")
        
        try:
            while True:
                files = self.get_file_info()
                current_count = len(files)
                
                # Clear screen for better visibilityaz
                os.system('cls' if os.name == 'nt' else 'clear')
                self._print_banner()
                
                # Display status
                console.print(f"\n📈 Current Status:", style="bold blue")
                console.print(f"Files: {current_count}/{self.max_files}", 
                            style="bold red" if current_count > self.max_files else "bold green")
                
                # Display current files
                self.display_current_files(files)
                
                if current_count > self.max_files:
                    self.cleanup_old_files()
                
                # Display next check time
                next_check = datetime.now().timestamp() + self.check_interval
                console.print(f"\n⏳ Next check at: {datetime.fromtimestamp(next_check).strftime('%H:%M:%S')}", 
                            style="bold cyan")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            console.print("\n\n👋 Monitoring stopped by user", style="bold yellow")
        except Exception as e:
            console.print(f"\n❌ An unexpected error occurred: {e}", style="bold red")

if __name__ == "__main__":
    try:
        # Initialize and start the monitor
        monitor = DirectoryMonitor(
            directory_path=r"C:\Users\admin\AppData\Local\Temp",
            max_files=10,
            check_interval=5
        )
        monitor.monitor()
    except Exception as e:
        console.print(f"❌ Failed to start monitor: {e}", style="bold red")
