"""
Share Contact Plugin for LXMF Client

Allows sharing and importing contact information.
Commands:
  share <contact_#> <recipient_#> - Share a contact with someone
  import [message_#]              - Import contact from last message or specific message
"""

import re
import json

class Plugin:
    def __init__(self, client):
        self.client = client
        self.description = "Share and import contacts"
        self.commands = ['share', 'sharecontact', 'import', 'importcontact']
        
        # Pattern to detect contact cards in messages
        self.contact_card_pattern = re.compile(
            r'Name:\s*(.+?)\n.*?LXMF Address:\s*\n([a-fA-F0-9]+)',
            re.DOTALL
        )
    
    def on_message(self, message, msg_data):
        """Check if incoming message contains a contact card"""
        content = msg_data.get('content', '')
        
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='replace')
        
        # Check if this looks like a contact card
        if '╔══════════════════════════════════╗' in content and 'CONTACT CARD' in content:
            # Mark message as containing a contact card (for future reference)
            msg_data['has_contact_card'] = True
            
            # Extract contact info
            match = self.contact_card_pattern.search(content)
            if match:
                name = match.group(1).strip()
                address = match.group(2).strip()
                
                # Also try to extract display name
                display_name = None
                display_match = re.search(r'Display Name:\s*(.+?)\n', content)
                if display_match:
                    display_name = display_match.group(1).strip()
                
                # Show import hint
                print(f"\n💡 This message contains a contact card for: {name}")
                if display_name and display_name != name:
                    print(f"   Display Name: {display_name}")
                print(f"   Type 'import' to add this contact")
        
        return False  # Don't suppress the message
    
    def handle_command(self, cmd, parts):
        """Handle share and import commands"""
        if cmd in ['share', 'sharecontact']:
            self._handle_share(parts)
        elif cmd in ['import', 'importcontact']:
            self._handle_import(parts)
    
    def _handle_share(self, parts):
        """Handle share command"""
        if len(parts) < 3:
            self._show_share_usage()
            return
        
        try:
            contact_idx = int(parts[1])
            recipient_idx = int(parts[2])
            
            # Find the contact to share
            contact_to_share = None
            contact_name = None
            
            for name, data in self.client.contacts.items():
                if data.get('index') == contact_idx:
                    contact_to_share = data
                    contact_name = name
                    break
            
            if not contact_to_share:
                self.client._print_error(f"No contact with index #{contact_idx}")
                print("Use 'contacts' to see the list")
                return
            
            # Get display name for the contact (if available)
            contact_hash = contact_to_share['hash']
            display_name = self.client.get_lxmf_display_name(contact_hash)
            
            # Format the contact card message
            message = self._format_contact_card(contact_name, contact_hash, display_name)
            
            # Resolve recipient
            recipient = self.client.resolve_contact_or_hash(str(recipient_idx))
            
            if not recipient:
                self.client._print_error(f"Invalid recipient #{recipient_idx}")
                print("Use 'contacts' or 'peers' to see available recipients")
                return
            
            # Get recipient display for confirmation
            recipient_display = self.client.format_contact_display_short(recipient)
            
            # Confirm before sending
            print(f"\n📇 Sharing contact:")
            print(f"   Contact: {contact_name}")
            if display_name:
                print(f"   Display name: {display_name}")
            print(f"   Address: {contact_hash[:16]}...{contact_hash[-8:]}")
            print(f"\n📤 To: {recipient_display}")
            
            confirm = input("\nSend? [Y/n]: ").strip().lower()
            
            if confirm in ['', 'y', 'yes']:
                # Send the message
                title = f"📇 Contact: {contact_name}"
                success = self.client.send_message(recipient, message, title=title)
                
                if success:
                    self.client._print_success(f"Contact card sent to {recipient_display}")
            else:
                print("Cancelled")
                
        except ValueError:
            self.client._print_error("Contact and recipient must be valid numbers")
            self._show_share_usage()
        except Exception as e:
            self.client._print_error(f"Error sharing contact: {e}")
    
    def _handle_import(self, parts):
        """Handle import command"""
        try:
            # Determine which message to import from
            target_message = None
            
            if len(parts) >= 2:
                # Import from specific message number
                try:
                    msg_idx = int(parts[1]) - 1
                    with self.client.messages_lock:
                        if 0 <= msg_idx < len(self.client.messages):
                            target_message = self.client.messages[msg_idx]
                        else:
                            self.client._print_error(f"Invalid message number. Use 'messages' to see list")
                            return
                except ValueError:
                    self.client._print_error("Message number must be a valid number")
                    return
            else:
                # Import from last received message
                with self.client.messages_lock:
                    for msg in reversed(self.client.messages):
                        if msg['direction'] == 'inbound':
                            target_message = msg
                            break
                
                if not target_message:
                    self.client._print_error("No received messages found")
                    print("Usage: import [message_#]")
                    return
            
            # Extract contact info from message
            content = target_message.get('content', '')
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            
            # Try to parse contact card
            match = self.contact_card_pattern.search(content)
            
            if not match:
                self.client._print_error("No contact card found in this message")
                print("The message must contain a contact card to import")
                return
            
            name = match.group(1).strip()
            address = match.group(2).strip()
            
            # Try to extract display name
            display_name = None
            display_match = re.search(r'Display Name:\s*(.+?)\n', content)
            if display_match:
                display_name = display_match.group(1).strip()
            
            # Check if contact already exists
            clean_address = address.replace(":", "").replace(" ", "").lower()
            existing_contact = None
            
            for contact_name, contact_data in self.client.contacts.items():
                if contact_data['hash'].replace(":", "").replace(" ", "").lower() == clean_address:
                    existing_contact = contact_name
                    break
            
            if existing_contact:
                self.client._print_warning(f"Contact already exists as: {existing_contact}")
                overwrite = input("Overwrite? [y/N]: ").strip().lower()
                if overwrite != 'y':
                    print("Import cancelled")
                    return
                # Remove old contact
                del self.client.contacts[existing_contact]
            
            # Show preview
            print(f"\n📇 Importing contact:")
            print(f"   Name: {name}")
            if display_name and display_name != name:
                print(f"   Display Name: {display_name}")
            print(f"   Address: {address[:16]}...{address[-8:]}")
            
            # Option to customize name
            custom_name = input(f"\nCustom name (press Enter to use '{name}'): ").strip()
            if custom_name:
                name = custom_name
            
            # Confirm import
            confirm = input("\nImport this contact? [Y/n]: ").strip().lower()
            
            if confirm in ['', 'y', 'yes']:
                # Add the contact
                self.client.add_contact(name, address)
                
                # Cache display name if we have it
                if display_name:
                    self.client.cache_display_name(address, display_name)
                
                self.client._print_success(f"Contact imported: {name}")
                if display_name and display_name != name:
                    print(f"   Display Name: {display_name}")
            else:
                print("Import cancelled")
                
        except Exception as e:
            self.client._print_error(f"Error importing contact: {e}")
            import traceback
            traceback.print_exc()
    
    def _format_contact_card(self, name, hash_str, display_name=None):
        """Format a contact card message"""
        # Clean format for easy copy-paste
        card = f"""╔══════════════════════════════════╗
║        CONTACT CARD              ║
╚══════════════════════════════════╝

Name: {name}"""
        
        if display_name and display_name != name:
            card += f"\nDisplay Name: {display_name}"
        
        card += f"""

LXMF Address:
{hash_str}

────────────────────────────────────
To add this contact, use:
add {name} {hash_str}

Or type 'import' to add automatically
────────────────────────────────────"""
        
        return card
    
    def _show_share_usage(self):
        """Show share usage information"""
        print("\n📇 Share Contact")
        print("─" * 50)
        print("Usage: share <contact_#> <recipient_#>")
        print("\nExamples:")
        print("  share 1 10   - Share contact #1 with recipient #10")
        print("  share 5 2    - Share contact #5 with contact #2")
        print("\nTips:")
        print("  • Use 'contacts' to see contact numbers")
        print("  • Use 'peers' to see peer numbers")
        print()

if __name__ == '__main__':
    print("This is a plugin for LXMF Client")
    print("Place in: ./lxmf_client_storage/plugins/")