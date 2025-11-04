import customtkinter as ctk
import subprocess
import sys
import time
import threading
import os
import sys
from main import TuneTransfer

# Initialize customtkinter appearance
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue") 

class ThreadSafeRedirector:
    def __init__(self, textbox: ctk.CTkTextbox):
        self.textbox = textbox

    def write(self, message: str):
        if not message:
            return

        try:
            self.textbox.after(0, lambda: self._append(message))
        except RuntimeError:
            # If widget is destroyed / app closed, ignore
            pass

    def _append(self, message: str):
        try:
            self.textbox.configure(state="normal")
            self.textbox.insert("end", message)
            self.textbox.see("end")
            self.textbox.configure("disabled")
        except Exception:
            pass

    def flush(self):
        pass

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Tunes Transfer")
        self.geometry("550x650")
        self.resizable(False, False)
        self.configure(fg_color="#233D96")

        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception as e:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        kalufira_font_path = resource_path(os.path.join('fonts', 'Kalufira.otf'))
        consola_font_path = resource_path(os.path.join('fonts', 'consola.ttf'))
        ctk.FontManager.load_font(kalufira_font_path)
        ctk.FontManager.load_font(consola_font_path)
        icon_path = resource_path(os.path.join('resources', 'logo.ico'))
        self.iconbitmap(default=icon_path)

        # Title Label
        self.title_label = ctk.CTkLabel(
            self, text="Cross-Platform Playlist Transfer",
            font=ctk.CTkFont(family='Kalufira', size=25), text_color='black'
        )
        self.title_label.pack(pady=(10, 10))

        # Input fields
        self.playlist_url_entry  = self._make_entry("Playlist URL here")

        # Radio Buttons
        self.from_platform = self._make_radio_button_row()
        self.to_platform = self._make_radio_button_row()

        # Event Buttons
        frame = ctk.CTkFrame(self, fg_color='transparent')
        frame.pack(pady=13)

        self.run_button = ctk.CTkButton(
            frame, text="transfer!", text_color='black', command=self.run_main_thread, fg_color="#42AF46", font=ctk.CTkFont(family="Kalufira", size=20), height=30, width=130)
        self.run_button.pack(side='top')

        # Output box
        self.output_box = ctk.CTkTextbox(self, height=360, width=500, font=ctk.CTkFont(family="Consolas", size=15))
        self.output_box.pack(pady=(0, 0))
        self.output_box.insert("end", "Output will appear here...\n")

        self.redirect = ThreadSafeRedirector(self.output_box)
        sys.stdout = self.redirect
        sys.stderr = self.redirect

    def _make_entry(self, label_text: str):
        frame = ctk.CTkFrame(self, fg_color='transparent')
        frame.pack(pady=6)

        entry = ctk.CTkEntry(frame, placeholder_text=label_text, height=35, width=400, font=ctk.CTkFont(family="Consolas", size=14))
        entry.pack(side="left")

        return entry

    def _get_entry_output(self, entry: ctk.CTkEntry):
        return entry.get()
    
    def _make_radio_button_row(self):
        selected_platform = ctk.StringVar(value="spotify")  # default

        frame = ctk.CTkFrame(self, fg_color='transparent')
        frame.pack(pady=20)

        # Create radio buttons
        spotify_radio = ctk.CTkRadioButton(frame, text="Spotify", variable=selected_platform,
                                       value="spotify", width=20, height=20, font=ctk.CTkFont(family="Kalufira", size=21), text_color='black')
        spotify_radio.pack(padx=8, side='left')

        yt_radio = ctk.CTkRadioButton(frame, text="YouTube Music", variable=selected_platform,
                                    value="youtube", width=20, height=20, font=ctk.CTkFont(family="Kalufira", size=21), text_color='black')
        yt_radio.pack(padx=8, side='left')

        return selected_platform
    
    def _get_radio_button_value(self, button):
        return button.get()
    

    def run_main(self):
        playlist_url = self._get_entry_output(self.playlist_url_entry)
        from_p = self._get_radio_button_value(self.from_platform)
        to_p = self._get_radio_button_value(self.to_platform)

        if not playlist_url:
            self.output_box.insert("end", "Please enter a playlist URL!\n")
            return
        
        print(f"\nFrom Platform: {from_p}\n")
        print(f"To Platform: {to_p}\n")
        try:
            tune = TuneTransfer(from_p, to_p, playlist_url.strip())
            tune.penetrate()
        except subprocess.CalledProcessError as e:
            self.output_box.insert("end", f"Error:\n{e.stderr}\n")

    def check_thread(self, thread: threading.Thread, start_time):
        if not thread.is_alive():
            self.output_box.insert("end", "\n\n---Playlist transfer process ended---\n")
        elif (time.time() - start_time) > 1200:
            self.output_box.insert("end", "App timeout reached, killing playlist transfer thread!\n")
        else:
            app.after(1000, lambda: self.check_thread(thread, start_time))

    def run_main_thread(self):
        main_thread = threading.Thread(target=self.run_main, daemon=True)
        main_thread.start()
        start_time = time.time()
        self.check_thread(main_thread, start_time)

if __name__ == "__main__":
    app = App()
    app.mainloop()
