import threading
from tkinter import *
from tkinter import scrolledtext
from openai import OpenAI


class ChinaCityGuide:
    def __init__(self):
        self.window = Tk()
        self.window.title("China City Guide")
        self.window.geometry("700x850")

        self.font = ("Arial", 12)
        self.title_font = ("Arial", 16, "bold")

        self.client = OpenAI(
            api_key="**********************",
            base_url="https://api.deepseek.com"
        )

        self.user_info = {}
        self.current_step = 0

        self.questions = [
            {"key": "age", "text": "What is your age?", "type": "input", "options": []},
            {"key": "companions", "text": "Who will you travel with?", "type": "buttons",
             "options": ["Travel alone", "Family", "Partner", "Friends"]},
            {"key": "interests", "text": "Which type of trip are you interested in the most?", "type": "buttons",
             "options": ["Culture and History", "Natural Scenery", "Foodie", "Shopping", "Night life"]},
            {"key": "city", "text": "Which city would you like to visit?", "type": "buttons",
             "options": ["Beijing", "Shang Hai", "Guang Zhou", "Cheng Du", "Xi An", "Hang Zhou", "Shen Zhen", "Su Zhou"]},
            {"key": "duration", "text": "How long is your trip?", "type": "buttons",
             "options": ["1-2 days", "3-4 days", "5-7 days", "More than a week"]}
        ]

        self.setup_gui()

    def setup_gui(self):
        # Title
        Label(self.window, text="China City Guide", font=self.title_font).pack(pady=10)
        Label(self.window, text="Welcome! I will recommend the best city attractions and travel routes for you.",
              font=self.font, bg="#FFFFFF").pack(pady=5)

        # Chat area
        chat_frame = Frame(self.window)
        chat_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.chat_display = scrolledtext.ScrolledText(chat_frame, font=self.font, wrap=WORD, state=DISABLED, height=12)
        self.chat_display.pack(fill=BOTH, expand=True)

        # Color tags for messages
        self.chat_display.tag_config("user", foreground="#0066CC")
        self.chat_display.tag_config("guide", foreground="#4CAF50")
        self.chat_display.tag_config("error", foreground="#FF0000")

        # Input frame
        self.input_frame = Frame(self.window, height=50)
        self.input_frame.pack(fill=X, padx=10, pady=5)

        Label(self.input_frame, text="Input:", font=self.font).pack(side=LEFT, pady=5)

        self.user_entry = Entry(self.input_frame, font=self.font)
        self.user_entry.pack(side=LEFT, fill=X, expand=True, padx=5, pady=5)
        self.user_entry.bind("<Return>", lambda event: self.send_message())

        Button(self.input_frame, text="Send", font=self.font, command=self.send_message,
               bg="#4CAF50", fg="white", activebackground="#45A049", borderwidth=0).pack(side=RIGHT, padx=5, pady=5)

        # Options frame
        self.options_frame = Frame(self.window, bg=self.window.cget("bg"))
        self.options_frame.pack(fill=X, padx=10, pady=10)

        self.ask_next_question()

    def clear_options_frame(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def show_option_buttons(self, options):
        self.clear_options_frame()
        self.input_frame.pack_forget()

        for i, opt in enumerate(options):
            btn = Button(self.options_frame, text=opt, font=self.font,
                         command=lambda o=opt: self.select_option(o),
                         bg="#2196F3", fg="white", activebackground="#1976D2", borderwidth=0, padx=10, pady=5)
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="ew")

        for col in range(3):
            self.options_frame.grid_columnconfigure(col, weight=1)

    def add_message(self, sender, message, tag):
        self.chat_display.config(state=NORMAL)
        self.chat_display.insert(END, f"{sender}: {message}\n\n", tag)
        self.chat_display.config(state=DISABLED)
        self.chat_display.see(END)

    def show_text_input(self):
        self.clear_options_frame()
        self.input_frame.pack(fill=X, padx=10, pady=5)
        self.user_entry.focus()

    def select_option(self, option):
        self.add_message("You", option, "user")
        if self.current_step < len(self.questions):
            q = self.questions[self.current_step]
            self.user_info[q["key"]] = option
            self.current_step += 1
            self.ask_next_question()

    def ask_next_question(self):
        if self.current_step < len(self.questions):
            q = self.questions[self.current_step]
            self.add_message("Guide", q["text"], "guide")
            if q["type"] == "input":
                self.show_text_input()
            else:
                self.show_option_buttons(q["options"])
        else:
            self.generate_attraction_recommendations()

    def send_message(self):
        text = self.user_entry.get().strip()
        if not text:
            return
        if text.lower() in ["quit", "exit", "q"]:
            self.window.quit()
            return
        self.user_entry.delete(0, END)
        self.add_message("You", text, "user")
        if self.current_step < len(self.questions):
            q = self.questions[self.current_step]
            self.user_info[q["key"]] = text
            self.current_step += 1
            self.ask_next_question()

    def generate_attraction_recommendations(self):
        self.clear_options_frame()
        self.input_frame.pack_forget()
        self.add_message("Guide", "Great! Let me recommend the best attractions and travel routes for you...", "guide")
        threading.Thread(target=self.get_ai_response, daemon=True).start()

    def get_ai_response(self):
        try:
            context = f"""
Age: {self.user_info.get('age', 'Not provided')}
Companions: {self.user_info.get('companions', 'Not provided')}
Interests: {self.user_info.get('interests', 'Not provided')}
Target City: {self.user_info.get('city', 'Not provided')}
Trip Duration: {self.user_info.get('duration', 'Not provided')}
"""
            system_prompt = """You are a professional China travel guide. Respond in English.
Provide detailed personalized recommendations including:
1. Brief city introduction
2. 6-8 attractions with details (features, visiting time, tickets, best time)
3. Day-by-day itinerary
4. Local food
5. Transportation tips
6. Best season and notes
Be warm and professional."""
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Recommend for:\n{context}"}
                ],
                stream=False
            )
            self.window.after(0, lambda: self.handle_ai_response(response.choices[0].message.content))
        except Exception as e:
            self.window.after(0, lambda: self.handle_ai_response(f"Error: {e}", is_error=True))

    def handle_ai_response(self, message, is_error=False):
        tag = "error" if is_error else "guide"
        sender = "Error" if is_error else "Guide"
        self.add_message(sender, message, tag)
        if not is_error:
            self.add_message("Guide", "Would you like to inquire about another city?", "guide")
            self.show_restart_buttons()

    def show_restart_buttons(self):
        self.clear_options_frame()
        Button(self.options_frame, text="Restart", font=self.font, command=self.restart_session,
               bg="#4CAF50", fg="white", padx=10, pady=5).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        Button(self.options_frame, text="Exit", font=self.font, command=self.window.quit,
               bg="#f44336", fg="white", padx=10, pady=5).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(1, weight=1)

    def restart_session(self):
        self.user_info = {}
        self.current_step = 0
        self.add_message("You", "Restart", "user")
        self.add_message("Guide", "Let's start over! I will recommend new city attractions for you.", "guide")
        self.ask_next_question()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = ChinaCityGuide()
    app.run()