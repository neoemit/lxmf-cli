# LXMF Interactive Client

**Feature-Rich Terminal-based LXMF Messaging Client for Reticulum**

A powerful, cross-platform command-line interface for [LXMF](https://github.com/markqvist/lxmf) messaging protocol over [Reticulum Network](https://reticulum.network/).

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Android-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>

## ✨ Features

### 📨 Messaging
- **Send and receive** LXMF messages over Reticulum mesh networks
- **Reply functionality** - Quick reply to the last received message with auto-targeting
- **Message history** - Persistent storage of all conversations
- **Conversation view** - Browse full message threads with specific users
- **Real-time delivery tracking** - Progress indicators and delivery confirmations with timing
- **Proper display name handling** - Correctly shows sender display names from LXMF announces

### 👥 Contacts & Peer Discovery
- **Contact management** - Save contacts with nicknames and fixed index numbers
- **Auto-discovery** - Automatically detects announced LXMF peers on the network
- **Display name caching** - Remembers display names from network announces with persistent storage
- **Quick messaging** - Send messages using contact numbers (e.g., `s 3 hello`)
- **Peer list** - View all discovered peers with last-seen timestamps and auto-indexing
- **Smart contact display** - Shows nickname → Display Name → Hash for easy identification

### 🛡️ Security Features
- **Stamp Cost Protection** - Require proof-of-work to prevent spam (configurable 0-32 bits)
- **Stamp validation** - Validates incoming message stamps against your requirements
- **Invalid stamp handling** - Option to ignore/accept messages with insufficient stamps
- **Blacklist system** - Block unwanted senders completely (exclusive feature!)
- **Persistent blacklist** - Blocked addresses saved across sessions

### 🔔 Notifications (Granular Control)
- **Platform-specific sounds**:
  - Windows: Musical beep melody
  - Linux: System notification sounds
  - Android/Termux: Vibration patterns + system notifications
- **Terminal bell** - Traditional alert sound (toggle on/off)
- **Visual flash** - Colorful ripple effects for incoming messages (toggle on/off)
- **Customizable alerts** - Enable/disable each notification type independently
- **Test function** - Test your notification settings before receiving messages

### 📊 Statistics & Information
- **Message statistics** - Track sent/received messages globally and per-user
- **System status** - View uptime, network info, security settings, and connection details
- **Conversation list** - See all users you've messaged with indexed navigation
- **Plugin statistics** - View loaded and enabled plugins

### 🔌 Plugin System
- **Extensible architecture** - Add custom commands and functionality
- **Message handlers** - Plugins can process incoming messages
- **Auto-loading** - Plugins loaded automatically from `plugins/` directory
- **Enable/disable** - Control plugins without deleting files
- **Hot reload** - Reload plugins without restarting the client
- Examples: Echo bot, remote control, chat bots, custom commands

### ⚙️ Customization
- **Interactive settings menu** - Easy configuration without editing files
- **Custom display name** - Set your visible identity on the network
- **Announce interval** - Configure auto-announce frequency (30s minimum)
- **Discovery alerts** - Toggle notifications for newly discovered peers
- **Notification preferences** - Fine-tune sound, bell, and visual alerts
- **Security settings** - Configure stamp costs and blacklist

### 🎨 User Interface
- **Color-coded output** - Beautiful terminal colors using colorama
- **Categorized help menu** - Organized commands by function (Messaging, Contacts, Security, etc.)
- **Responsive design** - Adapts to screen width (mobile-friendly)
- **Mobile optimization** - Compact layouts for Android/Termux
- **Dynamic prompt** - Visual indicator (●) for unread messages
- **Progress indicators** - Real-time message sending progress
- **Clean separators** - Adaptive line widths that fit any screen

### 🖥️ Cross-Platform Support
- **Windows** - Full support with native beep sounds
- **Linux** - Desktop and server environments
- **Android/Termux** - Mobile support with vibration and notifications
- **macOS** - Compatible (limited testing)

## 📋 Requirements

- Python 3.8 or higher
- [RNS (Reticulum Network Stack)](https://github.com/markqvist/Reticulum)
- [LXMF](https://github.com/markqvist/lxmf)
- colorama (for colored terminal output)

### Optional (for Termux/Android)
- termux-api package
- Termux:API app (from F-Droid or Play Store)

## 🚀 Installation

### Quick Install
```bash
# Clone the repository
git clone https://github.com/fr33n0w/lxmf-cli.git
cd lxmf-cli

# Install dependencies
pip install rns lxmf colorama

# Run the client
python lxmf-cli.py
```

### Termux/Android Installation
```bash
# Update packages
pkg update && pkg upgrade

# Install Python and dependencies
pkg install python git

# Install required Python packages
pip install rns lxmf colorama

# Optional: Install termux-api for notifications and vibration
pkg install termux-api
# Also install Termux:API app from F-Droid or Play Store

# Clone and run
git clone https://github.com/fr33n0w/lxmf-cli.git
cd lxmf-cli
python lxmf-cli.py
```

### First Run Setup

On first launch, you'll be prompted to:
1. **Set your display name** - This is how others will see you on the network
2. **Configure announce interval** - How often you announce your presence (default: 300s, minimum: 30s)

The client will automatically create necessary directories and files:
- `lxmf_client_identity` - Your cryptographic identity
- `lxmf_client_storage/` - Messages, contacts, configuration, and plugins

## 📖 Usage

### Basic Commands
```bash
# Messaging
send <name/#/hash> <message>    (s)  - Send a message
reply <message>                 (re) - Reply to last message
messages [count]                (m)  - Show recent messages
messages list                        - List all conversations
messages user <#>                    - View full conversation

# Contacts & Peers
contacts                        (c)  - List all contacts
add <name> <hash>              (a)  - Add a contact
remove <name>                  (rm) - Remove a contact
peers                          (p)  - List announced LXMF peers
sendpeer <#> <message>         (sp) - Send to peer by number
addpeer <#> [name]             (ap) - Add peer to contacts

# Security
blacklist [list]               (bl) - Show blacklist
block <#/name/hash>                 - Block a contact/peer
unblock <#/name/hash>               - Unblock address
blacklist add <#/name/hash>         - Add to blacklist
blacklist remove <#/name/hash>      - Remove from blacklist
blacklist clear                     - Clear entire blacklist

# Information & Stats
stats                          (st) - Show messaging statistics
status                              - Show system status
address                      (addr) - Show your LXMF address

# Settings
settings                      (set) - Open settings menu
name <new_name>                (n)  - Change display name
interval <seconds>             (i)  - Change announce interval

# Plugins
plugin [list]                       - List all plugins
plugin enable <name>                - Enable a plugin
plugin disable <name>               - Disable a plugin
plugin reload                       - Reload all plugins

# System
announce                      (ann) - Announce now
clear                         (cls) - Clear the screen
restart                        (r)  - Restart the client
help                           (h)  - Show help menu
quit / exit                    (q)  - Exit
```

### Quick Examples
```bash
# Send a message to a contact
> s alice Hey, how are you?

# Send using contact number
> s 3 Quick message to contact #3

# Reply to the last received message
> re Thanks for the info!

# View conversation with a user
> m list                    # See all conversations
> m user 5                  # View full chat with user #5

# Add a discovered peer to contacts
> p                         # List announced peers
> ap 2 Bob                  # Add peer #2 as "Bob"

# Block a spammer
> block 7                   # Block contact/peer #7
> block <hash>              # Block by hash
> blacklist                 # View all blocked addresses
> unblock alice             # Unblock contact "alice"

# Check statistics
> stats                     # View messaging stats
> status                    # View system status with security info
```

## 🎯 Key Features Explained

### Fixed Index Numbers
All contacts, peers, and conversations have **permanent index numbers** that never change. This prevents accidentally sending messages to the wrong person when new peers are discovered or messages are received.

### Peer Discovery
The client automatically discovers and lists LXMF peers that announce themselves on the network. You can:
- View discovered peers with `peers` (shows star ★ for contacts)
- Send messages directly using `sendpeer <#>`
- Add them to contacts with `addpeer <#>`
- Display names are automatically cached from announces

### Message Threading
View complete conversation history with any user:
```bash
> m list              # See all people you've messaged
> m user 3            # View full conversation with user #3
> re Hey there!       # Reply directly (target is auto-set)
```

### Stamp Cost Protection
Prevent spam by requiring senders to perform computational work:
```bash
> settings            # Open settings menu
> [7]                 # Enable stamp cost
> Enter cost: 8       # Set to 8 bits (medium protection)
```

Recommended values:
- **1-5 bits**: Low protection (fast, allows weaker devices)
- **6-15 bits**: Medium protection (balanced)
- **16-32 bits**: High protection (may be slow for some senders)

When stamp cost is enabled:
- Your requirement is announced to the network
- Other LXMF clients will see your stamp cost
- Messages without sufficient stamps are rejected
- Option to ignore/allow messages with invalid stamps

### Blacklist System
Completely block unwanted senders:
```bash
> block 5                      # Block contact #5
> block spammer                # Block by contact name
> block <hash>                 # Block by destination hash
> blacklist                    # View all blocked addresses
> unblock bob                  # Remove from blacklist
> blacklist clear              # Clear entire blacklist (with confirmation)
```

Blocked messages are:
- Silently dropped (no notification)
- Not saved to message history
- Logged to console for awareness

### Smart Notifications
Configure exactly how you want to be notified:
```bash
> settings            # Open settings menu
> [4]                 # Toggle sound notifications
> [5]                 # Toggle terminal bell
> [6]                 # Toggle visual flash
> [t]                 # Test your notification settings
```

Each notification type works independently:
- **Sound**: Platform-specific beeps/melodies/vibration
- **Bell**: Traditional terminal bell character
- **Visual**: Colorful flash animation

### Plugin System
Extend the client with custom functionality:

1. **Create a plugin** (place in `lxmf_client_storage/plugins/`):
```python
# echo_bot.py
class Plugin:
    def __init__(self, client):
        self.client = client
        self.commands = ['echo']  # Commands this plugin handles
        self.description = "Echo bot - auto-replies to messages"
    
    def on_message(self, message, msg_data):
        """Handle incoming messages"""
        # Auto-reply with "Echo: <message>"
        content = msg_data['content']
        reply = f"Echo: {content}"
        self.client.send_message(msg_data['source_hash'], reply)
        return True  # Return True to suppress normal notification
    
    def handle_command(self, cmd, parts):
        """Handle custom commands"""
        if cmd == 'echo':
            print("Echo bot is active!")
```

2. **Manage plugins**:
```bash
> plugin list                 # See all plugins
> plugin enable echo_bot      # Enable a plugin
> plugin disable echo_bot     # Disable without deleting
> plugin reload               # Reload all plugins
```

Plugins can:
- Add custom commands
- Process incoming messages
- Auto-respond to messages
- Implement chat bots
- Add remote control features
- Integrate with external services

## 🗂️ File Structure
```
lxmf-client/
├── lxmf-cli.py                     # Main client script
├── lxmf_client_identity            # Your identity (auto-generated)
└── lxmf_client_storage/
    ├── messages/                   # Individual message files
    ├── contacts.json               # Your contacts
    ├── config.json                 # Client configuration
    ├── display_names.json          # Cached display names
    ├── conversations.json          # Conversation indices
    ├── blacklist.json              # Blocked addresses
    ├── plugins/                    # Plugin directory
    │   ├── echo_bot.py            # Example plugin
    │   └── ...                    # Your custom plugins
    ├── plugins_config.json         # Plugin enable/disable state
    └── lxmf_router/               # LXMF router data
```

## ⚙️ Configuration

### Settings Menu
Access with `settings` command:
```
General Settings:
  [1] Display Name
  [2] Announce Interval
  [3] Discovery Alerts

Notification Settings:
  [4] Sound (beeps/melody)
  [5] Terminal Bell
  [6] Visual Flash

Security Settings:
  [7] Stamp Cost (enable/disable & set amount)
  [8] Ignore Invalid Stamps (reject or allow)

Options:
  [t] - Test notification
  [b] - Back to main menu
  [s] - Save and exit
```

### Manual Configuration
Edit `lxmf_client_storage/config.json`:
```json
{
  "display_name": "Your Name",
  "announce_interval": 300,
  "show_announces": true,
  "notify_sound": true,
  "notify_bell": true,
  "notify_visual": true,
  "stamp_cost_enabled": false,
  "stamp_cost": 0,
  "ignore_invalid_stamps": true
}
```

## 🔧 Troubleshooting

### No messages being received
- Ensure Reticulum is properly configured with at least one interface
- Check that your announce interval isn't too long
- Manually announce with `announce` command
- Check if sender is blocked: `blacklist list`

### Can't find a peer
- Ask them to announce: they should run `announce` in their client
- Check if they're using the same Reticulum network/interfaces
- Try `peers` to see if they appear in discovered peers
- Wait for their announce interval to pass

### Messages rejected due to stamps
- Check your stamp cost: `status`
- Ask the sender what their LXMF client supports
- Consider lowering stamp cost or disabling it temporarily
- Toggle "Ignore Invalid Stamps" to OFF to accept all messages

### Notifications not working (Termux)
- Install termux-api: `pkg install termux-api`
- Install Termux:API app from F-Droid or Play Store
- Grant notification and vibration permissions to Termux
- Test with `settings` → `[t]` to test notification

### Colors not showing
- Ensure your terminal supports ANSI colors
- colorama should handle most cases automatically
- On Windows, use Windows Terminal or a modern terminal emulator

### Plugins not loading
- Check plugin syntax (must have a `Plugin` class)
- View errors at startup or use `plugin reload`
- Ensure plugin file is in `lxmf_client_storage/plugins/`
- Check that plugin is enabled: `plugin list`

### UI wrapping on mobile
- The client automatically adapts to screen width
- Use landscape mode for wider tables
- Vertical layouts activate automatically on narrow screens

## 🔒 Security & Privacy

- **End-to-end encryption**: All messages are encrypted by Reticulum/LXMF
- **No central server**: Peer-to-peer mesh networking
- **Spam protection**: Stamp cost requires computational work from senders
- **Blacklist**: Complete blocking of unwanted contacts
- **Local storage**: All data stored locally on your device
- **Identity security**: Your identity file should be kept secure and backed up

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

Areas for contribution:
- Additional plugins
- Platform-specific improvements
- UI enhancements
- Documentation
- Testing on different platforms

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mark Qvist](https://github.com/markqvist) for creating [Reticulum](https://reticulum.network/) and [LXMF](https://github.com/markqvist/lxmf)
- The Reticulum community for inspiration and support
- All contributors to this project

## 🔗 Related Projects

- [Reticulum Network Stack](https://github.com/markqvist/Reticulum) - The underlying mesh networking protocol
- [LXMF](https://github.com/markqvist/lxmf) - Low Bandwidth Message Format
- [NomadNet](https://github.com/markqvist/NomadNet) - Resilient mesh communication
- [Sideband](https://github.com/markqvist/Sideband) - LXMF client for Android and Linux
- [MeshChat](https://github.com/liamcottle/meshtastic-reticulum-bridge) - Web-based LXMF client

## 📧 Contact

For questions, issues, or suggestions:
- Open an [issue](https://github.com/fr33n0w/lxmf-cli/issues)
- Reach out on LXMF at: `<0d051f3b6f844380c3e0c5d14e37fac8>`

---

**Note**: This client requires a working Reticulum installation and configuration. Please refer to the [Reticulum documentation](https://markqvist.github.io/Reticulum/manual/) for network setup.

## 📊 Comparison with Other Clients

| Feature | LXMF-CLI | NomadNet | Sideband | MeshChat |
|---------|----------|----------|----------|----------|
| Terminal UI | ✅ | ✅ | ❌ | ❌ |
| GUI | ❌ | ❌ | ✅ | ✅ |
| Contact Management | ✅ | ✅ | ✅ | ✅ |
| Message History | ✅ | ✅ | ✅ | ✅ |
| Peer Discovery | ✅ | ✅ | ✅ | ✅ |
| Stamp Cost | ✅ | ❌ | ✅ | ✅ |
| Blacklist | ✅ | ❌ | ❌ | ❌ |
| Plugin System | ✅ | ❌ | ❌ | ❌ |
| Mobile (Termux) | ✅ | ✅ | ✅ | ❌ |
| Custom Notifications | ✅ | ❌ | ✅ | ✅ |
| Cross-Platform | ✅ | ✅ | ⚠️  | ⚠️  |

---

**Made with ❤️ for the Reticulum community**
