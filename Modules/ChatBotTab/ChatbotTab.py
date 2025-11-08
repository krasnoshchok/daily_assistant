import tkinter as tk
import customtkinter as ctk
import threading


class ChatBotTab:
    """Tab for AI chatbot using a local transformers model"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.chat_history = []
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self.create_widgets()

        # Load model in background
        threading.Thread(target=self.load_model, daemon=True).start()

    def create_widgets(self):
        # Main container with a colored background
        main_container = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Status bar at the top
        status_frame = ctk.CTkFrame(main_container, height=50)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="⏳ Loading AI model... (this may take a minute on first run)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="orange"
        )
        self.status_label.pack(expand=True)

        # Chat history area with scroll
        history_container = ctk.CTkFrame(main_container, fg_color=("gray85", "gray20"))
        history_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Scrollable frame for messages
        self.chat_canvas = tk.Canvas(
            history_container,
            bg=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1] if ctk.get_appearance_mode() == "Dark" else
            ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0],
            highlightthickness=0
        )
        scrollbar = ctk.CTkScrollbar(history_container, command=self.chat_canvas.yview)
        self.chat_frame = ctk.CTkFrame(self.chat_canvas, fg_color="transparent")

        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )

        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw", width=800)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        self.chat_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=10)

        # Add a welcome message
        self.add_bot_message(
            "Hello! I'm your AI Assistant. 👋\n\n"
            "I'm powered by a local AI model running on your computer - "
            "no internet connection or API keys required!\n\n"
            "Please wait while I load the AI model...\n\n"
            "Once loaded, I can help you with:\n"
            "• Answering questions\n"
            "• General conversation\n"
            "• Providing information\n"
            "• Writing assistance"
        )

        # Input area
        input_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        input_frame.pack(fill=tk.X)

        # Entry and buttons row
        entry_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        entry_row.pack(fill=tk.X)

        self.chat_entry = ctk.CTkEntry(
            entry_row,
            placeholder_text="Type your message here and press Enter...",
            height=50,
            font=ctk.CTkFont(size=14),
            border_width=2
        )
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.chat_entry.bind("<Return>", lambda e: self.send_message())

        button_frame = ctk.CTkFrame(entry_row, fg_color="transparent")
        button_frame.pack(side=tk.RIGHT)

        self.send_button = ctk.CTkButton(
            button_frame,
            text="Send",
            width=100,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.send_message,
            state="disabled"
        )
        self.send_button.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear",
            width=80,
            height=50,
            font=ctk.CTkFont(size=14),
            command=self.clear_chat,
            fg_color="gray40",
            hover_color="gray30"
        )
        self.clear_button.pack(side=tk.LEFT)

    def load_model(self):
        """Load the AI model in the background with optimizations"""
        try:
            self.parent_frame.after(0, self.update_status, "⏳ Installing required libraries...", "orange")

            # Import required libraries
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                import torch
            except ImportError:
                self.parent_frame.after(0, self.show_install_instructions)
                return

            self.parent_frame.after(0, self.update_status, "⏳ Loading AI model...", "orange")

            # OPTIMIZATION 1: Use the smaller "small" model instead of "medium"
            # This is 3x smaller and loads much faster!
            model_name = "microsoft/DialoGPT-small"

            # OPTIMIZATION 2: Use low_cpu_mem_usage to reduce memory overhead during loading
            # OPTIMIZATION 3: Load with torch_dtype=torch.float32 explicitly (or float16 if you have GPU)
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                padding_side='left',
                use_fast=True  # Use fast tokenizer implementation
            )

            # Check if CUDA is available for faster inference
            device = "cuda" if torch.cuda.is_available() else "cpu"

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                low_cpu_mem_usage=True,  # Reduces memory usage during loading
                dtype=torch.float16 if device == "cuda" else torch.float32
            )

            # Move a model to the appropriate device
            self.model.to(device)

            # OPTIMIZATION 4: Set model to evaluation mode (disables dropout, etc.)
            self.model.eval()

            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model_loaded = True
            self.device = device

            status_msg = "✅ AI model ready! Start chatting below."
            if device == "cuda":
                status_msg += " (GPU acceleration enabled)"

            self.parent_frame.after(0, self.update_status, status_msg, "green")
            self.parent_frame.after(0, self.enable_chat)
            self.parent_frame.after(0, self.add_bot_message,
                                    "AI model loaded successfully! I'm ready to chat. 🎉")

        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            self.parent_frame.after(0, self.update_status, f"❌ {error_msg}", "red")
            self.parent_frame.after(0, self.add_error_message, error_msg)

    def show_install_instructions(self):
        """Show installation instructions"""
        instructions = (
            "Required libraries not found!\n\n"
            "Please install by running:\n"
            "pip install transformers torch\n\n"
            "Then restart the application."
        )
        self.add_error_message(instructions)
        self.update_status("❌ Libraries not installed", "red")

    def update_status(self, message, color):
        """Update status label"""
        self.status_label.configure(text=message, text_color=color)

    def enable_chat(self):
        """Enable chat input"""
        self.send_button.configure(state="normal")
        self.chat_entry.configure(state="normal")
        self.chat_entry.focus()

    def add_user_message(self, message):
        """Add user message bubble"""
        # Message container (right-aligned)
        msg_container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_container.pack(fill=tk.X, padx=10, pady=5)

        # Inner frame for the message bubble (right side)
        bubble_frame = ctk.CTkFrame(msg_container, fg_color="transparent")
        bubble_frame.pack(anchor="e", padx=(100, 0))

        # User label
        label_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
        label_frame.pack(anchor="e", pady=(0, 2))

        user_label = ctk.CTkLabel(
            label_frame,
            text="You",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1e88e5"
        )
        user_label.pack(anchor="e")

        # Message bubble
        bubble = ctk.CTkFrame(
            bubble_frame,
            fg_color=("#2196F3", "#1565C0"),
            corner_radius=15
        )
        bubble.pack(anchor="e")

        msg_label = ctk.CTkLabel(
            bubble,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=500,
            justify="left",
            text_color="white"
        )
        msg_label.pack(padx=15, pady=10)

        # Auto scroll
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def add_bot_message(self, message):
        """Add bot message bubble"""
        # Message container (left-aligned)
        msg_container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_container.pack(fill=tk.X, padx=10, pady=5)

        # Inner frame for the message bubble (left side)
        bubble_frame = ctk.CTkFrame(msg_container, fg_color="transparent")
        bubble_frame.pack(anchor="w", padx=(0, 100))

        # Bot label
        label_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
        label_frame.pack(anchor="w", pady=(0, 2))

        bot_label = ctk.CTkLabel(
            label_frame,
            text="Assistant",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4caf50"
        )
        bot_label.pack(anchor="w")

        # Message bubble
        bubble = ctk.CTkFrame(
            bubble_frame,
            fg_color=("gray70", "gray30"),
            corner_radius=15
        )
        bubble.pack(anchor="w")

        msg_label = ctk.CTkLabel(
            bubble,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=500,
            justify="left",
            text_color=("gray10", "gray90")
        )
        msg_label.pack(padx=15, pady=10)

        # Auto scroll
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def add_error_message(self, message):
        """Add error message bubble"""
        msg_container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_container.pack(fill=tk.X, padx=10, pady=5)

        bubble = ctk.CTkFrame(
            msg_container,
            fg_color=("#ffebee", "#c62828"),
            corner_radius=10
        )
        bubble.pack(anchor="center")

        error_label = ctk.CTkLabel(
            bubble,
            text="⚠️ " + message,
            font=ctk.CTkFont(size=12),
            wraplength=600,
            justify="center",
            text_color=("#c62828", "white")
        )
        error_label.pack(padx=15, pady=10)

        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def show_typing_indicator(self):
        """Show typing indicator"""
        self.typing_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.typing_frame.pack(fill=tk.X, padx=10, pady=5)

        bubble_frame = ctk.CTkFrame(self.typing_frame, fg_color="transparent")
        bubble_frame.pack(anchor="w", padx=(0, 100))

        bubble = ctk.CTkFrame(
            bubble_frame,
            fg_color=("gray70", "gray30"),
            corner_radius=15
        )
        bubble.pack(anchor="w")

        typing_label = ctk.CTkLabel(
            bubble,
            text="● ● ●  typing...",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="gray"
        )
        typing_label.pack(padx=15, pady=10)

        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def remove_typing_indicator(self):
        """Remove typing indicator"""
        if hasattr(self, 'typing_frame'):
            self.typing_frame.destroy()
            delattr(self, 'typing_frame')

    def clear_chat(self):
        """Clear chat history"""
        self.chat_history = []

        # Clear all messages
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

        self.add_bot_message("Chat cleared! How can I help you? 😊")

    def send_message(self):
        """Send the user message and get bot response"""
        message = self.chat_entry.get().strip()

        if not message:
            return

        if not self.model_loaded:
            self.add_error_message("Please wait for the AI model to load first!")
            return

        # Clear entry
        self.chat_entry.delete(0, tk.END)

        # Add a user message
        self.add_user_message(message)

        # Disable input
        self.send_button.configure(state="disabled")
        self.chat_entry.configure(state="disabled")
        self.clear_button.configure(state="disabled")

        # Show typing indicator
        self.show_typing_indicator()

        # Get response in thread
        threading.Thread(target=self.get_bot_response, args=(message,), daemon=True).start()

    def get_bot_response(self, user_message):
        """Generate response using the AI model"""
        try:
            import torch

            # Add a user message to history
            self.chat_history.append(user_message)

            # Keep only the last 10 messages
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]

            # Encode conversation
            bot_input_ids = self.tokenizer.encode(
                " ".join(self.chat_history) + self.tokenizer.eos_token,
                return_tensors='pt'
            ).to(self.device)

            # Generate response with optimized settings
            with torch.no_grad():
                chat_history_ids = self.model.generate(
                    bot_input_ids,
                    max_length=1000,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3,
                    do_sample=True,
                    top_k=50,
                    top_p=0.95,
                    temperature=0.7,
                    num_beams=1  # Faster than beam search
                )

            # Decode response
            response = self.tokenizer.decode(
                chat_history_ids[:, bot_input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )

            # Clean-up response
            response = response.strip()
            if not response:
                response = "I'm not sure how to respond to that. Could you rephrase?"

            # Add to history
            self.chat_history.append(response)

            # Update UI
            self.parent_frame.after(0, self.display_response, response)

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.parent_frame.after(0, self.display_error, error_msg)

    def display_response(self, response):
        """Display bot response in UI"""
        self.remove_typing_indicator()
        self.add_bot_message(response)

        # Re-enable input
        self.send_button.configure(state="normal")
        self.chat_entry.configure(state="normal")
        self.clear_button.configure(state="normal")
        self.chat_entry.focus()

    def display_error(self, error_message):
        """Display error in UI"""
        self.remove_typing_indicator()
        self.add_error_message(error_message)

        # Re-enable input
        self.send_button.configure(state="normal")
        self.chat_entry.configure(state="normal")
        self.clear_button.configure(state="normal")
        self.chat_entry.focus()