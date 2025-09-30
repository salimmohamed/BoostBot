#!/usr/bin/env python3
"""
BoostBot Modern Desktop GUI - Fixed Version
A sleek, modern desktop interface using Flet framework
Replaces the old CustomTkinter GUI with a beautiful, responsive design
"""

import flet as ft
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from config_manager import ConfigManager

class ModernBoostBotGUI:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.bot_process = None
        self.bot_running = False
        self.channel_name_cache = {}
        self.config = self.load_config()
        self.load_cached_channel_names()
        
        # UI Components
        self.status_text = None
        self.token_field = None
        self.case_sensitive_switch = None
        self.respond_self_switch = None
        self.reply_message_switch = None
        self.delay_slider = None
        self.delay_label = None
        self.bot_status_text = None
        self.start_button = None
        self.stop_button = None
        self.logs_text = None
        
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
    
    def save_config(self, create_backup=True):
        """Save configuration using ConfigManager"""
        try:
            success, message = self.config_manager.save_config(self.config, create_backup=create_backup)
            return success
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False
    
    def load_cached_channel_names(self):
        """Load channel names from persistent cache"""
        try:
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
    
    def create_main_app(self, page: ft.Page):
        """Create the main application interface"""
        page.title = "BoostBot Control Panel"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = ft.Colors.BLACK
        page.padding = 0
        
        # Create navigation tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Configuration",
                    icon=ft.Icons.SETTINGS,
                    content=self.create_config_tab()
                ),
                ft.Tab(
                    text="Keywords",
                    icon=ft.Icons.KEYBOARD,
                    content=self.create_keywords_tab()
                ),
                ft.Tab(
                    text="Role Mentions",
                    icon=ft.Icons.PERSON,
                    content=self.create_role_mentions_tab()
                ),
                ft.Tab(
                    text="Channels",
                    icon=ft.Icons.TAG,
                    content=self.create_channels_tab()
                ),
                ft.Tab(
                    text="Bot Control",
                    icon=ft.Icons.POWER_SETTINGS_NEW,
                    content=self.create_bot_control_tab()
                ),
                ft.Tab(
                    text="Config Management",
                    icon=ft.Icons.FOLDER_OPEN,
                    content=self.create_config_management_tab()
                ),
            ],
            expand=True,
        )
        
        # Status bar
        self.status_bar = ft.Container(
            content=ft.Text("Ready", color=ft.Colors.GREY_400, size=12),
            bgcolor=ft.Colors.GREY_900,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_800)),
        )
        
        # Main layout
        page.add(
            ft.Container(
                content=ft.Column([
                    # Header
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SMART_TOY, color=ft.Colors.PURPLE_400, size=32),
                            ft.Text("BoostBot Control Panel", 
                                   size=24, 
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.Colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.START),
                        bgcolor=ft.Colors.GREY_900,
                        padding=ft.padding.all(16),
                        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_800)),
                    ),
                    # Main content
                    ft.Container(
                        content=self.tabs,
                        expand=True,
                        padding=ft.padding.all(16),
                    ),
                    # Status bar
                    self.status_bar,
                ], spacing=0),
                expand=True,
            )
        )
    
    def create_config_tab(self):
        """Create configuration tab"""
        # Discord token field
        self.token_field = ft.TextField(
            label="Discord Token",
            value=self.config.get("token", ""),
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.GREY_700,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
        )
        
        # Bot settings
        self.case_sensitive_switch = ft.Switch(
            label="Case Sensitive",
            value=self.config.get("case_sensitive", False),
            active_color=ft.Colors.PURPLE_400,
        )
        
        self.respond_self_switch = ft.Switch(
            label="Respond to Self",
            value=self.config.get("respond_to_self", False),
            active_color=ft.Colors.PURPLE_400,
        )
        
        self.reply_message_switch = ft.Switch(
            label="Reply to Message",
            value=self.config.get("reply_to_message", True),
            active_color=ft.Colors.PURPLE_400,
        )
        
        # Message delay slider
        self.delay_slider = ft.Slider(
            min=0,
            max=30,
            divisions=30,
            value=self.config.get("message_delay_minutes", 5),
            active_color=ft.Colors.PURPLE_400,
            inactive_color=ft.Colors.GREY_700,
        )
        
        self.delay_label = ft.Text(
            f"Message Delay: {int(self.delay_slider.value)} minutes",
            color=ft.Colors.GREY_400,
        )
        
        def on_delay_change(e):
            self.delay_label.value = f"Message Delay: {int(e.control.value)} minutes"
            self.delay_label.update()
        
        self.delay_slider.on_change = on_delay_change
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Configuration", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                
                # Discord Token
                ft.Container(
                    content=ft.Column([
                        ft.Text("Discord Token", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.token_field,
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Bot Settings
                ft.Container(
                    content=ft.Column([
                        ft.Text("Bot Settings", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.case_sensitive_switch,
                        self.respond_self_switch,
                        self.reply_message_switch,
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Message Delay
                ft.Container(
                    content=ft.Column([
                        ft.Text("Message Delay Timer", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.delay_label,
                        self.delay_slider,
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Save button
                ft.ElevatedButton(
                    "Save Configuration",
                    on_click=self.save_configuration,
                    bgcolor=ft.Colors.PURPLE_600,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    
    def create_keywords_tab(self):
        """Create keywords management tab"""
        self.keywords_list = ft.ListView(
            height=300,
            spacing=8,
        )
        
        self.new_keyword_field = ft.TextField(
            label="New Keyword",
            border_color=ft.Colors.GREY_700,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
        )
        
        self.new_response_field = ft.TextField(
            label="Response",
            border_color=ft.Colors.GREY_700,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Keywords", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                
                # Add new keyword
                ft.Container(
                    content=ft.Column([
                        ft.Text("Add New Keyword", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.new_keyword_field,
                        self.new_response_field,
                        ft.ElevatedButton(
                            "Add Keyword",
                            on_click=self.add_keyword,
                            bgcolor=ft.Colors.PURPLE_600,
                            color=ft.Colors.WHITE,
                        ),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Keywords list
                ft.Container(
                    content=ft.Column([
                        ft.Text("Current Keywords", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.keywords_list,
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    
    def create_role_mentions_tab(self):
        """Create role mentions management tab"""
        self.roles_list = ft.ListView(
            height=300,
            spacing=8,
        )
        
        self.new_role_id_field = ft.TextField(
            label="Role ID",
            border_color=ft.Colors.GREY_700,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
        )
        
        self.new_role_response_field = ft.TextField(
            label="Response",
            border_color=ft.Colors.GREY_700,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Role Mentions", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                
                # Information
                ft.Container(
                    content=ft.Text(
                        "To get a Role ID, enable Developer Mode in Discord (Settings > Advanced), then right-click a role and 'Copy Role ID'.",
                        color=ft.Colors.GREY_400,
                        size=12,
                    ),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Add new role mention
                ft.Container(
                    content=ft.Column([
                        ft.Text("Add New Role Mention", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.new_role_id_field,
                        self.new_role_response_field,
                        ft.ElevatedButton(
                            "Add Role Mention",
                            on_click=self.add_role_mention,
                            bgcolor=ft.Colors.PURPLE_600,
                            color=ft.Colors.WHITE,
                        ),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Roles list
                ft.Container(
                    content=ft.Column([
                        ft.Text("Current Role Mentions", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.roles_list,
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    
    def create_channels_tab(self):
        """Create channels management tab"""
        self.channels_list = ft.ListView(
            height=300,
            spacing=8,
        )
        
        self.new_channel_field = ft.TextField(
            label="Channel ID",
            border_color=ft.Colors.GREY_700,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Channels", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                
                # Information
                ft.Container(
                    content=ft.Text(
                        "Restrict the bot to specific channels. To get a Channel ID, enable Developer Mode, then right-click a channel and 'Copy Channel ID'. Leave empty to allow all channels.",
                        color=ft.Colors.GREY_400,
                        size=12,
                    ),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Add new channel
                ft.Container(
                    content=ft.Column([
                        ft.Text("Add New Channel", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.new_channel_field,
                        ft.Row([
                            ft.ElevatedButton(
                                "Add Channel",
                                on_click=self.add_channel,
                                bgcolor=ft.Colors.PURPLE_600,
                                color=ft.Colors.WHITE,
                            ),
                            ft.ElevatedButton(
                                "Refresh Names",
                                on_click=self.refresh_channels,
                                bgcolor=ft.Colors.GREY_600,
                                color=ft.Colors.WHITE,
                            ),
                            ft.ElevatedButton(
                                "Get All Names",
                                on_click=self.get_all_channel_names,
                                bgcolor=ft.Colors.GREY_600,
                                color=ft.Colors.WHITE,
                            ),
                        ]),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Channels list
                ft.Container(
                    content=ft.Column([
                        ft.Text("Allowed Channels", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.channels_list,
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    
    def create_bot_control_tab(self):
        """Create bot control tab"""
        self.bot_status_text = ft.Text(
            "Disconnected",
            color=ft.Colors.RED_400,
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        
        self.start_button = ft.ElevatedButton(
            "Start Bot",
            on_click=self.start_bot,
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
        
        self.stop_button = ft.ElevatedButton(
            "Stop Bot",
            on_click=self.stop_bot,
            bgcolor=ft.Colors.RED_600,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            disabled=True,
        )
        
        self.logs_text = ft.TextField(
            value="Bot logs will appear here...",
            multiline=True,
            read_only=True,
            height=200,
            border_color=ft.Colors.GREY_700,
            bgcolor=ft.Colors.GREY_900,
            color=ft.Colors.WHITE,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Bot Control", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                
                # Bot status
                ft.Container(
                    content=ft.Column([
                        ft.Text("Bot Status", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Row([
                            ft.Text("Status: ", color=ft.Colors.GREY_300),
                            self.bot_status_text,
                        ]),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Bot controls
                ft.Container(
                    content=ft.Column([
                        ft.Text("Controls", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Row([
                            self.start_button,
                            self.stop_button,
                        ]),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Bot information
                ft.Container(
                    content=ft.Column([
                        ft.Text("Bot Information", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Row([
                            ft.ElevatedButton(
                                "Dump Roles",
                                on_click=self.dump_roles,
                                bgcolor=ft.Colors.GREY_600,
                                color=ft.Colors.WHITE,
                            ),
                            ft.ElevatedButton(
                                "Dump Channels",
                                on_click=self.dump_channels,
                                bgcolor=ft.Colors.GREY_600,
                                color=ft.Colors.WHITE,
                            ),
                        ]),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Bot logs
                ft.Container(
                    content=ft.Column([
                        ft.Text("Bot Logs", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.logs_text,
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    
    def create_config_management_tab(self):
        """Create config management tab"""
        self.configs_list = ft.ListView(
            height=200,
            spacing=8,
        )
        
        self.new_config_field = ft.TextField(
            label="New Config Name",
            border_color=ft.Colors.GREY_700,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Config Management", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                
                # Current config
                ft.Container(
                    content=ft.Column([
                        ft.Text("Current Configuration", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(
                            f"Loaded: {self.config_manager.get_current_config_name() or 'None'}",
                            color=ft.Colors.PURPLE_400,
                        ),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Create new config
                ft.Container(
                    content=ft.Column([
                        ft.Text("Create New Config", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.new_config_field,
                        ft.ElevatedButton(
                            "Create Config",
                            on_click=self.create_new_config,
                            bgcolor=ft.Colors.PURPLE_600,
                            color=ft.Colors.WHITE,
                        ),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
                
                # Configs list
                ft.Container(
                    content=ft.Column([
                        ft.Text("Available Configurations", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.configs_list,
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=ft.padding.all(16),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    
    # Event handlers
    def save_configuration(self, e):
        """Save configuration"""
        self.config.update({
            "token": self.token_field.value,
            "case_sensitive": self.case_sensitive_switch.value,
            "respond_to_self": self.respond_self_switch.value,
            "reply_to_message": self.reply_message_switch.value,
            "message_delay_minutes": int(self.delay_slider.value),
        })
        
        if self.save_config():
            self.update_status("Configuration saved successfully!")
        else:
            self.update_status("Error saving configuration!")
    
    def add_keyword(self, e):
        """Add new keyword"""
        keyword = self.new_keyword_field.value.strip()
        response = self.new_response_field.value.strip()
        
        if not keyword or not response:
            self.update_status("Keyword and response cannot be empty!")
            return
        
        if keyword in self.config.get("keywords", {}):
            self.update_status("Keyword already exists!")
            return
        
        if "keywords" not in self.config:
            self.config["keywords"] = {}
        
        self.config["keywords"][keyword] = response
        
        self.new_keyword_field.value = ""
        self.new_response_field.value = ""
        self.new_keyword_field.update()
        self.new_response_field.update()
        
        self.refresh_keywords_list()
        self.update_status(f"Added keyword: {keyword}")
    
    def add_role_mention(self, e):
        """Add new role mention"""
        role_id = self.new_role_id_field.value.strip()
        response = self.new_role_response_field.value.strip()
        
        if not role_id or not response:
            self.update_status("Role ID and response cannot be empty!")
            return
        
        if "role_mentions" not in self.config:
            self.config["role_mentions"] = {}
        
        if role_id in self.config["role_mentions"]:
            self.update_status("Role ID already exists!")
            return
        
        self.config["role_mentions"][role_id] = response
        
        self.new_role_id_field.value = ""
        self.new_role_response_field.value = ""
        self.new_role_id_field.update()
        self.new_role_response_field.update()
        
        self.refresh_roles_list()
        self.update_status(f"Added role mention: {role_id}")
    
    def add_channel(self, e):
        """Add new channel"""
        channel_id = self.new_channel_field.value.strip()
        
        if not channel_id:
            self.update_status("Channel ID cannot be empty!")
            return
        
        if "allowed_channels" not in self.config:
            self.config["allowed_channels"] = []
        
        if channel_id in self.config["allowed_channels"]:
            self.update_status("Channel ID already exists!")
            return
        
        self.config["allowed_channels"].append(channel_id)
        
        self.new_channel_field.value = ""
        self.new_channel_field.update()
        
        self.refresh_channels_list()
        self.update_status(f"Added channel: {channel_id}")
    
    def start_bot(self, e):
        """Start bot button click"""
        if not self.config.get("token"):
            self.update_status("Please enter a Discord token first!")
            return
        
        try:
            # Save config first
            self.save_configuration(None)
            
            # Start bot process
            self.bot_process = subprocess.Popen(
                [sys.executable, "bot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Start log monitoring thread
            threading.Thread(target=self._monitor_bot_logs, daemon=True).start()
            
            self.bot_running = True
            self.bot_status_text.value = "Running"
            self.bot_status_text.color = ft.Colors.GREEN_400
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.update_status("Bot started successfully!")
            
        except Exception as ex:
            self.update_status(f"Error starting bot: {ex}")
        
        self.bot_status_text.update()
        self.start_button.update()
        self.stop_button.update()
    
    def stop_bot(self, e):
        """Stop bot button click"""
        try:
            if self.bot_process:
                self.bot_process.terminate()
                self.bot_process = None
            
            self.bot_running = False
            self.bot_status_text.value = "Disconnected"
            self.bot_status_text.color = ft.Colors.RED_400
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.update_status("Bot stopped successfully!")
            
        except Exception as ex:
            self.update_status(f"Error stopping bot: {ex}")
        
        self.bot_status_text.update()
        self.start_button.update()
        self.stop_button.update()
    
    def _monitor_bot_logs(self):
        """Monitor bot process output"""
        if not self.bot_process:
            return
        
        try:
            for line in iter(self.bot_process.stdout.readline, ''):
                if line.strip():
                    # Update logs in main thread
                    self.logs_text.value += line
                    self.logs_text.update()
        except:
            pass
    
    def dump_roles(self, e):
        """Dump roles information"""
        try:
            with open("get_role_names", "w") as f:
                f.write("")
            self.update_status("Role information dump requested")
            self.logs_text.value += "Role information dump requested\n"
            self.logs_text.update()
        except Exception as ex:
            self.update_status(f"Error requesting roles: {ex}")
    
    def dump_channels(self, e):
        """Dump channels information"""
        try:
            with open("get_channel_names", "w") as f:
                f.write("")
            self.update_status("Channel information dump requested")
            self.logs_text.value += "Channel information dump requested\n"
            self.logs_text.update()
        except Exception as ex:
            self.update_status(f"Error requesting channels: {ex}")
    
    def refresh_channels(self, e):
        """Refresh channel names from cache"""
        try:
            if os.path.exists("channel_names_cache.json"):
                with open("channel_names_cache.json", "r") as f:
                    cache_data = json.load(f)
                    self.channel_name_cache = cache_data.get("channels", {})
            
            self.refresh_channels_list()
            self.update_status("Channel list refreshed")
        except Exception as ex:
            self.update_status(f"Error refreshing channels: {ex}")
    
    def get_all_channel_names(self, e):
        """Get all channel names from bot"""
        try:
            with open("get_channel_names", "w") as f:
                f.write("")
            self.update_status("Channel names request sent to bot")
            self.logs_text.value += "Channel names request sent to bot\n"
            self.logs_text.update()
        except Exception as ex:
            self.update_status(f"Error requesting channel names: {ex}")
    
    def create_new_config(self, e):
        """Create new configuration file"""
        name = self.new_config_field.value.strip()
        if not name:
            self.update_status("Config name cannot be empty!")
            return
        
        if not name.endswith(".json"):
            name += ".json"
        
        try:
            # Create new config with current settings
            with open(name, "w") as f:
                json.dump(self.config, f, indent=4)
            
            self.new_config_field.value = ""
            self.new_config_field.update()
            self.update_status(f"Created new config: {name}")
        except Exception as ex:
            self.update_status(f"Error creating config: {ex}")
    
    def refresh_keywords_list(self):
        """Refresh keywords list display"""
        self.keywords_list.controls.clear()
        
        for keyword, response in self.config.get("keywords", {}).items():
            self.keywords_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"'{keyword}' → '{response}'", color=ft.Colors.WHITE),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_FOREVER,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, k=keyword: self.remove_keyword(k),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.Colors.GREY_800,
                    padding=ft.padding.all(12),
                    border_radius=8,
                )
            )
        
        self.keywords_list.update()
    
    def refresh_roles_list(self):
        """Refresh roles list display"""
        self.roles_list.controls.clear()
        
        for role_id, response in self.config.get("role_mentions", {}).items():
            self.roles_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"Role ID: {role_id} → '{response}'", color=ft.Colors.WHITE),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_FOREVER,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, r=role_id: self.remove_role_mention(r),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.Colors.GREY_800,
                    padding=ft.padding.all(12),
                    border_radius=8,
                )
            )
        
        self.roles_list.update()
    
    def refresh_channels_list(self):
        """Refresh channels list display"""
        self.channels_list.controls.clear()
        
        allowed_channels = self.config.get("allowed_channels", [])
        if not allowed_channels:
            self.channels_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No channels specified - bot will listen in ALL channels.",
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=ft.padding.all(20),
                )
            )
        else:
            for channel_id in allowed_channels:
                readable_name = self.get_channel_readable_name(channel_id)
                self.channels_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(readable_name, color=ft.Colors.WHITE),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_FOREVER,
                                icon_color=ft.Colors.RED_400,
                                on_click=lambda e, c=channel_id: self.remove_channel(c),
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        bgcolor=ft.Colors.GREY_800,
                        padding=ft.padding.all(12),
                        border_radius=8,
                    )
                )
        
        self.channels_list.update()
    
    def get_channel_readable_name(self, channel_id):
        """Get readable name for a channel ID"""
        try:
            if channel_id in self.channel_name_cache:
                return self.channel_name_cache[channel_id]
            return f"Channel ID: {channel_id} (not cached)"
        except Exception as e:
            return f"Channel ID: {channel_id} (error: {e})"
    
    def remove_keyword(self, keyword):
        """Remove keyword"""
        if keyword in self.config.get("keywords", {}):
            del self.config["keywords"][keyword]
            self.refresh_keywords_list()
            self.update_status(f"Removed keyword: {keyword}")
    
    def remove_role_mention(self, role_id):
        """Remove role mention"""
        if role_id in self.config.get("role_mentions", {}):
            del self.config["role_mentions"][role_id]
            self.refresh_roles_list()
            self.update_status(f"Removed role mention: {role_id}")
    
    def remove_channel(self, channel_id):
        """Remove channel"""
        if channel_id in self.config.get("allowed_channels", []):
            self.config["allowed_channels"].remove(channel_id)
            self.refresh_channels_list()
            self.update_status(f"Removed channel: {channel_id}")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.content.value = message
        self.status_bar.update()
        print(f"Status: {message}")

def main():
    """Main application entry point"""
    app = ModernBoostBotGUI()
    
    def on_page_ready(page: ft.Page):
        app.create_main_app(page)
        # Load initial data
        app.refresh_keywords_list()
        app.refresh_roles_list()
        app.refresh_channels_list()
    
    ft.app(target=on_page_ready, view=ft.AppView.FLET_APP)

if __name__ == "__main__":
    main()
