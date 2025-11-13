"""
Keyword Alert Plugin for LXMF-CLI
Alert when specific keywords appear in messages
"""

class Plugin:
    def __init__(self, client):
        self.client = client
        self.commands = ['keyword', 'keywords']
        self.description = "Alert on specific keywords in messages"
        self.keywords = set()
        self.case_sensitive = False
        print("Keyword Alert loaded! Use 'keyword add <word>' to start")
    
    def on_message(self, message, msg_data):
        if msg_data['direction'] == 'outbound':
            return False
        
        content = msg_data.get('content', '')
        if not content:
            return False
        
        # Check for keywords
        check_content = content if self.case_sensitive else content.lower()
        found_keywords = []
        
        for keyword in self.keywords:
            check_keyword = keyword if self.case_sensitive else keyword.lower()
            if check_keyword in check_content:
                found_keywords.append(keyword)
        
        if found_keywords:
            sender = self.client.format_contact_display_short(msg_data['source_hash'])
            print(f"\n{'='*60}")
            print(f"🔔 KEYWORD ALERT from {sender}")
            print(f"Keywords found: {', '.join(found_keywords)}")
            
            # Show message preview
            preview = content[:100]
            if len(content) > 100:
                preview += "..."
            print(f"Message: {preview}")
            print(f"{'='*60}")
            print("> ", end="", flush=True)
            
            # Extra notification
            self.client.notify_new_message()
        
        return False
    
    def handle_command(self, cmd, parts):
        if len(parts) < 2:
            # Show current keywords
            print(f"\n{'='*60}")
            print("KEYWORD ALERTS")
            print(f"{'='*60}")
            
            if self.keywords:
                print("Active keywords:")
                for kw in sorted(self.keywords):
                    print(f"  - {kw}")
            else:
                print("No keywords set")
            
            print(f"\nCase sensitive: {'YES' if self.case_sensitive else 'NO'}")
            print("\nCommands:")
            print("  keyword add <word>       - Add keyword")
            print("  keyword remove <word>    - Remove keyword")
            print("  keyword clear            - Clear all")
            print("  keyword case on/off      - Toggle case sensitivity")
            print("  keyword list             - Show keywords")
            print(f"{'='*60}\n")
            return
        
        subcmd = parts[1].lower()
        
        if subcmd == 'add' and len(parts) >= 3:
            keyword = ' '.join(parts[2:])
            self.keywords.add(keyword)
            self.client._print_success(f"Added keyword: {keyword}")
            print(f"Total keywords: {len(self.keywords)}")
        
        elif subcmd == 'remove' and len(parts) >= 3:
            keyword = ' '.join(parts[2:])
            if keyword in self.keywords:
                self.keywords.remove(keyword)
                self.client._print_success(f"Removed keyword: {keyword}")
            else:
                self.client._print_error("Keyword not found")
        
        elif subcmd == 'clear':
            count = len(self.keywords)
            self.keywords.clear()
            self.client._print_success(f"Cleared {count} keywords")
        
        elif subcmd == 'case' and len(parts) >= 3:
            setting = parts[2].lower()
            if setting in ['on', 'true', '1', 'yes']:
                self.case_sensitive = True
                self.client._print_success("Case sensitivity ON")
            else:
                self.case_sensitive = False
                self.client._print_success("Case sensitivity OFF")
        
        elif subcmd in ['list', 'show']:
            # Same as no arguments
            self.handle_command(cmd, [cmd])