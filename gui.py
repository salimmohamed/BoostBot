import customtkinter as ctk
import json
import threading
import subprocess
import sys
import os
from tkinter import messagebox
from config_manager import ConfigManager

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
        
        # Config manager
        self.config_manager = ConfigManager()
        
        # Channel name cache
        self.channel_name_cache = {}
        
        # Load configuration
        self.config = self.load_config()
        
        # Load cached channel names on startup
        self.load_cached_channel_names()
        
        # Create GUI
        self.create_widgets()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_config(self):
        """Load configuration using ConfigManager"""
        try:
            config, message = self.config_manager.load_config()
            if config is None:
                print(f"ERROR: {message}")
                # Try to create default config
                success, msg = self.config_manager.create_config("config.json")
                if success:
                    config, message = self.config_manager.load_config()
                    if config is None:
                        print(f"ERROR creating default config: {message}")
                        return self.config_manager.get_default_config()
                else:
                    print(f"ERROR creating default config: {msg}")
                    return self.config_manager.get_default_config()
            return config
        except Exception as e:
            print(f"ERROR loading config: {e}")
            return self.config_manager.get_default_config()
    
    def save_config(self):
        """Save configuration using ConfigManager"""
        try:
            success, message = self.config_manager.save_config(self.config)
            if not success:
                messagebox.showerror("Error", f"Failed to save configuration: {message}")
            return success
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            return False
    
    def load_cached_channel_names(self):
        """Load channel names from persistent cache"""
        try:
            import json
            from datetime import datetime, timedelta
            
            if not os.path.exists("channel_names_cache.json"):
                print("No channel names cache found")
                return
            
            with open("channel_names_cache.json", "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid (7 days)
            last_updated = datetime.fromisoformat(cache_data.get("last_updated", ""))
            cache_age = datetime.now() - last_updated
            
            if cache_age < timedelta(days=7):
                self.channel_name_cache = cache_data.get("channels", {})
                print(f"Loaded {len(self.channel_name_cache)} cached channel names")
            else:
                print("Channel names cache is stale (older than 7 days)")
                
        except Exception as e:
            print(f"Error loading cached channel names: {e}")
    
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
        
        # Channels tab
        self.create_channels_tab()
        
        # Bot Control tab
        self.create_control_tab()
        
        # Config Management tab
        self.create_config_management_tab()
        
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
        
        # Message delay timer
        delay_frame = ctk.CTkFrame(settings_frame)
        delay_frame.pack(fill="x", pady=10)
        
        delay_label = ctk.CTkLabel(delay_frame, text="Message Delay Timer", 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        delay_label.pack(pady=(10, 5))
        
        delay_info = ctk.CTkLabel(delay_frame, 
                                text="Global delay between messages (prevents rate limiting)",
                                font=ctk.CTkFont(size=12))
        delay_info.pack(pady=2)
        
        # Timer slider
        self.delay_var = ctk.IntVar(value=self.config.get("message_delay_minutes", 5))
        self.delay_slider = ctk.CTkSlider(delay_frame, from_=0, to=30, 
                                        variable=self.delay_var, 
                                        command=self.update_delay_label,
                                        number_of_steps=30)
        self.delay_slider.pack(fill="x", padx=20, pady=10)
        
        # Delay value label
        initial_delay = self.delay_var.get()
        initial_text = "No delay" if initial_delay == 0 else f"{initial_delay} minutes"
        self.delay_value_label = ctk.CTkLabel(delay_frame, 
                                            text=initial_text,
                                            font=ctk.CTkFont(size=14, weight="bold"))
        self.delay_value_label.pack(pady=5)
        
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
    
    def create_channels_tab(self):
        """Create channels management tab"""
        channels_tab = self.notebook.add("Channels")
        
        # Info section
        info_frame = ctk.CTkFrame(channels_tab)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        info_label = ctk.CTkLabel(info_frame, text="Channel Restrictions", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        info_label.pack(pady=(20, 10))
        
        info_text = ctk.CTkLabel(info_frame, 
                               text="The bot will only respond in the specified channels.\nLeave empty to listen in ALL channels.\nTo get a channel ID: Right-click the channel → Copy ID (requires Developer Mode)",
                               font=ctk.CTkFont(size=12))
        info_text.pack(pady=10)
        
        # Add channel section
        add_frame = ctk.CTkFrame(channels_tab)
        add_frame.pack(fill="x", padx=20, pady=20)
        
        add_label = ctk.CTkLabel(add_frame, text="Add New Channel", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        add_label.pack(pady=(20, 10))
        
        # Channel ID input
        channel_id_frame = ctk.CTkFrame(add_frame)
        channel_id_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(channel_id_frame, text="Channel ID:").pack(side="left", padx=10)
        self.new_channel_id_entry = ctk.CTkEntry(channel_id_frame, placeholder_text="Enter channel ID...")
        self.new_channel_id_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Add button
        add_channel_button = ctk.CTkButton(add_frame, text="Add Channel", 
                                         command=self.add_channel)
        add_channel_button.pack(pady=10)
        
        # Channels list
        channels_list_frame = ctk.CTkFrame(channels_tab)
        channels_list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with refresh button
        header_frame = ctk.CTkFrame(channels_list_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        channels_list_label = ctk.CTkLabel(header_frame, text="Allowed Channels", 
                                         font=ctk.CTkFont(size=16, weight="bold"))
        channels_list_label.pack(side="left", padx=10, pady=5)
        
        # Button frame
        button_frame = ctk.CTkFrame(header_frame)
        button_frame.pack(side="right", padx=10, pady=5)
        
        # Refresh button
        refresh_channels_button = ctk.CTkButton(button_frame, text="Refresh", 
                                              command=self.refresh_channels_list,
                                              width=80, height=30)
        refresh_channels_button.pack(side="left", padx=5)
        
        # Get all names button (safer approach)
        get_all_names_button = ctk.CTkButton(button_frame, text="Get All Names", 
                                           command=self.get_all_channel_names,
                                           width=100, height=30)
        get_all_names_button.pack(side="left", padx=5)
        
        # Create documentation button
        create_docs_button = ctk.CTkButton(button_frame, text="Create Docs", 
                                         command=self.create_channel_documentation,
                                         width=90, height=30)
        create_docs_button.pack(side="left", padx=5)
        
        # Channels listbox with scrollbar
        self.channels_listbox = ctk.CTkScrollableFrame(channels_list_frame, height=300)
        self.channels_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_channels_list()
    
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
        
        # Info dump buttons
        info_frame = ctk.CTkFrame(control_tab)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        info_label = ctk.CTkLabel(info_frame, text="Bot Information", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        info_label.pack(pady=(20, 10))
        
        dump_buttons_frame = ctk.CTkFrame(info_frame)
        dump_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        self.dump_roles_button = ctk.CTkButton(dump_buttons_frame, text="Dump Roles", 
                                             command=self.dump_roles,
                                             height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.dump_roles_button.pack(side="left", padx=10, pady=10)
        
        self.dump_channels_button = ctk.CTkButton(dump_buttons_frame, text="Dump Channels", 
                                                command=self.dump_channels,
                                                height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.dump_channels_button.pack(side="left", padx=10, pady=10)
        
        # Test button to check if bot is monitoring files (commented out - uncomment if needed for debugging)
        # self.test_bot_button = ctk.CTkButton(dump_buttons_frame, text="Test Bot", 
        #                                    command=self.test_bot_connection,
        #                                    height=40, font=ctk.CTkFont(size=14, weight="bold"))
        # self.test_bot_button.pack(side="left", padx=10, pady=10)
        
        # Logs section
        logs_frame = ctk.CTkFrame(control_tab)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        logs_label = ctk.CTkLabel(logs_frame, text="Bot Logs", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        logs_label.pack(pady=(20, 10))
        
        self.logs_text = ctk.CTkTextbox(logs_frame, height=200)
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_config_management_tab(self):
        """Create config management tab"""
        config_mgmt_tab = self.notebook.add("Config Management")
        
        # Current config section
        current_frame = ctk.CTkFrame(config_mgmt_tab)
        current_frame.pack(fill="x", padx=20, pady=20)
        
        current_label = ctk.CTkLabel(current_frame, text="Current Configuration", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        current_label.pack(pady=(20, 10))
        
        # Current config name display
        self.current_config_label = ctk.CTkLabel(current_frame, 
                                               text=f"Loaded: {self.config_manager.get_current_config_name() or 'None'}", 
                                               font=ctk.CTkFont(size=14))
        self.current_config_label.pack(pady=10)
        
        # Config selection section
        selection_frame = ctk.CTkFrame(config_mgmt_tab)
        selection_frame.pack(fill="x", padx=20, pady=20)
        
        selection_label = ctk.CTkLabel(selection_frame, text="Load Configuration", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        selection_label.pack(pady=(20, 10))
        
        # Config dropdown
        config_dropdown_frame = ctk.CTkFrame(selection_frame)
        config_dropdown_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(config_dropdown_frame, text="Select Config:").pack(side="left", padx=10)
        self.config_dropdown = ctk.CTkComboBox(config_dropdown_frame, 
                                              values=self.get_available_configs(),
                                              command=self.on_config_selected)
        self.config_dropdown.pack(side="left", padx=10, fill="x", expand=True)
        
        # Load button
        load_button = ctk.CTkButton(config_dropdown_frame, text="Load", 
                                  command=self.load_selected_config,
                                  width=80)
        load_button.pack(side="right", padx=10)
        
        # Config management section
        management_frame = ctk.CTkFrame(config_mgmt_tab)
        management_frame.pack(fill="x", padx=20, pady=20)
        
        management_label = ctk.CTkLabel(management_frame, text="Configuration Management", 
                                      font=ctk.CTkFont(size=16, weight="bold"))
        management_label.pack(pady=(20, 10))
        
        # New config section
        new_config_frame = ctk.CTkFrame(management_frame)
        new_config_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(new_config_frame, text="Create New Config:").pack(side="left", padx=10)
        self.new_config_entry = ctk.CTkEntry(new_config_frame, placeholder_text="Enter config name...")
        self.new_config_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        create_button = ctk.CTkButton(new_config_frame, text="Create", 
                                    command=self.create_new_config,
                                    width=80)
        create_button.pack(side="right", padx=10)
        
        # Copy config section
        copy_config_frame = ctk.CTkFrame(management_frame)
        copy_config_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(copy_config_frame, text="Copy Config:").pack(side="left", padx=10)
        self.copy_source_dropdown = ctk.CTkComboBox(copy_config_frame, 
                                                  values=self.get_available_configs())
        self.copy_source_dropdown.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkLabel(copy_config_frame, text="to:").pack(side="left", padx=5)
        self.copy_target_entry = ctk.CTkEntry(copy_config_frame, placeholder_text="New name...")
        self.copy_target_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        copy_button = ctk.CTkButton(copy_config_frame, text="Copy", 
                                  command=self.copy_config,
                                  width=80)
        copy_button.pack(side="right", padx=10)
        
        # Config list section
        list_frame = ctk.CTkFrame(config_mgmt_tab)
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        list_label = ctk.CTkLabel(list_frame, text="Available Configurations", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        list_label.pack(pady=(20, 10))
        
        # Config list with scrollbar
        self.config_listbox = ctk.CTkScrollableFrame(list_frame, height=200)
        self.config_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_config_list()
    
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
    
    def update_delay_label(self, value):
        """Update the delay label when slider changes"""
        minutes = int(float(value))
        if minutes == 0:
            self.delay_value_label.configure(text="No delay")
        else:
            self.delay_value_label.configure(text=f"{minutes} minutes")
    
    def save_configuration(self):
        """Save configuration"""
        # Update config with current values
        self.config["token"] = self.token_entry.get()
        self.config["case_sensitive"] = self.case_sensitive_var.get()
        self.config["respond_to_self"] = self.respond_self_var.get()
        self.config["reply_to_message"] = self.reply_message_var.get()
        self.config["message_delay_minutes"] = self.delay_var.get()
        
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
    
    def add_channel(self):
        """Add new channel"""
        channel_id = self.new_channel_id_entry.get().strip()
        
        if not channel_id:
            messagebox.showerror("Error", "Please enter a channel ID")
            return
        
        # Initialize allowed_channels if it doesn't exist
        if "allowed_channels" not in self.config:
            self.config["allowed_channels"] = []
        
        if channel_id in self.config["allowed_channels"]:
            messagebox.showerror("Error", "Channel ID already exists")
            return
        
        self.config["allowed_channels"].append(channel_id)
        if self.save_config():
            self.new_channel_id_entry.delete(0, "end")
            self.refresh_channels_list()
            self.status_text.configure(text=f"Added channel: {channel_id}")
    
    def remove_channel(self, channel_id):
        """Remove channel"""
        if "allowed_channels" in self.config and channel_id in self.config["allowed_channels"]:
            self.config["allowed_channels"].remove(channel_id)
            if self.save_config():
                self.refresh_channels_list()
                self.status_text.configure(text=f"Removed channel: {channel_id}")
    
    def get_channel_readable_name(self, channel_id):
        """Get readable name for a channel ID"""
        try:
            # Check cache first
            if channel_id in self.channel_name_cache:
                return self.channel_name_cache[channel_id]

            # If not in cache, show ID with note
            fallback_name = f"Channel ID: {channel_id} (not cached - use 'Get All Names')"
            return fallback_name

        except Exception as e:
            error_name = f"Channel ID: {channel_id} (error: {e})"
            return error_name
    
    def refresh_channels_list(self):
        """Refresh channels list display"""
        try:
            # Clear existing widgets
            for widget in self.channels_listbox.winfo_children():
                widget.destroy()
            
            # DON'T clear cache - use cached names if available
            # self.channel_name_cache.clear()  # REMOVED THIS LINE
            
            # Add channels
            allowed_channels = self.config.get("allowed_channels", [])
            if not allowed_channels:
                # Show message when no channels are specified
                no_channels_label = ctk.CTkLabel(self.channels_listbox, 
                                               text="No channels specified - bot will listen in ALL channels",
                                               font=ctk.CTkFont(size=12),
                                               text_color="gray")
                no_channels_label.pack(pady=20)
            else:
                # Show normal list
                self._show_channels_list(allowed_channels)
                    
        except Exception as e:
            print(f"Error refreshing channels list: {e}")
            # Show error message
            error_label = ctk.CTkLabel(self.channels_listbox, 
                                      text=f"Error refreshing channels: {e}",
                                      font=ctk.CTkFont(size=12),
                                      text_color="red")
            error_label.pack(pady=20)
    
    def _show_channels_list(self, allowed_channels):
        """Show the channels list"""
        try:
            for channel_id in allowed_channels:
                channel_frame = ctk.CTkFrame(self.channels_listbox)
                channel_frame.pack(fill="x", padx=5, pady=5)
                
                # Get readable name for the channel
                readable_name = self.get_channel_readable_name(channel_id)
                
                # Channel info with readable name
                channel_label = ctk.CTkLabel(channel_frame, text=readable_name, 
                                           font=ctk.CTkFont(size=12))
                channel_label.pack(side="left", padx=10, pady=5)
                
                # Remove button
                remove_button = ctk.CTkButton(channel_frame, text="Remove", 
                                            command=lambda c=channel_id: self.remove_channel(c),
                                            width=80, height=30)
                remove_button.pack(side="right", padx=10, pady=5)
        except Exception as e:
            print(f"Error showing channels list: {e}")
    
    def get_all_channel_names(self):
        """Get all channel names using the safer bulk dump approach"""
        try:
            if not (hasattr(self, 'bot_process') and self.bot_process and self.bot_process.poll() is None):
                messagebox.showwarning("Warning", "Bot is not running. Start the bot first to get channel names.")
                return
            
            # Use the existing bulk dump functionality which is safer
            try:
                with open("get_channel_names", "w") as f:
                    f.write("dump_channels")
                
                # Show message that we're getting names
                for widget in self.channels_listbox.winfo_children():
                    widget.destroy()
                
                loading_label = ctk.CTkLabel(self.channels_listbox, 
                                           text="Getting all channel names from bot...\nCheck the bot console for results.",
                                           font=ctk.CTkFont(size=12),
                                           text_color="orange")
                loading_label.pack(pady=20)
                
                self.status_text.configure(text="Requesting all channel names from bot...")
                
                # Schedule a refresh after a delay
                self.root.after(3000, self._refresh_after_bulk_dump)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to request channel names: {e}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get channel names: {e}")
    
    def _refresh_after_bulk_dump(self):
        """Refresh the channels list after bulk dump"""
        try:
            # Clear the loading message
            for widget in self.channels_listbox.winfo_children():
                widget.destroy()
            
            # Try to parse channel names from bot logs and update cache
            self._parse_channel_names_from_logs()
            
            # Show normal list (names will be cached from bulk dump)
            allowed_channels = self.config.get("allowed_channels", [])
            self._show_channels_list(allowed_channels)
            
            self.status_text.configure(text="Channel names updated")
            
        except Exception as e:
            print(f"Error refreshing after bulk dump: {e}")
    
    def _parse_channel_names_from_logs(self):
        """Parse channel names from bot logs and update cache"""
        try:
            # Read the channel mapping file that the bot created
            if os.path.exists("channel_mapping.txt"):
                with open("channel_mapping.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                # Parse the mapping file
                for line in lines:
                    if '|' in line:
                        channel_id, readable_name = line.strip().split('|', 1)
                        self.channel_name_cache[channel_id] = readable_name
                
                # Clean up the mapping file
                os.remove("channel_mapping.txt")
                print(f"Loaded {len(self.channel_name_cache)} channel names from mapping file")
                
                # Save updated cache to persistent storage
                self.save_channel_names_cache()
                        
        except Exception as e:
            print(f"Error parsing channel names from mapping file: {e}")
    
    def save_channel_names_cache(self):
        """Save channel names cache to persistent storage"""
        try:
            import json
            from datetime import datetime
            
            cache_data = {
                "last_updated": datetime.now().isoformat(),
                "channels": self.channel_name_cache
            }
            
            with open("channel_names_cache.json", "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"Saved {len(self.channel_name_cache)} channel names to cache")
        except Exception as e:
            print(f"Error saving channel names cache: {e}")
    
    def create_channel_documentation(self):
        """Create channel documentation file"""
        try:
            if not (hasattr(self, 'bot_process') and self.bot_process and self.bot_process.poll() is None):
                messagebox.showwarning("Warning", "Bot is not running. Start the bot first to create documentation.")
                return
            
            # Request documentation creation from bot
            try:
                with open("create_documentation", "w") as f:
                    f.write("create_docs")
                
                self.status_text.configure(text="Creating channel documentation...")
                messagebox.showinfo("Success", "Channel documentation will be created.\nCheck for 'channel_names.md' file.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to request documentation creation: {e}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create documentation: {e}")
    
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
            
            # Add initial log message
            self.update_logs("Starting bot process...\n")
            
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
            # Add debug info to see what we're receiving
            self.logs_text.insert("end", output)
            self.logs_text.see("end")
            # Also print to console for debugging
            print(f"GUI received: {repr(output)}")
    
    def dump_roles(self):
        """Dump role information to console"""
        try:
            self.update_logs("=== ROLE INFORMATION DUMP ===\n")
            
            role_mentions = self.config.get("role_mentions", {})
            if not role_mentions:
                self.update_logs("No role mentions configured\n")
            else:
                # Try to get formatted info from bot if it's running
                if hasattr(self, 'bot_process') and self.bot_process:
                    try:
                        with open("get_role_names", "w") as f:
                            f.write("dump_roles")
                        self.update_logs("Requesting role names from bot...\n")
                        # Verify file was created
                        if os.path.exists("get_role_names"):
                            self.update_logs("Role request file created successfully\n")
                        else:
                            self.update_logs("ERROR: Role request file was not created\n")
                        self.status_text.configure(text="Requesting role information from bot...")
                    except Exception as e:
                        self.update_logs(f"Failed to request from bot: {e}\n")
                        # Fallback to basic info
                        self.update_logs(f"Found {len(role_mentions)} role mentions in config:\n")
                        for role_id, response in role_mentions.items():
                            self.update_logs(f"Role ID: {role_id} | Response: '{response}'\n")
                else:
                    # Fallback to basic info if bot not running
                    self.update_logs(f"Found {len(role_mentions)} role mentions in config:\n")
                    for role_id, response in role_mentions.items():
                        self.update_logs(f"Role ID: {role_id} | Response: '{response}'\n")
            
            self.update_logs("=== END ROLE DUMP ===\n")
            self.status_text.configure(text="Role information dumped to console")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to dump roles: {e}")
    
    def dump_channels(self):
        """Dump channel information to console"""
        try:
            self.update_logs("=== CHANNEL INFORMATION DUMP ===\n")
            
            allowed_channels = self.config.get("allowed_channels", [])
            if not allowed_channels:
                self.update_logs("No channel restrictions - listening in ALL channels\n")
            else:
                # Try to get formatted info from bot if it's running
                if hasattr(self, 'bot_process') and self.bot_process:
                    try:
                        with open("get_channel_names", "w") as f:
                            f.write("dump_channels")
                        self.update_logs("Requesting channel names from bot...\n")
                        # Verify file was created
                        if os.path.exists("get_channel_names"):
                            self.update_logs("Channel request file created successfully\n")
                            self.update_logs("Bot will resolve channel names and display them in the console.\n")
                            self.update_logs("Check the bot console output for detailed channel information.\n")
                        else:
                            self.update_logs("ERROR: Channel request file was not created\n")
                        self.status_text.configure(text="Requesting channel information from bot...")
                    except Exception as e:
                        self.update_logs(f"Failed to request from bot: {e}\n")
                        # Fallback to basic info
                        self.update_logs(f"Found {len(allowed_channels)} allowed channels in config:\n")
                        for channel_id in allowed_channels:
                            readable_name = self.get_channel_readable_name(channel_id)
                            self.update_logs(f"  {readable_name}\n")
                else:
                    # Fallback to basic info if bot not running
                    self.update_logs(f"Found {len(allowed_channels)} allowed channels in config:\n")
                    for channel_id in allowed_channels:
                        self.update_logs(f"Channel ID: {channel_id}\n")
            
            self.update_logs("=== END CHANNEL DUMP ===\n")
            self.status_text.configure(text="Channel information dumped to console")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to dump channels: {e}")
    
    # Test bot connection function (commented out - uncomment if needed for debugging)
    # def test_bot_connection(self):
    #     """Test if bot is monitoring files"""
    #     try:
    #         self.update_logs("=== BOT CONNECTION TEST ===\n")
    #         
    #         if hasattr(self, 'bot_process') and self.bot_process:
    #             # Create a test file
    #             with open("test_bot_connection", "w") as f:
    #                 f.write("test")
    #             self.update_logs("Test file created - waiting for bot response...\n")
    #             self.status_text.configure(text="Testing bot connection...")
    #         else:
    #             self.update_logs("Bot is not running - cannot test connection\n")
    #         
    #         self.update_logs("=== END BOT TEST ===\n")
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to test bot: {e}")
    
    def get_available_configs(self):
        """Get list of available configuration files"""
        return self.config_manager.get_config_names()
    
    def on_config_selected(self, selected_config):
        """Handle config selection from dropdown"""
        pass  # Could add preview functionality here
    
    def load_selected_config(self):
        """Load the selected configuration"""
        selected_config = self.config_dropdown.get()
        if not selected_config:
            messagebox.showerror("Error", "Please select a configuration to load")
            return
        
        try:
            # Load the new config
            new_config, message = self.config_manager.load_config(selected_config)
            if new_config is None:
                messagebox.showerror("Error", f"Failed to load config: {message}")
                return
            
            # Update current config
            self.config = new_config
            
            # Update UI elements with new config
            self.update_ui_with_config()
            
            # Update current config label
            self.current_config_label.configure(text=f"Loaded: {selected_config}")
            
            # Refresh dropdowns
            self.refresh_config_dropdowns()
            
            self.status_text.configure(text=f"Loaded configuration: {selected_config}")
            messagebox.showinfo("Success", f"Configuration '{selected_config}' loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def create_new_config(self):
        """Create a new configuration file"""
        config_name = self.new_config_entry.get().strip()
        if not config_name:
            messagebox.showerror("Error", "Please enter a configuration name")
            return
        
        try:
            # Create new config based on current config
            success, message = self.config_manager.create_config(config_name, self.config)
            if success:
                self.new_config_entry.delete(0, "end")
                self.refresh_config_list()
                self.refresh_config_dropdowns()
                self.status_text.configure(text=f"Created configuration: {config_name}")
                messagebox.showinfo("Success", f"Configuration '{config_name}' created successfully!")
            else:
                messagebox.showerror("Error", f"Failed to create config: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create configuration: {e}")
    
    def copy_config(self):
        """Copy an existing configuration"""
        source_config = self.copy_source_dropdown.get()
        target_name = self.copy_target_entry.get().strip()
        
        if not source_config or not target_name:
            messagebox.showerror("Error", "Please select source config and enter target name")
            return
        
        try:
            success, message = self.config_manager.copy_config(source_config, target_name)
            if success:
                self.copy_target_entry.delete(0, "end")
                self.refresh_config_list()
                self.refresh_config_dropdowns()
                self.status_text.configure(text=f"Copied configuration: {source_config} -> {target_name}")
                messagebox.showinfo("Success", f"Configuration copied successfully!")
            else:
                messagebox.showerror("Error", f"Failed to copy config: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy configuration: {e}")
    
    def delete_config(self, config_name):
        """Delete a configuration file"""
        if config_name == "config.json":
            messagebox.showerror("Error", "Cannot delete the default configuration file")
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                  f"Are you sure you want to delete configuration '{config_name}'?\nThis action cannot be undone.")
        if result:
            try:
                success, message = self.config_manager.delete_config(config_name)
                if success:
                    self.refresh_config_list()
                    self.refresh_config_dropdowns()
                    self.status_text.configure(text=f"Deleted configuration: {config_name}")
                    messagebox.showinfo("Success", f"Configuration '{config_name}' deleted successfully!")
                else:
                    messagebox.showerror("Error", f"Failed to delete config: {message}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete configuration: {e}")
    
    def refresh_config_list(self):
        """Refresh the configuration list display"""
        # Clear existing widgets
        for widget in self.config_listbox.winfo_children():
            widget.destroy()
        
        # Get available configs
        configs = self.get_available_configs()
        
        if not configs:
            no_configs_label = ctk.CTkLabel(self.config_listbox, 
                                          text="No configuration files found",
                                          font=ctk.CTkFont(size=12),
                                          text_color="gray")
            no_configs_label.pack(pady=20)
            return
        
        # Add each config
        for config_name in configs:
            config_frame = ctk.CTkFrame(self.config_listbox)
            config_frame.pack(fill="x", padx=5, pady=5)
            
            # Config name and status
            is_current = config_name == self.config_manager.get_current_config_name()
            status_text = " (Current)" if is_current else ""
            config_label = ctk.CTkLabel(config_frame, 
                                      text=f"{config_name}{status_text}", 
                                      font=ctk.CTkFont(size=12))
            config_label.pack(side="left", padx=10, pady=5)
            
            # Delete button (if not current and not default)
            if not is_current and config_name != "config.json":
                delete_button = ctk.CTkButton(config_frame, text="Delete", 
                                            command=lambda c=config_name: self.delete_config(c),
                                            width=80, height=30)
                delete_button.pack(side="right", padx=10, pady=5)
    
    def refresh_config_dropdowns(self):
        """Refresh all config dropdowns"""
        configs = self.get_available_configs()
        self.config_dropdown.configure(values=configs)
        self.copy_source_dropdown.configure(values=configs)
    
    def update_ui_with_config(self):
        """Update UI elements with current config data"""
        # Update token
        self.token_entry.delete(0, "end")
        self.token_entry.insert(0, self.config.get("token", ""))
        
        # Update checkboxes
        self.case_sensitive_var.set(self.config.get("case_sensitive", False))
        self.respond_self_var.set(self.config.get("respond_to_self", False))
        self.reply_message_var.set(self.config.get("reply_to_message", True))
        
        # Update delay slider
        delay = self.config.get("message_delay_minutes", 5)
        self.delay_var.set(delay)
        self.update_delay_label(delay)
        
        # Refresh other lists
        self.refresh_keywords_list()
        self.refresh_role_mentions_list()
        self.refresh_channels_list()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DiscordBotGUI()
    app.run()
