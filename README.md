# Crate Cleaner

A lightweight automation that removes songs from a Spotify playlist once you've listened to them. Useful for temporary queues, Discover Weekly clones, or inbox-style music sorting.

## How It Works

On each run, the script:

1. Fetches your 50 most recently played tracks from the Spotify Web API.
2. Loads the target playlist.
3. Finds tracks that appear in both lists (played for at least 30 seconds).
4. Removes those tracks from the playlist.

When scheduled to run periodically, this keeps the playlist limited to music you haven't heard yet.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Spotify Premium account

## Setup

### 1. Create a Spotify app

1. Open the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Create a new app.
3. Under **Settings**, add this redirect URI: `http://127.0.0.1:8080`
4. Under **User Management**, add your Spotify account email so you can use the app outside developer mode.

### 2. Configure the project

Clone the repository and create a `.env` file in the project root:

```bash
SPOTIFY_CLIENT_ID="your_client_id_here"
SPOTIFY_CLIENT_SECRET="your_client_secret_here"
SPOTIFY_REDIRECT_URI="http://127.0.0.1:8080"
SPOTIFY_PLAYLIST_ID="your_target_playlist_id_here"
```

Install dependencies:

```bash
uv sync
```

### 3. Authenticate once

Run the script manually before scheduling it. This opens a browser login and writes a `.cache` file with your refresh token:

```bash
uv run --env-file .env -- python main.py
```

## Scheduling

### Mac

`launchd` can run jobs on a sleeping Mac, unlike cron. Create the file `com.user.cratecleaner.plist` with the following contents:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.cratecleaner</string>

    <key>WorkingDirectory</key>
    <string>/path/to/repo/crate-cleaner</string>

    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/uv</string>
        <string>run</string>
        <string>--env-file</string>
        <string>.env</string>
        <string>--</string>
        <string>python</string>
        <string>main.py</string>
    </array>

    <key>StartInterval</key>
    <integer>3600</integer>

    <key>LimitLoadToSessionType</key>
    <string>Aqua</string>

    <key>StandardOutPath</key>
    <string>/path/to/repo/crate-cleaner/launchd_output.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/repo/crate-cleaner/launchd_error.log</string>
</dict>
</plist>
```

Update these values for your machine:

- `WorkingDirectory` — absolute path to the project root
- `ProgramArguments` — path to your `uv` binary (e.g. `/opt/homebrew/bin/uv` on Apple Silicon)
- `StandardOutPath` / `StandardErrorPath` — log file locations

Install the LaunchAgent:

```bash
ln -s com.user.cratecleaner.plist ~/Library/LaunchAgents/com.user.cratecleaner.plist
```

and load the service:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.cratecleaner.plist
```

To stop it:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.cratecleaner.plist
```

### Linux

Use a **systemd user timer** to run the script hourly.

Create `~/.config/systemd/user/crate-cleaner.service`:

```ini
[Unit]
Description=Crate Cleaner Spotify playlist sync

[Service]
Type=oneshot
WorkingDirectory=/path/to/discover-cleaner
ExecStart=/home/you/.local/bin/uv run --env-file .env -- python main.py
StandardOutput=append:/path/to/discover-cleaner/systemd_output.log
StandardError=append:/path/to/discover-cleaner/systemd_error.log
```

Create `~/.config/systemd/user/crate-cleaner.timer`:

```ini
[Unit]
Description=Run Crate Cleaner hourly

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h
Persistent=true

[Install]
WantedBy=timers.target
```

Update these values for your machine:

- `WorkingDirectory` — absolute path to the project root
- `ExecStart` — path to your `uv` binary (often `~/.local/bin/uv` after installing with the official installer)
- `StandardOutput` / `StandardError` — log file locations

Enable and start the timer:

```bash
systemctl --user daemon-reload
systemctl --user enable --now crate-cleaner.timer
```

Check that it is scheduled:

```bash
systemctl --user list-timers crate-cleaner.timer
```

To stop it:

```bash
systemctl --user disable --now crate-cleaner.timer
```

**Cron alternative:** If you prefer cron or do not use systemd, add an hourly entry (adjust paths):

```cron
0 * * * * cd /path/to/discover-cleaner && /home/you/.local/bin/uv run --env-file .env -- python main.py >> /path/to/discover-cleaner/cron.log 2>&1
```

### PC

Use **Task Scheduler** to run the script hourly. A small wrapper script keeps the working directory and logging straightforward.

Create `run-crate-cleaner.bat` in the project root:

```bat
@echo off
cd /d C:\path\to\discover-cleaner
"C:\Users\you\.local\bin\uv.exe" run --env-file .env -- python main.py >> crate-cleaner.log 2>&1
```

Update these values for your machine:

- `cd /d` path — absolute path to the project root
- `uv.exe` path — often `%USERPROFILE%\.local\bin\uv.exe` after installing with the official installer

Create the scheduled task (run in PowerShell or Command Prompt):

```powershell
schtasks /Create /TN "Crate Cleaner" /SC HOURLY /TR "C:\path\to\discover-cleaner\run-crate-cleaner.bat" /F
```

Or use the Task Scheduler GUI:

1. Open **Task Scheduler** → **Create Basic Task…**
2. **Trigger:** Daily, then check **Repeat task every** → **1 hour**
3. **Action:** Start a program → browse to `run-crate-cleaner.bat`
4. Finish, then open the task properties and confirm **Start in (optional)** is set to the project root if logs fail to write

To remove the task:

```powershell
schtasks /Delete /TN "Crate Cleaner" /F
```
