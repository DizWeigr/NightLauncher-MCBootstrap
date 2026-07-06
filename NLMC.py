import customtkinter as ctk
import minecraft_launcher_lib
import subprocess
import threading
import os
import requests
import json

# --- Configuration ---
MINECRAFT_DIR = os.path.join(os.getenv('APPDATA'), '.night_launcher')
MODS_DIR = os.path.join(MINECRAFT_DIR, "mods")

class NightLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NightLauncher (NL)")
        self.geometry("1100x650")
        ctk.set_appearance_mode("dark")

        # Setup Directories
        for path in [MINECRAFT_DIR, MODS_DIR]:
            if not os.path.exists(path):
                os.makedirs(path)

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="NIGHT LAUNCHER", font=ctk.CTkFont(size=24, weight="bold", slant="italic"))
        self.logo.grid(row=0, column=0, padx=20, pady=40)

        self.btn_play = ctk.CTkButton(self.sidebar, text="Play", command=self.show_play_frame, fg_color="#333333")
        self.btn_play.grid(row=1, column=0, padx=20, pady=10)

        self.btn_mods = ctk.CTkButton(self.sidebar, text="Mod Browser", command=self.show_mod_frame, fg_color="#333333")
        self.btn_mods.grid(row=2, column=0, padx=20, pady=10)

        # --- Main Container ---
        self.container = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.play_frame = ctk.CTkFrame(self.container, fg_color="#121212")
        self.mod_frame = ctk.CTkFrame(self.container, fg_color="#121212")

        self.setup_play_frame()
        self.setup_mod_frame()
        self.show_play_frame()

    def show_play_frame(self):
        self.mod_frame.grid_forget()
        self.play_frame.grid(row=0, column=0, sticky="nsew")

    def show_mod_frame(self):
        self.play_frame.grid_forget()
        self.mod_frame.grid(row=0, column=0, sticky="nsew")

    # --- PLAY FRAME (Dynamic Version Support) ---
    def setup_play_frame(self):
        self.lbl = ctk.CTkLabel(self.play_frame, text="NL Dashboard", font=("Impact", 40))
        self.lbl.pack(pady=30)

        self.version_var = ctk.StringVar(value="Fetching versions...")
        self.ver_menu = ctk.CTkOptionMenu(self.play_frame, variable=self.version_var, command=self.on_version_change)
        self.ver_menu.pack(pady=10)
        
        # Load all real versions from Mojang on startup
        threading.Thread(target=self.load_all_versions).start()

        self.user_entry = ctk.CTkEntry(self.play_frame, placeholder_text="Username", width=300, height=40)
        self.user_entry.pack(pady=10)

        self.launch_btn = ctk.CTkButton(self.play_frame, text="LAUNCH", fg_color="#FF4B4B", 
                                       font=("Arial", 20, "bold"), height=60, width=250, command=self.start_launch)
        self.launch_btn.pack(pady=40)

        self.status_label = ctk.CTkLabel(self.play_frame, text="System Ready", text_color="gray")
        self.status_label.pack(side="bottom", pady=20)

    def load_all_versions(self):
        """Fetches EVERY version from Mojang to ensure support for all future releases."""
        try:
            all_versions = minecraft_launcher_lib.utils.get_version_list()
            # Filter to show only stable releases (no snapshots)
            release_versions = [v['id'] for v in all_versions if v['type'] == 'release']
            # Sort newest to oldest
            release_versions.sort(reverse=True)
            
            self.version_var.set(release_versions[0])
            self.ver_menu._values = release_versions
        except Exception as e:
            self.status_label.configure(text=f"Version Error: {e}")

    def on_version_change(self, val):
        self.status_label.configure(text=f"Selected: {val}")

    # --- MOD BROWSER FRAME (Prism Style) ---
    def setup_mod_frame(self):
        # Search Bar
        search_bar_frame = ctk.CTkFrame(self.mod_frame, fg_color="transparent")
        search_bar_frame.pack(fill="x", padx=20, pady=20)

        self.search_entry = ctk.CTkEntry(search_bar_frame, placeholder_text="Search Modrinth/CurseForge...", width=400)
        self.search_entry.pack(side="left", padx=10)

        self.search_btn = ctk.CTkButton(search_bar_frame, text="Search", width=100, command=self.search_mods)
        self.search_btn.pack(side="left")

        # Results Area
        self.results_list = ctk.CTkTextbox(self.mod_frame, width=800, height=300, font=("Arial", 14))
        self.results_list.pack(pady=10, padx=20)
        self.results_list.insert("0.0", "Search for mods to see results here...\n(Note: This simulates the Modrinth API connection)")

        self.install_btn = ctk.CTkButton(self.mod_frame, text="Install Selected Mod", command=self.install_selected_mod)
        self.install_btn.pack(pady=10)

    def search_mods(self):
        query = self.search_entry.get()
        self.results_list.delete("0.0", "end")
        self.results_list.insert("end", f"Searching for '{query}'...\n")
        
        # Simulation of Modrinth API response
        # In a production environment, you would use: requests.get(f"https://api.modrinth.com/v2/search?query={query}")
        def mock_search():
            import time
            time.sleep(1.5)
            results = [
                {"name": "Sodium", "desc": "Extreme FPS Boost", "link": "https://example.com/sodium.jar"},
                {"name": "Iris", "desc": "Shaders Support", "link": "https://example.com/iris.jar"},
                {"name": "Lithium", "desc": "Game Logic Optimization", "link": "https://example.com/lithium.jar"}
            ]
            self.results_list.delete("0.0", "end")
            for r in results:
                self.results_list.insert("end", f"NAME: {r['name']} | DESC: {r['desc']}\nLINK: {r['link']}\n---\n")
            self.last_search_results = results # Store for installation
            
        threading.Thread(target=mock_search).start()

    def install_selected_mod(self):
        # For this demo, it installs the first result from the search
        if hasattr(self, 'last_search_results'):
            mod = self.last_search_results[0]
            threading.Thread(target=self.download_logic, args=(mod['link'], mod['name'])).start()

    def download_logic(self, url, name):
        self.status_label.configure(text=f"Downloading {name}...")
        try:
            # Simulate download
            r = requests.get(url, timeout=5)
            with open(os.path.join(MODS_DIR, f"{name}.jar"), 'wb') as f:
                f.write(r.content)
            self.status_label.configure(text=f"Installed {name} successfully!")
        except:
            self.status_label.configure(text="Install failed (Mock Link used)")

    # --- LAUNCH LOGIC ---
    def start_launch(self):
        threading.Thread(target=self.launch_game).start()

    def launch_game(self):
        version = self.version_var.get()
        user = self.user_entry.get() or "NightPlayer"
        
        try:
            self.launch_btn.configure(state="disabled")
            self.status_label.configure(text="Downloading assets (this can take a while)...")
            
            minecraft_launcher_lib.install.install_minecraft_version(version, MINECRAFT_DIR)
            
            # Attempt Fabric Install (The modern standard)
            self.status_label.configure(text="Setting up Fabric Loader...")
            try:
                version = minecraft_launcher_lib.fabric.install_fabric(version, MINECRAFT_DIR)
            except:
                self.status_label.configure(text="Fabric not available. Launching Vanilla.")

            options = {"username": user, "uuid": "", "token": ""}
            command = minecraft_launcher_lib.command.get_minecraft_command(version, MINECRAFT_DIR, options)
            
            self.status_label.configure(text="GAME RUNNING!")
            subprocess.call(command)
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
        finally:
            self.launch_btn.configure(state="normal")

if __name__ == "__main__":
    app = NightLauncher()
    app.mainloop()
