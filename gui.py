import customtkinter as ctk
import json
import threading
import subprocess
import sys
import os
from tkinter import messagebox

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class DiscordBotGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Discord Self-Bot Configuration")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Bot process
        self.bot_process = None
        self.bot_running = False
        
        # Load configuration
        self.config = self.load_config()
        
        # Create GUI
        self.create_widgets()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config
            default_config = {
                "token": "",
                "keywords": {
                    "hello": "Hi there! How can I help you?",
                    "help": "I'm here to assist you!",
                    "test": "This is an automated response!"
                },
                "case_sensitive": False,
                "respond_to_self": False,
                "reply_to_message": True,
                "role_mentions": {}
            }
            with open('config.json', 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
    
    def save_config(self):
        """Save configuration to config.json"""
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            return False
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Discord Self-Bot Configuration", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(20, 30))
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuration tab
        self.create_config_tab()
        
        # Keywords tab
        self.create_keywords_tab()
        
        # Role Mentions tab
        self.create_role_mentions_tab()
        
        # Bot Control tab
        self.create_control_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_config_tab(self):
        """Create configuration tab"""
        config_tab = self.notebook.add("Configuration")
        
        # Token section
        token_frame = ctk.CTkFrame(config_tab)
        token_frame.pack(fill="x", padx=20, pady=20)
        
        token_label = ctk.CTkLabel(token_frame, text="Discord Token", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        token_label.pack(pady=(20, 10))
        
        self.token_entry = ctk.CTkEntry(token_frame, placeholder_text="Enter your Discord token...", 
                                      width=400, show="*")
        self.token_entry.pack(pady=10)
        self.token_entry.insert(0, self.config.get("token", ""))
        
        # Show/Hide token button
        self.show_token_var = ctk.BooleanVar()
        show_token_check = ctk.CTkCheckBox(token_frame, text="Show token", 
                                          variable=self.show_token_var,
                                          command=self.toggle_token_visibility)
        show_token_check.pack(pady=5)
        
        # Settings section
        settings_frame = ctk.CTkFrame(config_tab)
        settings_frame.pack(fill="x", padx=20, pady=20)
        
        settings_label = ctk.CTkLabel(settings_frame, text="Bot Settings", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
        settings_label.pack(pady=(20, 10))
        
        # Case sensitive
        self.case_sensitive_var = ctk.BooleanVar(value=self.config.get("case_sensitive", False))
        case_check = ctk.CTkCheckBox(settings_frame, text="Case sensitive matching", 
                                   variable=self.case_sensitive_var)
        case_check.pack(pady=5, anchor="w")
        
        # Respond to self
        self.respond_self_var = ctk.BooleanVar(value=self.config.get("respond_to_self", False))
        self_check = ctk.CTkCheckBox(settings_frame, text="Respond to own messages", 
                                   variable=self.respond_self_var)
        self_check.pack(pady=5, anchor="w")
        
        # Reply to message
        self.reply_message_var = ctk.BooleanVar(value=self.config.get("reply_to_message", True))
        reply_check = ctk.CTkCheckBox(settings_frame, text="Reply to original message", 
                                    variable=self.reply_message_var)
        reply_check.pack(pady=5, anchor="w")
        
        # Save button
        save_button = ctk.CTkButton(config_tab, text="Save Configuration", 
                                  command=self.save_configuration,
                                  height=40, font=ctk.CTkFont(size=14, weight="bold"))
        save_button.pack(pady=30)
    
    def create_keywords_tab(self):
        """Create keywords management tab"""
        keywords_tab = self.notebook.add("Keywords")
        
        # Add keyword section
        add_frame = ctk.CTkFrame(keywords_tab)
        add_frame.pack(fill="x", padx=20, pady=20)
        
        add_label = ctk.CTkLabel(add_frame, text="Add New Keyword", 
                               font=ctk.CTkFont(size=16, weight="bold"))
        add_label.pack(pady=(20, 10))
        
        # Keyword input
        keyword_frame = ctk.CTkFrame(add_frame)
        keyword_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(keyword_frame, text="Keyword:").pack(side="left", padx=10)
        self.new_keyword_entry = ctk.CTkEntry(keyword_frame, placeholder_text="Enter keyword...")
        self.new_keyword_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Response input
        response_frame = ctk.CTkFrame(add_frame)
        response_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(response_frame, text="Response:").pack(side="left", padx=10)
        self.new_response_entry = ctk.CTkEntry(response_frame, placeholder_text="Enter response...")
        self.new_response_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Add button
        add_button = ctk.CTkButton(add_frame, text="Add Keyword", 
                                 command=self.add_keyword)
        add_button.pack(pady=10)
        
        # Keywords list
        list_frame = ctk.CTkFrame(keywords_tab)
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        list_label = ctk.CTkLabel(list_frame, text="Current Keywords", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        list_label.pack(pady=(20, 10))
        
        # Keywords listbox with scrollbar
        self.keywords_listbox = ctk.CTkScrollableFrame(list_frame, height=300)
        self.keywords_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_keywords_list()
    
    def create_role_mentions_tab(self):
        """Create role mentions management tab"""
        role_tab = self.notebook.add("Role Mentions")
        
        # Info section
        info_frame = ctk.CTkFrame(role_tab)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        info_label = ctk.CTkLabel(info_frame, text="Role Mention Detection", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        info_label.pack(pady=(20, 10))
        
        info_text = ctk.CTkLabel(info_frame, 
                               text="The bot will respond when specific roles are mentioned in messages.\nTo get a role ID: Right-click the role → Copy ID (requires Developer Mode)",
                               font=ctk.CTkFont(size=12))
        info_text.pack(pady=10)
        
        # Add role mention section
        add_frame = ctk.CTkFrame(role_tab)
        add_frame.pack(fill="x", padx=20, pady=20)
        
        add_label = ctk.CTkLabel(add_frame, text="Add New Role Mention", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        add_label.pack(pady=(20, 10))
        
        # Role ID input
        role_id_frame = ctk.CTkFrame(add_frame)
        role_id_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(role_id_frame, text="Role ID:").pack(side="left", padx=10)
        self.new_role_id_entry = ctk.CTkEntry(role_id_frame, placeholder_text="Enter role ID...")
        self.new_role_id_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Response input
        role_response_frame = ctk.CTkFrame(add_frame)
        role_response_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(role_response_frame, text="Response:").pack(side="left", padx=10)
        self.new_role_response_entry = ctk.CTkEntry(role_response_frame, placeholder_text="Enter response...")
        self.new_role_response_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Add button
        add_role_button = ctk.CTkButton(add_frame, text="Add Role Mention", 
                                      command=self.add_role_mention)
        add_role_button.pack(pady=10)
        
        # Role mentions list
        role_list_frame = ctk.CTkFrame(role_tab)
        role_list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        role_list_label = ctk.CTkLabel(role_list_frame, text="Current Role Mentions", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        role_list_label.pack(pady=(20, 10))
        
        # Role mentions listbox with scrollbar
        self.role_mentions_listbox = ctk.CTkScrollableFrame(role_list_frame, height=300)
        self.role_mentions_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_role_mentions_list()
    
    def create_control_tab(self):
        """Create bot control tab"""
        control_tab = self.notebook.add("Bot Control")
        
        # Status section
        status_frame = ctk.CTkFrame(control_tab)
        status_frame.pack(fill="x", padx=20, pady=20)
        
        status_label = ctk.CTkLabel(status_frame, text="Bot Status", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        status_label.pack(pady=(20, 10))
        
        self.status_label = ctk.CTkLabel(status_frame, text="Disconnected", 
                                       text_color="red", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(pady=10)
        
        # Control buttons
        button_frame = ctk.CTkFrame(control_tab)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.start_button = ctk.CTkButton(button_frame, text="Start Bot", 
                                        command=self.start_bot,
                                        height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.start_button.pack(side="left", padx=10, pady=20)
        
        self.stop_button = ctk.CTkButton(button_frame, text="Stop Bot", 
                                        command=self.stop_bot,
                                        height=50, font=ctk.CTkFont(size=16, weight="bold"),
                                        state="disabled")
        self.stop_button.pack(side="left", padx=10, pady=20)
        
        # Logs section
        logs_frame = ctk.CTkFrame(control_tab)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        logs_label = ctk.CTkLabel(logs_frame, text="Bot Logs", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        logs_label.pack(pady=(20, 10))
        
        self.logs_text = ctk.CTkTextbox(logs_frame, height=200)
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_text = ctk.CTkLabel(status_frame, text="Ready")
        self.status_text.pack(side="left", padx=10, pady=5)
    
    def toggle_token_visibility(self):
        """Toggle token visibility"""
        if self.show_token_var.get():
            self.token_entry.configure(show="")
        else:
            self.token_entry.configure(show="*")
    
    def save_configuration(self):
        """Save configuration"""
        # Update config with current values
        self.config["token"] = self.token_entry.get()
        self.config["case_sensitive"] = self.case_sensitive_var.get()
        self.config["respond_to_self"] = self.respond_self_var.get()
        self.config["reply_to_message"] = self.reply_message_var.get()
        
        if self.save_config():
            self.status_text.configure(text="Configuration saved successfully!")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        else:
            self.status_text.configure(text="Failed to save configuration")
    
    def add_keyword(self):
        """Add new keyword"""
        keyword = self.new_keyword_entry.get().strip()
        response = self.new_response_entry.get().strip()
        
        if not keyword or not response:
            messagebox.showerror("Error", "Please enter both keyword and response")
            return
        
        if keyword in self.config["keywords"]:
            messagebox.showerror("Error", "Keyword already exists")
            return
        
        self.config["keywords"][keyword] = response
        if self.save_config():
            self.new_keyword_entry.delete(0, "end")
            self.new_response_entry.delete(0, "end")
            self.refresh_keywords_list()
            self.status_text.configure(text=f"Added keyword: {keyword}")
    
    def remove_keyword(self, keyword):
        """Remove keyword"""
        if keyword in self.config["keywords"]:
            del self.config["keywords"][keyword]
            if self.save_config():
                self.refresh_keywords_list()
                self.status_text.configure(text=f"Removed keyword: {keyword}")
    
    def refresh_keywords_list(self):
        """Refresh keywords list display"""
        # Clear existing widgets
        for widget in self.keywords_listbox.winfo_children():
            widget.destroy()
        
        # Add keywords
        for keyword, response in self.config["keywords"].items():
            keyword_frame = ctk.CTkFrame(self.keywords_listbox)
            keyword_frame.pack(fill="x", padx=5, pady=5)
            
            # Keyword and response
            ctk.CTkLabel(keyword_frame, text=f"'{keyword}' → '{response}'", 
                        font=ctk.CTkFont(size=12)).pack(side="left", padx=10, pady=5)
            
            # Remove button
            remove_button = ctk.CTkButton(keyword_frame, text="Remove", 
                                        command=lambda k=keyword: self.remove_keyword(k),
                                        width=80, height=30)
            remove_button.pack(side="right", padx=10, pady=5)
    
    def add_role_mention(self):
        """Add new role mention"""
        role_id = self.new_role_id_entry.get().strip()
        response = self.new_role_response_entry.get().strip()
        
        if not role_id or not response:
            messagebox.showerror("Error", "Please enter both role ID and response")
            return
        
        if role_id in self.config.get("role_mentions", {}):
            messagebox.showerror("Error", "Role ID already exists")
            return
        
        # Initialize role_mentions if it doesn't exist
        if "role_mentions" not in self.config:
            self.config["role_mentions"] = {}
        
        self.config["role_mentions"][role_id] = response
        if self.save_config():
            self.new_role_id_entry.delete(0, "end")
            self.new_role_response_entry.delete(0, "end")
            self.refresh_role_mentions_list()
            self.status_text.configure(text=f"Added role mention: {role_id}")
    
    def remove_role_mention(self, role_id):
        """Remove role mention"""
        if "role_mentions" in self.config and role_id in self.config["role_mentions"]:
            del self.config["role_mentions"][role_id]
            if self.save_config():
                self.refresh_role_mentions_list()
                self.status_text.configure(text=f"Removed role mention: {role_id}")
    
    def refresh_role_mentions_list(self):
        """Refresh role mentions list display"""
        # Clear existing widgets
        for widget in self.role_mentions_listbox.winfo_children():
            widget.destroy()
        
        # Add role mentions
        role_mentions = self.config.get("role_mentions", {})
        for role_id, response in role_mentions.items():
            role_frame = ctk.CTkFrame(self.role_mentions_listbox)
            role_frame.pack(fill="x", padx=5, pady=5)
            
            # Role ID and response
            ctk.CTkLabel(role_frame, text=f"Role ID: {role_id} → '{response}'", 
                        font=ctk.CTkFont(size=12)).pack(side="left", padx=10, pady=5)
            
            # Remove button
            remove_button = ctk.CTkButton(role_frame, text="Remove", 
                                        command=lambda r=role_id: self.remove_role_mention(r),
                                        width=80, height=30)
            remove_button.pack(side="right", padx=10, pady=5)
    
    def start_bot(self):
        """Start the bot"""
        if not self.config.get("token"):
            messagebox.showerror("Error", "Please enter a Discord token first")
            return
        
        try:
            # Start bot in separate process
            self.bot_process = subprocess.Popen([sys.executable, "bot.py"], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.STDOUT,
                                              text=True,
                                              bufsize=1,
                                              universal_newlines=True)
            
            self.bot_running = True
            self.status_label.configure(text="Running", text_color="green")
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_text.configure(text="Bot started successfully!")
            
            # Start monitoring bot output in a separate thread
            self.monitor_thread = threading.Thread(target=self.monitor_bot_output_thread, daemon=True)
            self.monitor_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bot: {e}")
    
    def stop_bot(self):
        """Stop the bot"""
        self.bot_running = False
        
        if self.bot_process:
            try:
                print("Stopping bot process...")
                
                # Try graceful shutdown first
                self.bot_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.bot_process.wait(timeout=5)
                    print("Bot stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't stop gracefully
                    print("Force killing bot process...")
                    self.bot_process.kill()
                    self.bot_process.wait()
                    print("Bot force killed")
                    
            except Exception as e:
                print(f"Error stopping bot: {e}")
            finally:
                self.bot_process = None
        
        # Clean up lock file if it exists
        try:
            if os.path.exists("bot.lock"):
                os.remove("bot.lock")
                print("Removed bot.lock file")
        except Exception as e:
            print(f"Could not remove lock file: {e}")
        
        self.status_label.configure(text="Stopped", text_color="red")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_text.configure(text="Bot stopped")
        
        # Update logs
        self.update_logs("Bot stopped and cleaned up\n")
    
    def on_closing(self):
        """Handle window closing - ensure bot is stopped"""
        if self.bot_running and self.bot_process:
            print("GUI closing - stopping bot...")
            self.stop_bot()
        
        # Wait a moment for cleanup
        self.root.after(1000, self.root.destroy)
    
    def monitor_bot_output_thread(self):
        """Monitor bot output in a separate thread"""
        while self.bot_running and self.bot_process:
            try:
                # Read output line by line
                output = self.bot_process.stdout.readline()
                if output:
                    # Schedule GUI update on main thread
                    self.root.after(0, self.update_logs, output)
                
                # Check if process is still running
                if self.bot_process and self.bot_process.poll() is not None:
                    self.root.after(0, self.stop_bot)
                    break
                
                # Small delay to prevent excessive CPU usage
                import time
                time.sleep(0.1)
                
            except Exception as e:
                self.root.after(0, self.update_logs, f"Error monitoring bot: {e}\n")
                break
    
    def update_logs(self, output):
        """Update logs display (called from main thread)"""
        if output:
            self.logs_text.insert("end", output)
            self.logs_text.see("end")
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DiscordBotGUI()
    app.run()
