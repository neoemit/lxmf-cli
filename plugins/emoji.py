"""
Emoji Sender Plugin for LXMF-CLI
Browse and send emoji/emoticons easily
"""

class Plugin:
    def __init__(self, client):
        self.client = client
        self.commands = ['emoji', 'emo', 'emoticon']
        self.description = "Browse and send emoji easily"
        
        # Curated list - only the most used/essential emojis
        self.emojis = [
            # Essential faces (10)
            ('😊', 'Happy'),
            ('😂', 'Laughing'),
            ('😍', 'Love'),
            ('😎', 'Cool'),
            ('😢', 'Sad'),
            ('😭', 'Crying'),
            ('😡', 'Angry'),
            ('😱', 'Shocked'),
            ('🤔', 'Thinking'),
            ('😴', 'Sleepy'),
            
            # Key gestures (8)
            ('👍', 'Thumbs Up'),
            ('👎', 'Thumbs Down'),
            ('👌', 'OK'),
            ('✌️', 'Peace'),
            ('🤝', 'Handshake'),
            ('👋', 'Wave'),
            ('🙏', 'Pray/Thanks'),
            ('💪', 'Strong'),
            
            # Hearts & symbols (8)
            ('❤️', 'Heart'),
            ('💔', 'Broken Heart'),
            ('💯', '100'),
            ('🔥', 'Fire'),
            ('⚡', 'Lightning'),
            ('✨', 'Sparkles'),
            ('⭐', 'Star'),
            ('💫', 'Dizzy'),
            
            # Common animals (6)
            ('🐶', 'Dog'),
            ('🐱', 'Cat'),
            ('🐻', 'Bear'),
            ('🦊', 'Fox'),
            ('🐧', 'Penguin'),
            ('🦄', 'Unicorn'),
            
            # Popular food (8)
            ('🍕', 'Pizza'),
            ('🍔', 'Burger'),
            ('🍺', 'Beer'),
            ('☕', 'Coffee'),
            ('🍰', 'Cake'),
            ('🍎', 'Apple'),
            ('🍉', 'Watermelon'),
            ('🌮', 'Taco'),
            
            # Activities (6)
            ('⚽', 'Soccer'),
            ('🏀', 'Basketball'),
            ('🎮', 'Gaming'),
            ('🎵', 'Music'),
            ('🎬', 'Movie'),
            ('📚', 'Books'),
            
            # Travel & vehicles (6)
            ('🚗', 'Car'),
            ('✈️', 'Airplane'),
            ('🚀', 'Rocket'),
            ('🏠', 'Home'),
            ('🌍', 'Earth'),
            ('🗺️', 'Map'),
            
            # Tech & objects (6)
            ('💻', 'Laptop'),
            ('📱', 'Phone'),
            ('⌚', 'Watch'),
            ('💡', 'Idea'),
            ('🔧', 'Tool'),
            ('🔋', 'Battery'),
            
            # Nature (6)
            ('🌞', 'Sun'),
            ('🌙', 'Moon'),
            ('🌈', 'Rainbow'),
            ('🌸', 'Flower'),
            ('🌲', 'Tree'),
            ('🌊', 'Wave'),
            
            # Extra useful (6)
            ('🎉', 'Party'),
            ('🎁', 'Gift'),
            ('💰', 'Money'),
            ('⏰', 'Clock'),
            ('📅', 'Calendar'),
            ('✅', 'Check'),
        ]
        
        print(f"✓ Emoji plugin loaded! {len(self.emojis)} emojis")
    
    def handle_command(self, cmd, parts):
        # Simple usage: just a number
        if len(parts) >= 2:
            # Check if first arg is a number
            try:
                emoji_idx = int(parts[1])
                
                # Check if there's a recipient
                recipient = None
                if len(parts) >= 3:
                    recipient = ' '.join(parts[2:])
                
                self._send_emoji(emoji_idx, recipient)
                return
                
            except ValueError:
                # Not a number, check for subcommands
                subcmd = parts[1].lower()
                
                if subcmd == 'search':
                    if len(parts) < 3:
                        print("\nUsage: emoji search <keyword>")
                        return
                    keyword = ' '.join(parts[2:])
                    self._search_emoji(keyword)
                    return
                
                elif subcmd == 'random':
                    recipient = None
                    if len(parts) >= 3:
                        recipient = ' '.join(parts[2:])
                    self._send_random_emoji(recipient)
                    return
        
        # Default: show all emojis
        self._show_emojis()
    
    def _show_emojis(self):
        """Show all emojis in 2 columns"""
        import shutil
        try:
            width = min(shutil.get_terminal_size().columns, 90)
        except:
            width = 90
        
        print(f"\n{'='*width}")
        print(f"😊 EMOJI PICKER ({len(self.emojis)} emojis)")
        print(f"{'='*width}\n")
        
        # Show in 2 columns
        half = (len(self.emojis) + 1) // 2
        
        for i in range(half):
            # Left column
            left_idx = i
            left_emoji, left_name = self.emojis[left_idx]
            left_str = f"[{left_idx:2d}] {left_emoji}  {left_name:<15}"
            
            # Right column (if exists)
            right_idx = i + half
            if right_idx < len(self.emojis):
                right_emoji, right_name = self.emojis[right_idx]
                right_str = f"[{right_idx:2d}] {right_emoji}  {right_name:<15}"
                print(f"{left_str}  {right_str}")
            else:
                print(left_str)
        
        print(f"\n{'='*width}")
        print(f"💡 Quick send: emo <#>")
        print(f"   Example: emo 0")
        print(f"   To someone: emo 5 alice")
        print(f"   Search: emo search love")
        print(f"   Random: emo random")
        
        print(f"\n📬 Last contact: ", end="")
        if self.client.last_sender_hash:
            print(self.client.format_contact_display_short(self.client.last_sender_hash))
        else:
            print("None (specify recipient)")
        
        print(f"{'='*width}\n")
    
    def _search_emoji(self, keyword):
        """Search for emoji by keyword"""
        keyword_lower = keyword.lower()
        results = []
        
        for i, (emoji, name) in enumerate(self.emojis):
            if keyword_lower in name.lower():
                results.append((i, emoji, name))
        
        if not results:
            print(f"\n🔍 No emojis found for: '{keyword}'\n")
            return
        
        import shutil
        try:
            width = min(shutil.get_terminal_size().columns, 90)
        except:
            width = 90
        
        print(f"\n{'='*width}")
        print(f"🔍 SEARCH: '{keyword}' ({len(results)} found)")
        print(f"{'='*width}\n")
        
        for idx, emoji, name in results:
            print(f"[{idx:2d}] {emoji}  {name}")
        
        print(f"\n{'='*width}")
        print(f"💡 Send: emo <#> [contact]")
        print(f"{'='*width}\n")
    
    def _send_emoji(self, emoji_idx, recipient=None):
        """Send an emoji"""
        # Validate index
        if emoji_idx < 0 or emoji_idx >= len(self.emojis):
            self.client._print_error(f"Invalid emoji #{emoji_idx}")
            print(f"Valid range: 0-{len(self.emojis)-1}")
            print("Use 'emo' to see the list")
            return
        
        emoji, name = self.emojis[emoji_idx]
        
        # Determine recipient
        if recipient:
            dest_hash = self.client.resolve_contact_or_hash(recipient)
            if not dest_hash:
                self.client._print_error(f"Unknown contact: {recipient}")
                return
        else:
            if not self.client.last_sender_hash:
                self.client._print_error("No recent conversation")
                print("Specify recipient: emo <#> <contact>")
                return
            dest_hash = self.client.last_sender_hash
        
        recipient_name = self.client.format_contact_display_short(dest_hash)
        
        # Send the emoji
        print(f"\n📤 {emoji} ({name}) → {recipient_name}")
        success = self.client.send_message(dest_hash, emoji)
        
        if success:
            print(f"✓ Sent!\n")
    
    def _send_random_emoji(self, recipient=None):
        """Send a random emoji"""
        import random
        emoji_idx = random.randint(0, len(self.emojis) - 1)
        emoji, name = self.emojis[emoji_idx]
        
        print(f"\n🎲 Random: {emoji} ({name})")
        self._send_emoji(emoji_idx, recipient)

if __name__ == '__main__':
    print("This is a plugin for LXMF Client")
    print("Place in: ./lxmf_client_storage/plugins/")