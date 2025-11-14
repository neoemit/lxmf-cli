"""
System Info Plugin for LXMF Client

Get detailed system information locally or from remote nodes.
Commands:
  sysinfo              - Show local system info
  sysinfo-remote <#>   - Request sysinfo from a remote peer
  sysinfo-toggle       - Enable/disable remote sysinfo requests
  sysinfo-config       - Configure what info to share remotely
"""

import os
import time
import platform
import json
import psutil
from datetime import datetime, timedelta

class Plugin:
    def __init__(self, client):
        self.client = client
        self.description = "System information and monitoring"
        self.commands = ['sysinfo', 'sysinfo-remote', 'sysinfo-toggle', 'sysinfo-config']
        
        # Configuration
        self.config_file = os.path.join(client.storage_path, "sysinfo_config.json")
        self.remote_enabled = False
        self.client_start_time = time.time()
        
        # What info to share remotely (privacy controls)
        self.share_config = {
            'uptime': True,
            'battery': True,
            'memory': True,
            'disk': True,
            'cpu': True,
            'network': True,
            'client_stats': True,
            'system_details': False,  # Hostname, IPs, etc
        }
        
        # Statistics tracking
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'data_tracked_since': time.time()
        }
        
        self.load_config()
    
    def on_message(self, message, msg_data):
        """Handle incoming sysinfo requests"""
        content = msg_data.get('content', '')
        
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='replace')
        
        # Track statistics
        self.stats['messages_received'] += 1
        try:
            self.stats['bytes_received'] += len(str(content).encode('utf-8'))
        except:
            pass
        
        # Check if this is a sysinfo request
        if content.strip().lower() == 'sysinfo' or content.strip().lower() == 'sysinfo?':
            if self.remote_enabled:
                # Generate and send system info
                source_hash = msg_data.get('source_hash')
                
                print(f"\n[🔍 SysInfo] Request from {self.client.format_contact_display_short(source_hash)}")
                
                info = self._gather_system_info(for_remote=True)
                response = self._format_sysinfo_message(info)
                
                # Send response
                self.client.send_message(
                    source_hash,
                    response,
                    title="📊 System Information"
                )
                
                print(f"[🔍 SysInfo] Response sent")
                print("> ", end="", flush=True)
                
                return False  # Don't suppress the original request message
            else:
                # Remote requests disabled
                source_hash = msg_data.get('source_hash')
                print(f"\n[🔍 SysInfo] Request denied from {self.client.format_contact_display_short(source_hash)} (remote disabled)")
                print("> ", end="", flush=True)
                return False
        
        return False
    
    def handle_command(self, cmd, parts):
        """Handle sysinfo commands"""
        if cmd == 'sysinfo':
            if len(parts) > 1 and parts[1].lower() in ['remote', 'r']:
                # Alias for sysinfo-remote
                self._request_remote_sysinfo(parts[2:] if len(parts) > 2 else [])
            else:
                self._show_local_sysinfo()
        
        elif cmd == 'sysinfo-remote':
            self._request_remote_sysinfo(parts[1:])
        
        elif cmd == 'sysinfo-toggle':
            self._toggle_remote()
        
        elif cmd == 'sysinfo-config':
            self._configure_sharing()
    
    def _show_local_sysinfo(self):
        """Show detailed local system information"""
        info = self._gather_system_info(for_remote=False)
        
        import shutil
        try:
            width = min(shutil.get_terminal_size().columns, 80)
        except:
            width = 80
        
        print(f"\n{'='*width}")
        print("📊 SYSTEM INFORMATION")
        print(f"{'='*width}")
        
        # System Details
        print(f"\n🖥️  System")
        print(f"   Platform: {info['system']['platform']}")
        print(f"   OS: {info['system']['os']}")
        print(f"   Architecture: {info['system']['architecture']}")
        print(f"   Hostname: {info['system']['hostname']}")
        print(f"   Python: {info['system']['python_version']}")
        
        # Uptime
        print(f"\n⏱️  Uptime")
        print(f"   System: {info['uptime']['system_uptime']}")
        print(f"   Client: {info['uptime']['client_uptime']}")
        
        # CPU
        print(f"\n🔧 CPU")
        print(f"   Cores: {info['cpu']['cores']} ({info['cpu']['physical_cores']} physical)")
        print(f"   Usage: {info['cpu']['usage']:.1f}%")
        print(f"   Frequency: {info['cpu']['frequency']:.0f} MHz")
        
        # Memory
        print(f"\n💾 Memory")
        print(f"   Total: {self._format_bytes(info['memory']['total'])}")
        print(f"   Available: {self._format_bytes(info['memory']['available'])}")
        print(f"   Used: {self._format_bytes(info['memory']['used'])} ({info['memory']['percent']:.1f}%)")
        
        # Disk
        print(f"\n💿 Disk")
        print(f"   Total: {self._format_bytes(info['disk']['total'])}")
        print(f"   Free: {self._format_bytes(info['disk']['free'])}")
        print(f"   Used: {self._format_bytes(info['disk']['used'])} ({info['disk']['percent']:.1f}%)")
        
        # Battery (if available)
        if info['battery']['present']:
            print(f"\n🔋 Battery")
            print(f"   Level: {info['battery']['percent']:.1f}%")
            print(f"   Status: {info['battery']['status']}")
            if info['battery']['time_left']:
                print(f"   Time Left: {info['battery']['time_left']}")
            print(f"   Plugged: {info['battery']['plugged']}")
        
        # Network
        if info['network']['interfaces']:
            print(f"\n🌐 Network")
            print(f"   Sent: {self._format_bytes(info['network']['bytes_sent'])}")
            print(f"   Received: {self._format_bytes(info['network']['bytes_recv'])}")
            if info['network']['ip_addresses']:
                print(f"   IPs: {', '.join(info['network']['ip_addresses'][:3])}")
        
        # Client Statistics
        print(f"\n📨 LXMF Client Stats")
        print(f"   Messages Sent: {sum(1 for m in self.client.messages if m.get('direction') == 'outbound')}")
        print(f"   Messages Received: {sum(1 for m in self.client.messages if m.get('direction') == 'inbound')}")
        print(f"   Total Messages: {len(self.client.messages)}")
        print(f"   Contacts: {len(self.client.contacts)}")
        print(f"   Announced Peers: {len(self.client.announced_peers)}")
        
        # Plugin data usage tracking
        tracked_time = time.time() - self.stats['data_tracked_since']
        if tracked_time > 60:
            print(f"\n📊 Data Usage (Plugin Tracking)")
            print(f"   Tracked for: {self._format_duration(tracked_time)}")
            print(f"   Messages: ↑{self.stats['messages_sent']} ↓{self.stats['messages_received']}")
            print(f"   Data: ↑{self._format_bytes(self.stats['bytes_sent'])} ↓{self._format_bytes(self.stats['bytes_received'])}")
        
        # Termux specific info
        if os.path.exists('/data/data/com.termux'):
            print(f"\n📱 Termux Environment")
            print(f"   Detected: Yes")
            print(f"   Prefix: {os.environ.get('PREFIX', 'N/A')}")
        
        print(f"\n{'='*width}")
        
        # Remote status
        status_icon = "✅" if self.remote_enabled else "❌"
        status_text = "ENABLED" if self.remote_enabled else "DISABLED"
        
        print(f"\n🌐 Remote SysInfo: {status_icon} {status_text}")
        print(f"   Use 'sysinfo-toggle' to change")
        print()
    
    def _request_remote_sysinfo(self, parts):
        """Request sysinfo from a remote peer"""
        if not parts:
            print("\nUsage: sysinfo-remote <contact_#/name>")
            print("Example: sysinfo-remote 1")
            return
        
        target = ' '.join(parts)
        dest_hash = self.client.resolve_contact_or_hash(target)
        
        if not dest_hash:
            self.client._print_error(f"Unknown contact: {target}")
            return
        
        recipient_display = self.client.format_contact_display_short(dest_hash)
        
        print(f"\n🔍 Requesting system info from {recipient_display}...")
        
        # Send request
        success = self.client.send_message(
            dest_hash,
            "sysinfo",
            title="🔍 System Info Request"
        )
        
        if success:
            self.client._print_success("Request sent")
            print("   Waiting for response...")
            print("   (Response will appear as a new message)\n")
        else:
            self.client._print_error("Failed to send request")
    
    def _toggle_remote(self):
        """Toggle remote sysinfo requests"""
        self.remote_enabled = not self.remote_enabled
        self.save_config()
        
        status_icon = "✅" if self.remote_enabled else "❌"
        status = "ENABLED" if self.remote_enabled else "DISABLED"
        
        print(f"\n{status_icon} Remote SysInfo: {status}")
        
        if self.remote_enabled:
            print("   Remote peers can now request your system info")
            print("   Use 'sysinfo-config' to control what is shared")
        else:
            print("   Remote requests will be denied")
        print()
    
    def _configure_sharing(self):
        """Configure what information to share remotely"""
        print("\n📊 SysInfo Sharing Configuration")
        print("="*60)
        print("\nChoose what information to share with remote peers:")
        print()
        
        options = [
            ('uptime', 'System and client uptime'),
            ('battery', 'Battery status and level'),
            ('memory', 'RAM usage statistics'),
            ('disk', 'Disk space usage'),
            ('cpu', 'CPU usage and specs'),
            ('network', 'Network data statistics'),
            ('client_stats', 'LXMF message statistics'),
            ('system_details', 'Hostname, IP addresses (privacy concern)'),
        ]
        
        for idx, (key, description) in enumerate(options, 1):
            status_icon = "✅" if self.share_config[key] else "❌"
            print(f"  [{idx}] {status_icon} {description}")
        
        print("\n" + "="*60)
        print("\nCommands:")
        print("  [1-8] - Toggle setting")
        print("  [all] - Enable all")
        print("  [none] - Disable all (only uptime)")
        print("  [q] - Save and exit")
        
        while True:
            choice = input("\nSelect option: ").strip().lower()
            
            if choice == 'q':
                self.save_config()
                self.client._print_success("Configuration saved")
                break
            elif choice == 'all':
                for key in self.share_config:
                    self.share_config[key] = True
                print("✅ All options enabled")
            elif choice == 'none':
                for key in self.share_config:
                    self.share_config[key] = False
                self.share_config['uptime'] = True  # Always share uptime
                print("✅ All options disabled (except uptime)")
            elif choice.isdigit() and 1 <= int(choice) <= len(options):
                idx = int(choice) - 1
                key = options[idx][0]
                self.share_config[key] = not self.share_config[key]
                status = "enabled" if self.share_config[key] else "disabled"
                status_icon = "✅" if self.share_config[key] else "❌"
                print(f"   {status_icon} {options[idx][1]}: {status}")
            else:
                print("❌ Invalid option")
            
            # Show updated status
            print()
            for idx, (key, description) in enumerate(options, 1):
                status_icon = "✅" if self.share_config[key] else "❌"
                print(f"  [{idx}] {status_icon} {description}")
    
    def _gather_system_info(self, for_remote=False):
        """Gather system information"""
        info = {}
        
        # Always include uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        client_uptime_seconds = time.time() - self.client_start_time
        
        info['uptime'] = {
            'system_uptime': self._format_duration(uptime_seconds),
            'client_uptime': self._format_duration(client_uptime_seconds),
            'system_uptime_seconds': int(uptime_seconds),
            'client_uptime_seconds': int(client_uptime_seconds)
        }
        
        # System details (only if not remote or if allowed)
        if not for_remote or self.share_config['system_details']:
            info['system'] = {
                'platform': platform.system(),
                'os': platform.platform(),
                'architecture': platform.machine(),
                'hostname': platform.node(),
                'python_version': platform.python_version()
            }
        else:
            info['system'] = {
                'platform': platform.system(),
                'os': 'Hidden',
                'architecture': platform.machine(),
                'hostname': 'Hidden',
                'python_version': platform.python_version()
            }
        
        # CPU (if allowed)
        if not for_remote or self.share_config['cpu']:
            cpu_freq = psutil.cpu_freq()
            info['cpu'] = {
                'cores': psutil.cpu_count(),
                'physical_cores': psutil.cpu_count(logical=False),
                'usage': psutil.cpu_percent(interval=0.1),
                'frequency': cpu_freq.current if cpu_freq else 0
            }
        
        # Memory (if allowed)
        if not for_remote or self.share_config['memory']:
            mem = psutil.virtual_memory()
            info['memory'] = {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'percent': mem.percent
            }
        
        # Disk (if allowed)
        if not for_remote or self.share_config['disk']:
            disk = psutil.disk_usage('/')
            info['disk'] = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        
        # Battery (if allowed and available)
        if not for_remote or self.share_config['battery']:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    time_left = None
                    if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft > 0:
                        time_left = self._format_duration(battery.secsleft)
                    
                    info['battery'] = {
                        'present': True,
                        'percent': battery.percent,
                        'plugged': battery.power_plugged,
                        'status': 'Charging' if battery.power_plugged else 'Discharging',
                        'time_left': time_left
                    }
                else:
                    info['battery'] = {'present': False}
            except:
                info['battery'] = {'present': False}
        else:
            info['battery'] = {'present': False}
        
        # Network (if allowed)
        if not for_remote or self.share_config['network']:
            net_io = psutil.net_io_counters()
            
            # Get IP addresses
            ip_addresses = []
            if not for_remote or self.share_config['system_details']:
                try:
                    import socket
                    hostname = socket.gethostname()
                    ip_addresses = [socket.gethostbyname(hostname)]
                except:
                    pass
            
            info['network'] = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'interfaces': True,
                'ip_addresses': ip_addresses
            }
        
        # Client stats (if allowed)
        if not for_remote or self.share_config['client_stats']:
            info['client_stats'] = {
                'messages_sent': sum(1 for m in self.client.messages if m.get('direction') == 'outbound'),
                'messages_received': sum(1 for m in self.client.messages if m.get('direction') == 'inbound'),
                'total_messages': len(self.client.messages),
                'contacts': len(self.client.contacts),
                'peers': len(self.client.announced_peers)
            }
        
        return info
    
    def _format_sysinfo_message(self, info):
        """Format system info as a message"""
        msg = "╔══════════════════════════════════╗\n"
        msg += "║     SYSTEM INFORMATION           ║\n"
        msg += "╚══════════════════════════════════╝\n\n"
        
        # Uptime
        msg += f"⏱️  UPTIME\n"
        msg += f"System: {info['uptime']['system_uptime']}\n"
        msg += f"Client: {info['uptime']['client_uptime']}\n\n"
        
        # CPU
        if 'cpu' in info:
            msg += f"🔧 CPU\n"
            msg += f"Cores: {info['cpu']['cores']}\n"
            msg += f"Usage: {info['cpu']['usage']:.1f}%\n\n"
        
        # Memory
        if 'memory' in info:
            msg += f"💾 MEMORY\n"
            msg += f"Total: {self._format_bytes(info['memory']['total'])}\n"
            msg += f"Used: {self._format_bytes(info['memory']['used'])} ({info['memory']['percent']:.1f}%)\n"
            msg += f"Free: {self._format_bytes(info['memory']['available'])}\n\n"
        
        # Disk
        if 'disk' in info:
            msg += f"💿 DISK\n"
            msg += f"Total: {self._format_bytes(info['disk']['total'])}\n"
            msg += f"Used: {self._format_bytes(info['disk']['used'])} ({info['disk']['percent']:.1f}%)\n"
            msg += f"Free: {self._format_bytes(info['disk']['free'])}\n\n"
        
        # Battery
        if 'battery' in info and info['battery']['present']:
            msg += f"🔋 BATTERY\n"
            msg += f"Level: {info['battery']['percent']:.1f}%\n"
            msg += f"Status: {info['battery']['status']}\n"
            if info['battery']['time_left']:
                msg += f"Time Left: {info['battery']['time_left']}\n"
            msg += "\n"
        
        # Network
        if 'network' in info:
            msg += f"🌐 NETWORK\n"
            msg += f"Sent: {self._format_bytes(info['network']['bytes_sent'])}\n"
            msg += f"Received: {self._format_bytes(info['network']['bytes_recv'])}\n\n"
        
        # Client stats
        if 'client_stats' in info:
            msg += f"📨 LXMF STATS\n"
            msg += f"Messages: ↑{info['client_stats']['messages_sent']} ↓{info['client_stats']['messages_received']}\n"
            msg += f"Contacts: {info['client_stats']['contacts']}\n"
            msg += f"Peers: {info['client_stats']['peers']}\n\n"
        
        msg += "────────────────────────────────────\n"
        msg += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return msg
    
    def _format_bytes(self, bytes_value):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def _format_duration(self, seconds):
        """Format duration to human readable"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return ' '.join(parts)
    
    def load_config(self):
        """Load configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.remote_enabled = config.get('remote_enabled', False)
                    self.share_config.update(config.get('share_config', {}))
                    self.stats = config.get('stats', self.stats)
            except Exception as e:
                print(f"Error loading sysinfo config: {e}")
    
    def save_config(self):
        """Save configuration"""
        try:
            config = {
                'remote_enabled': self.remote_enabled,
                'share_config': self.share_config,
                'stats': self.stats
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving sysinfo config: {e}")

if __name__ == '__main__':
    print("This is a plugin for LXMF Client")
    print("Place in: ./lxmf_client_storage/plugins/")