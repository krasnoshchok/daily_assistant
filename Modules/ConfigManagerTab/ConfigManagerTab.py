import tkinter as tk
import customtkinter as ctk


class ConfigManagerTab:
    """Tab for placeholder"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_container = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Center frame for content
        center_frame = ctk.CTkFrame(main_container)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Icon/emoji
        icon_label = ctk.CTkLabel(
            center_frame,
            text="⚙️",
            font=ctk.CTkFont(size=80)
        )
        icon_label.pack(pady=(20, 10))

        # Title
        title_label = ctk.CTkLabel(
            center_frame,
            text="Placeholder",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            center_frame,
            text="Coming Soon",
            font=ctk.CTkFont(size=16),
            text_color=("gray50", "gray60")
        )
        subtitle_label.pack(pady=(0, 20))

        # Description
        desc_label = ctk.CTkLabel(
            center_frame,
            text="This is just a placeholder.",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray70")
        )
        desc_label.pack(pady=(0, 20))
