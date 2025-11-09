# OSC Message Listener

A simple utility to listen for and display OSC (Open Sound Control) messages.

**Website:** https://blueroar.com/osclistener  
**GitHub:** https://github.com/BlueRoar/OSCListener

## Installation

1. Install Python 3 (if not already installed)
2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

### Running as a Python Script

Run the script:
```bash
python3 osc_listener.py
```

A GUI window will open with:
- **IP Address field**: Enter the IP address to listen on (default: `127.0.0.1`)
- **Port field**: Enter the port number to listen on (default: `7700`)
- **Connect button**: Click to start/stop listening for OSC messages
- **Log area**: Displays all received OSC messages with timestamps
- **Clear Log button**: Clears the message log
- **Copy to Clipboard button**: Copies all log content to the clipboard

## Features

- Clean, formatted display of OSC messages with timestamps
- Real-time message logging
- Easy connection/disconnection
- Clear log functionality
- Copy logs to clipboard
- Status indicator showing connection state

## Example

1. Enter IP address (e.g., `127.0.0.1`)
2. Enter port number (e.g., `7700`)
3. Click "Connect"
4. OSC messages will appear in the log area with timestamps and formatted arguments
5. Use "Clear Log" to clear the display
6. Use "Copy to Clipboard" to copy all logs
