# Directory Monitor Pro 📁

A powerful Python-based directory monitoring system with real-time file tracking, system resource monitoring, and automatic cleanup capabilities.

![Directory Monitor Banner](https://via.placeholder.com/800x200?text=Directory+Monitor+Pro)

## Features ✨

- 🔄 Real-time directory monitoring
- 📊 System resource tracking (CPU, Memory, Disk usage)
- 🔍 Duplicate file detection
- 🗑️ Automatic cleanup of old files
- 💾 Automatic file backups
- 📈 Usage statistics tracking
- 🎨 Rich, colorful terminal interface

## Screenshots 📸

### Main Interface
![Main Interface](https://via.placeholder.com/800x400?text=Main+Interface)
*The main monitoring interface showing system stats and file list*

### File Operations
![File Operations](https://via.placeholder.com/800x400?text=File+Operations)
*Automatic cleanup and backup operations in action*

### System Resources
![System Resources](https://via.placeholder.com/800x400?text=System+Resources)
*Real-time system resource monitoring*

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/ktalib/directory-monitor-pro.git
cd directory-monitor-pro
```

2. Install required packages:
```bash
pip install watchdog psutil rich colorama humanize
```

## Usage 💻

1. Modify the directory path in the script:
```python
directory_to_monitor = r"C:\Your\Path\Here"
```

2. Run the script:
```bash
python temp-file-monitor.py
```

### Configuration Options

You can customize these parameters in the script:
```python
monitor = DirectoryMonitor(
    directory_path=r"C:\Your\Path\Here",  # Directory to monitor
    max_files=10,                         # Maximum files to keep
    check_interval=5                      # Check interval in seconds
)
```

## Features in Detail 🔎

### Real-time Monitoring
- Instantly detects new files
- Tracks file creation and deletion
- Provides immediate feedback

### System Resource Tracking
- CPU usage monitoring
- Memory usage tracking
- Disk space utilization
- Real-time updates

### File Management
- Maintains specified maximum file count
- Automatically removes oldest files
- Creates backups before deletion
- Detects duplicate files

### User Interface
- Colorful terminal display
- Easy-to-read tables
- Progress indicators
- Status notifications

## Configuration File 📝

The script creates a `monitor_config.ini` file to save your settings:
```ini
[Settings]
max_files = 10
check_interval = 5
```

## Backup System 💾

- Automatically creates a `backup` directory
- Preserves deleted files
- Maintains file metadata
- Enables easy file recovery

## Requirements 📋

- Python 3.6+
- Required packages:
  - watchdog
  - psutil
  - rich
  - colorama
  - humanize

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments 🙏

- Rich library for terminal formatting
- Watchdog for file system events
- Psutil for system monitoring

## Author ✍️

Your Name - [@ktalib](https://github.com/ktalib)

## Support 🆘

If you encounter any problems or have suggestions, please open an issue in the GitHub repository.
