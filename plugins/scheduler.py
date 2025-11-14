"""
Message Scheduler Plugin for LXMF-CLI
Schedule messages to be sent at specific times
"""
import time
import threading
from datetime import datetime

class Plugin:
    def __init__(self, client):
        self.client = client
        self.commands = ['schedule', 'scheduled', 'schedule-cancel']
        self.description = "Schedule messages for later delivery"
        self.scheduled_messages = []
        self.running = True
        
        # Start scheduler thread
        self.thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.thread.start()
        print("✓ Message Scheduler loaded!")
    
    def scheduler_loop(self):
        """Background thread to check and send scheduled messages"""
        while self.running:
            try:
                current_time = time.time()
                
                # Check for messages to send
                to_send = []
                remaining = []
                
                for msg in self.scheduled_messages:
                    if msg['send_time'] <= current_time:
                        to_send.append(msg)
                    else:
                        remaining.append(msg)
                
                # Send due messages
                for msg in to_send:
                    try:
                        self.client.send_message(msg['recipient'], msg['content'])
                        print(f"\n[📅 SCHEDULER] ✓ Sent scheduled message to {msg['recipient_name']}")
                        print("> ", end="", flush=True)
                    except Exception as e:
                        print(f"\n[❌ SCHEDULER ERROR] {e}")
                        print("> ", end="", flush=True)
                
                self.scheduled_messages = remaining
                
            except Exception as e:
                print(f"\n[❌ SCHEDULER ERROR] {e}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def handle_command(self, cmd, parts):
        if cmd == 'schedule':
            # Handle the parsing issue from main client
            # parts = ['schedule', 'contact', 'minutes message...']
            # We need to split the third part further
            
            if len(parts) > 0 and parts[0] == 'schedule':
                args = parts[1:]
            else:
                args = parts
            
            # Now args might be: ['10', '2 test message!']
            # We need to split args[1] to separate minutes from message
            
            if len(args) < 2:
                print("\n📅 Message Scheduler")
                print("="*60)
                print("Usage: schedule <contact/#> <minutes> <message>")
                print("\nExamples:")
                print("  schedule alice 30 Don't forget the meeting!")
                print("  schedule 5 60 Reminder to check logs")
                print("  schedule 10 2 Test message")
                print("\nTips:")
                print("  • Use contact name or number from 'contacts' list")
                print("  • Minutes must be at least 1")
                print("  • View scheduled: 'scheduled'")
                print("="*60)
                print()
                return
            
            # Parse recipient
            recipient = args[0]
            
            # Split the remaining part to get minutes and message
            remaining = args[1].split(maxsplit=1)
            
            if len(remaining) < 2:
                print("\n📅 Message Scheduler")
                print("="*60)
                print("Usage: schedule <contact/#> <minutes> <message>")
                print("\nError: Missing message content")
                print("="*60)
                print()
                return
            
            try:
                minutes = int(remaining[0])
                if minutes < 1:
                    self.client._print_error("Minutes must be at least 1")
                    return
            except ValueError:
                self.client._print_error(f"Invalid minutes: '{remaining[0]}' (must be a number)")
                return
            
            message = remaining[1]
            
            if not message.strip():
                self.client._print_error("Message cannot be empty")
                return
            
            # Resolve recipient
            dest_hash = self.client.resolve_contact_or_hash(recipient)
            
            if not dest_hash:
                self.client._print_error(f"Cannot find contact: '{recipient}'")
                print("\n💡 Available options:")
                print("  • Use contact name: schedule alice 5 Hello")
                print("  • Use contact number: schedule 3 5 Hello")
                print("  • Use LXMF hash: schedule <hash> 5 Hello")
                print("\nTo see your contacts: 'contacts'")
                print("To see available peers: 'peers'")
                print()
                return
            
            recipient_name = self.client.format_contact_display_short(dest_hash)
            
            # Schedule the message
            send_time = time.time() + (minutes * 60)
            send_datetime = datetime.fromtimestamp(send_time)
            
            self.scheduled_messages.append({
                'recipient': dest_hash,
                'recipient_name': recipient_name,
                'content': message,
                'send_time': send_time,
                'scheduled_at': time.time()
            })
            
            print()
            self.client._print_success(f"Message scheduled to {recipient_name}")
            print(f"📅 Will send at: {send_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  In {minutes} minute{'s' if minutes != 1 else ''}")
            
            # Show preview
            preview = message[:50]
            if len(message) > 50:
                preview += "..."
            print(f"💬 Message: \"{preview}\"")
            print()
        
        elif cmd == 'scheduled':
            if not self.scheduled_messages:
                print("\n📅 No scheduled messages\n")
                return
            
            import shutil
            try:
                width = min(shutil.get_terminal_size().columns, 80)
            except:
                width = 80
            
            print(f"\n{'='*width}")
            print("📅 SCHEDULED MESSAGES")
            print(f"{'='*width}\n")
            
            # Sort by send time
            sorted_msgs = sorted(self.scheduled_messages, key=lambda x: x['send_time'])
            
            for idx, msg in enumerate(sorted_msgs, 1):
                send_datetime = datetime.fromtimestamp(msg['send_time'])
                time_until_seconds = msg['send_time'] - time.time()
                
                print(f"[{idx}] To: {msg['recipient_name']}")
                print(f"    📅 When: {send_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if time_until_seconds > 0:
                    time_until_minutes = int(time_until_seconds / 60)
                    if time_until_minutes > 60:
                        hours = time_until_minutes // 60
                        mins = time_until_minutes % 60
                        print(f"    ⏱️  In: {hours}h {mins}m")
                    else:
                        print(f"    ⏱️  In: {time_until_minutes} minute{'s' if time_until_minutes != 1 else ''}")
                else:
                    print(f"    ⚡ Status: Sending soon...")
                
                # Show message preview
                preview = msg['content'][:60]
                if len(msg['content']) > 60:
                    preview += "..."
                print(f"    💬 Message: \"{preview}\"")
                print()
            
            print(f"{'='*width}")
            print(f"\n💡 Total scheduled: {len(self.scheduled_messages)}")
            print(f"💡 Use 'schedule-cancel <#>' to cancel a message")
            print()
        
        elif cmd == 'schedule-cancel':
            # Handle args with or without command name
            if len(parts) > 0 and parts[0] == 'schedule-cancel':
                args = parts[1:]
            else:
                args = parts
            
            if len(args) < 1:
                print("\nUsage: schedule-cancel <message_#>")
                print("Use 'scheduled' to see message numbers")
                return
            
            try:
                # Might need to split if args[0] contains the number and more
                num_str = args[0].split()[0] if args[0] else ""
                msg_num = int(num_str)
                
                if msg_num < 1 or msg_num > len(self.scheduled_messages):
                    self.client._print_error(f"Invalid message number: {msg_num}")
                    return
                
                # Sort to match 'scheduled' display
                sorted_msgs = sorted(self.scheduled_messages, key=lambda x: x['send_time'])
                msg_to_cancel = sorted_msgs[msg_num - 1]
                
                # Remove from list
                self.scheduled_messages.remove(msg_to_cancel)
                
                self.client._print_success(f"Cancelled scheduled message to {msg_to_cancel['recipient_name']}")
                print()
                
            except ValueError:
                self.client._print_error("Message number must be a number")
                return

if __name__ == '__main__':
    print("This is a plugin for LXMF Client")
    print("Place in: ./lxmf_client_storage/plugins/")