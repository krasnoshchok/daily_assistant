import customtkinter as ctk
from Modules.SortPituresTab.SortPicturesTab import SortPicturesTab
from Modules.ConfigManagerTab.ConfigManagerTab import ConfigManagerTab
from Modules.ChatBotTab.ChatBotTab import ChatBotTab

class DailyAssistant(ctk.CTk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Keyboard shortcuts
        self.bind_all('<Alt-a>', lambda event: self.show_module("Sort Pictures"))
        self.bind_all('<Alt-s>', lambda event: self.show_module("Placeholder"))
        self.bind_all('<Alt-d>', lambda event: self.show_module("Chatbot"))
        self.bind_all('<Escape>', lambda event: self.show_home())

        # Configure window
        self.title("Daily Assistant - Your Personal Helper")
        self.geometry("1200x900")

        # Create sidebar
        self.create_sidebar()

        # Main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Show home screen
        self.show_home()

    def create_sidebar(self):
        """Create sidebar with navigation"""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack_propagate(False)
        self.sidebar_frame.pack(side="left", fill="y")

        # Title
        title_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Daily Assistant",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(30, 5))

        subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Your Personal Helper",
            font=ctk.CTkFont(size=11)
        )
        subtitle_label.pack(pady=(0, 30))

        # Navigation buttons
        self.nav_btn_1 = ctk.CTkButton(
            self.sidebar_frame,
            text="Sort Pictures",
            command=lambda: self.show_module("Sort Pictures"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.nav_btn_1.pack(fill="x", padx=10, pady=5)

        self.nav_btn_2 = ctk.CTkButton(
            self.sidebar_frame,
            text="Placeholder",
            command=lambda: self.show_module("Placeholder"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.nav_btn_2.pack(fill="x", padx=10, pady=5)

        self.nav_btn_3 = ctk.CTkButton(
            self.sidebar_frame,
            text="Chatbot",
            command=lambda: self.show_module("Chatbot"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        self.nav_btn_3.pack(fill="x", padx=10, pady=5)

        # Appearance mode at bottom
        self.appearance_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Appearance Mode:",
            anchor="w"
        )
        self.appearance_label.pack(side="bottom", padx=20, pady=(10, 0))

        self.appearance_option = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark"],
            command=self.change_appearance_mode
        )
        self.appearance_option.pack(side="bottom", padx=20, pady=(0, 20))
        self.appearance_option.set("Light")

    def clear_main_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        """Show home/welcome screen"""
        self.clear_main_frame()

        welcome_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        welcome_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Header
        header = ctk.CTkLabel(
            welcome_frame,
            text="Welcome to Daily Assistant",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(pady=(20, 10))

        description = ctk.CTkLabel(
            welcome_frame,
            text="Your personal helper for daily tasks",
            font=ctk.CTkFont(size=15)
        )
        description.pack(pady=(0, 40))

        # Feature buttons
        btn_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        btn_frame.pack(expand=True, fill="both")
        btn_frame.columnconfigure((0, 1, 2), weight=1, uniform="column")
        btn_frame.rowconfigure(0, weight=1)

        # Sort Pictures button
        sort_btn = ctk.CTkButton(
            btn_frame,
            text="📸\n\nSort Pictures",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=100,
            height=150,
            corner_radius=10,
            command=lambda: self.show_module("Sort Pictures")
        )
        sort_btn.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        # Placeholder button
        config_btn = ctk.CTkButton(
            btn_frame,
            text="⚙️\n\nPlaceholder",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=100,
            height=150,
            corner_radius=10,
            command=lambda: self.show_module("Placeholder")
        )
        config_btn.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")

        # Chatbot button
        chat_btn = ctk.CTkButton(
            btn_frame,
            text="💬\n\nChatbot",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=100,
            height=150,
            corner_radius=10,
            command=lambda: self.show_module("Chatbot")
        )
        chat_btn.grid(row=0, column=2, padx=15, pady=10, sticky="nsew")

        # Shortcuts info
        shortcuts_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        shortcuts_frame.pack(side="bottom", fill="x", pady=20)

        shortcuts_label = ctk.CTkLabel(
            shortcuts_frame,
            text="⌨️ Keyboard Shortcuts: Alt+A = Sort Pictures | Alt+S = Placeholder | Alt+D = Chatbot | ESC = Home",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        shortcuts_label.pack()

    def show_module(self, module_name):
        """Show selected module"""
        self.clear_main_frame()

        # Create header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))

        header = ctk.CTkLabel(
            header_frame,
            text=module_name,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(anchor="w")

        separator = ctk.CTkFrame(self.main_frame, height=2, fg_color=("gray75", "gray25"))
        separator.pack(fill="x", padx=20, pady=(10, 0))

        # Content area
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=0, pady=0)

        # Load appropriate module
        if module_name == "Sort Pictures":
            SortPicturesTab(content_frame)
        elif module_name == "Placeholder":
            ConfigManagerTab(content_frame)
        elif module_name == "Chatbot":
            ChatBotTab(content_frame)

    @staticmethod
    def change_appearance_mode(new_mode):
        """Change appearance mode"""
        ctk.set_appearance_mode(new_mode)


def main():
    """Main entry point"""
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = DailyAssistant()
    app.mainloop()


if __name__ == "__main__":
    main()

