import customtkinter as ctk
from tkinter import filedialog, Canvas
from tkinterdnd2 import DND_FILES
import re
import os
import sys
from PIL import Image
import platform

MAX_FILE_SIZE = 1 * 1024 * 1024

def resource_path(relative_path):
    """ Get absolute path to resource for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ==============================================
# CONFIGURE THESE PATHS TO YOUR IMAGE FILES
# ==============================================
DOWNLOAD_ICON_PATH = resource_path(os.path.join('assets', 'download.png'))
DELETE_ICON_PATH = resource_path(os.path.join('assets', 'delete.png'))
DRAG_DROP_ICON_PATH = resource_path(os.path.join('assets', 'upload.png'))
APP_ICON_PATH = resource_path(os.path.join('assets', 'icon.ico'))
# ==============================================

class M3UPlaylistGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(APP_ICON_PATH)
        self.title("M3U Playlist Generator")
        self.geometry("725x240")
        self.resizable(False, False)
        self.configure_theme()
        self.load_images()
        self.setup_ui()
        
    def configure_theme(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        self.text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        
    def load_images(self):
        try:
            self.download_icon = ctk.CTkImage(Image.open(DOWNLOAD_ICON_PATH), size=(30, 30))
            self.delete_icon = ctk.CTkImage(Image.open(DELETE_ICON_PATH), size=(30, 30))
            self.drag_drop_icon = ctk.CTkImage(Image.open(DRAG_DROP_ICON_PATH), size=(120, 120))
        except Exception as e:
            print(f"Image loading error: {e}")
            self.download_icon = self.delete_icon = self.drag_drop_icon = None

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure columns for equal width split
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=12)
    
        # Left drop frame (fixed width, flexible height)
        drop_frame = ctk.CTkFrame(main_frame, width=160, height=100)
        drop_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        self.create_drag_drop_area(drop_frame)
    
        # Right list frame (flexible width, same height)
        list_frame = ctk.CTkFrame(main_frame, height=100)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        self.create_scrollable_list(list_frame)

        # Status Bar
        self.status_label = ctk.CTkLabel(self, padx=5,text="Ready", anchor="w",
                                       font=("Arial", 10), height=24)
        self.status_label.pack(side="bottom", fill="x")

        # Drag & Drop setup
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_file_drop)
    
    # Scrollable List
    def update_scrollbar_visibility(self):
        self.scrollable_frame.update_idletasks()
        # Get height of the scrollable content
        content_height = self.scrollable_frame.winfo_reqheight()
        # Get visible height of the canvas
        visible_height = self.canvas.winfo_height()

        if content_height > visible_height:
            # Show scrollbar
            self.scrollbar.pack(side="right", fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.scroll_enabled = True
            
        else:
            # Hide scrollbar
            self.scrollbar.pack_forget()
            self.canvas.yview_moveto(0)
            self.canvas.configure(yscrollcommand=lambda *args: None)
            self.scroll_enabled = False
            
    def create_scrollable_list(self, parent):
        self.canvas = Canvas(parent, highlightthickness=0, bg=self.bg_color[1])
        self.canvas.pack(side="left",fill="both",expand=True)
        self.scrollbar = ctk.CTkScrollbar(parent, command=self.canvas.yview,width=12)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")

        self.scrollable_frame.bind("<Configure>", 
                                 lambda e: self.canvas.configure(
                                     scrollregion=self.canvas.bbox("all")
                                 ))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        system = platform.system()

        if system == "Windows":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        elif system == "Darwin":  # MacOS
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:  # Linux
            self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
            self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
    
        
    def _on_mousewheel(self, event):
        if getattr(self, 'scroll_enabled', True):
            system = platform.system()
            if system == "Windows":
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif system == "Darwin":
                self.canvas.yview_scroll(int(-1*event.delta), "units")
            
        
    def create_drag_drop_area(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(expand=True, fill="both")

        # Center container for vertical and horizontal alignment
        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")  # Perfect center

        if self.drag_drop_icon:
            icon = ctk.CTkLabel(center_frame, image=self.drag_drop_icon, text="",justify="center")
        else:
            icon = ctk.CTkLabel(center_frame, text="⬆", font=("Arial", 36))
        icon.pack(pady=(0, 10))


        for widget in [container, icon]:
            widget.bind("<Button-1>", lambda e: self.open_file())

    def handle_file_drop(self, event):
        self.status_label.configure(text=" Ready", text_color="gray")
        file_path = event.data.strip('{}')
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.process_file(file_path)

    def process_file(self, path):
        if not path.lower().endswith(".txt"):
            self.update_status("Please select a .txt file!", "red")
            return
        if os.path.getsize(path) > MAX_FILE_SIZE:
            self.update_status("File too large! Max allowed: 1 MB", "red")
            return
        
        base_name = os.path.splitext(os.path.basename(path))[0]
        output_file = os.path.join(os.path.dirname(path), f"{base_name}.m3u")
        
        success, message = self.create_m3u_playlist(path, output_file)
        if success:
            self.add_file_entry(base_name, output_file)
            self.update_status(f"Added: {base_name}", "green")
            self.update_scrollbar_visibility()
        else:
            self.update_status(message, "red")

    def create_m3u_playlist(self, input_file, output_file):
        try:
            with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
                f_out.write("#EXTM3U\n")
                links = f_in.readlines()
                sorted_links = sorted(links, key=self.extract_episode_number)
                for link in sorted_links:
                    if link.strip():
                        episode = link.split('/')[-1].removesuffix('.mkv')
                        f_out.write(f"#EXTINF:-1,{episode}\n{link.strip()}\n")
            return True, "Successfully created!"
        except Exception as e:
            return False, f"Error: {e}"

    def extract_episode_number(self, link):
        match = re.search(r"S(\d+)E(\d+)", link, re.IGNORECASE)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return (0, 0)

    def add_file_entry(self, name, output_path):
        entry_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=self.bg_color)
        entry_frame.pack(fill="x", pady=3, padx=5)
        
        entry_frame.grid_columnconfigure(0, weight=1)
        entry_frame.grid_columnconfigure(1, weight=0)
        
        # Truncate long name for display
        display_name = name if len(name) <= 50 else name[:50] + "..."
        
        # Calculate number of spaces to pad
        max_length = 62
        spaces_to_add = max_length - len(display_name)
        if spaces_to_add < 0:
            spaces_to_add = 0

        # Add dynamic spaces at the end
        display_name_padded = display_name + " " * spaces_to_add

        # File name label
        lbl_name = ctk.CTkLabel(
            entry_frame,
            text=display_name_padded,
            font=("Arial", 12),
            anchor="w",
            justify="left"
        )
        lbl_name.grid(row=0, column=0, sticky="we", padx=(10,5))

        # Action buttons container
        btn_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e", padx=(5, 10))
         
        # Download Button
        ctk.CTkButton(
            btn_frame,
            text="",
            image=self.download_icon,
            width=4,
            height=4,
            fg_color="transparent",
            hover_color="#4CAF50",
            command=lambda: self.download_file(output_path)
        ).pack(side="left", padx=(0, 5))

        # Delete Button
        ctk.CTkButton(
            btn_frame,
            text="",
            image=self.delete_icon,
            width=4,
            height=4,
            fg_color="transparent",
            hover_color="#F44336",
            command=lambda: self.delete_file(entry_frame, output_path)
        ).pack(side="left")
        
        

        # Force UI update
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_status(self, message, color="gray"):
        self.status_label.configure(text=message, text_color=color)

    def delete_file(self, frame, path):
        frame.destroy()
        self.update_status(f"Deleted: {os.path.basename(path)}", "orange")
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update_scrollbar_visibility()

    def download_file(self, path):
        self.update_status(f"Downloaded: {os.path.basename(path)}", "blue")

    def open_file(self):
        if path := filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")]):
            self.process_file(path)
        else:
            self.update_status("No file selected!", "red")

if __name__ == "__main__":
    app = M3UPlaylistGenerator()
    app.mainloop()
