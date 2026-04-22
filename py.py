import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
from pathlib import Path
import datetime
import json
import threading
import time
import random
import subprocess
import webbrowser

# ============================================
# کلاس اصلی سیستم عامل
# ============================================
class PyOSComplete:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyOS 98")
        self.root.geometry("1024x768")
        
        # متغیرهای سیستم
        self.desktop_path = Path.home() / "Desktop"
        self.pyos_home = self.desktop_path / "PyOS_System"
        self.pyos_home.mkdir(exist_ok=True)
        
        # زیرپوشه‌های سیستم
        self.users_dir = self.pyos_home / "Users"
        self.settings_dir = self.pyos_home / "Settings"
        self.temp_dir = self.pyos_home / "Temp"
        for d in [self.users_dir, self.settings_dir, self.temp_dir]:
            d.mkdir(exist_ok=True)
        
        self.current_path = self.pyos_home / "Users"
        self.settings_file = self.settings_dir / "config.json"
        
        # وضعیت سیستم
        self.current_user = None
        self.clipboard = None
        self.idle_seconds = 0
        self.screensaver_active = False
        self.drag_data = {"widget": None, "x": 0, "y": 0}
        self.running_tasks = []
        self.desktop_icons = []
        
        # بارگذاری تنظیمات
        self.settings = self.load_settings()
        
        # رنگ‌های تم
        self.colors = {
            "bg_dark": "#616166",
            "bg_medium": "#505152",
            "bg_light": "#d45757",
            "accent": "#e94560",
            "success": "#00ff88",
            "text": "#ffffff"
        }
        
        # راه‌اندازی UI
        self.setup_login_screen()
        
    # ============================================
    # سیستم مدیریت کاربران
    # ============================================
    def load_settings(self):
        default = {
            "theme": "dark",
            "auto_screensaver": 60,
            "users": {"admin": {"password": "admin123", "type": "admin"}}
        }
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return {**default, **json.load(f)}
            except:
                return default
        return default
    
    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2)
    
    def setup_login_screen(self):
        self.clear_window()
        self.root.configure(bg=self.colors["bg_dark"])
        
        login_frame = tk.Frame(self.root, bg=self.colors["bg_medium"], width=400, height=350)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        login_frame.pack_propagate(False)
        
        # عنوان
        tk.Label(login_frame, text="PyOS", font=("Arial", 28, "bold"),
                bg=self.colors["bg_medium"], fg=self.colors["success"]).pack(pady=20)
        
        tk.Label(login_frame, text="Operating System", font=("Arial", 10),
                bg=self.colors["bg_medium"], fg=self.colors["text"]).pack()
        
        # فرم لاگین
        form_frame = tk.Frame(login_frame, bg=self.colors["bg_medium"])
        form_frame.pack(pady=30)
        
        tk.Label(form_frame, text="Username:", bg=self.colors["bg_medium"], 
                fg=self.colors["text"], font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        username_entry = tk.Entry(form_frame, bg=self.colors["bg_light"], fg=self.colors["text"],
                                  font=("Arial", 11), insertbackground=self.colors["text"])
        username_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Password:", bg=self.colors["bg_medium"], 
                fg=self.colors["text"], font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        password_entry = tk.Entry(form_frame, bg=self.colors["bg_light"], fg=self.colors["text"],
                                  font=("Arial", 11), show="•", insertbackground=self.colors["text"])
        password_entry.grid(row=1, column=1, pady=5, padx=10)
        
        def login():
            username = username_entry.get()
            password = password_entry.get()
            
            if username in self.settings["users"]:
                if self.settings["users"][username]["password"] == password:
                    self.current_user = username
                    self.user_folder = self.users_dir / username
                    self.user_folder.mkdir(exist_ok=True)
                    (self.user_folder / "Documents").mkdir(exist_ok=True)
                    (self.user_folder / "Desktop").mkdir(exist_ok=True)
                    (self.user_folder / "Downloads").mkdir(exist_ok=True)
                    (self.user_folder / "Pictures").mkdir(exist_ok=True)
                    self.current_path = self.user_folder / "Desktop"
                    self.setup_main_ui()
                    return
            
            messagebox.showerror("Login Failed", "Invalid username or password")
        
        def create_account():
            dialog = tk.Toplevel(self.root)
            dialog.title("Create Account")
            dialog.geometry("300x200")
            dialog.configure(bg=self.colors["bg_medium"])
            
            tk.Label(dialog, text="New Username:", bg=self.colors["bg_medium"], 
                    fg=self.colors["text"]).pack(pady=5)
            new_user_entry = tk.Entry(dialog, bg=self.colors["bg_light"], fg=self.colors["text"])
            new_user_entry.pack(pady=5)
            
            tk.Label(dialog, text="Password:", bg=self.colors["bg_medium"], 
                    fg=self.colors["text"]).pack(pady=5)
            new_pass_entry = tk.Entry(dialog, bg=self.colors["bg_light"], fg=self.colors["text"], show="•")
            new_pass_entry.pack(pady=5)
            
            def save_user():
                username = new_user_entry.get()
                password = new_pass_entry.get()
                if username and password:
                    self.settings["users"][username] = {"password": password, "type": "user"}
                    self.save_settings()
                    messagebox.showinfo("Success", f"Account '{username}' created!")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "All fields are required")
            
            tk.Button(dialog, text="Create", command=save_user,
                     bg=self.colors["success"], fg=self.colors["bg_dark"],
                     font=("Arial", 10, "bold"), width=15).pack(pady=20)
            
            new_user_entry.focus()
        
        # دکمه‌ها
        btn_frame = tk.Frame(login_frame, bg=self.colors["bg_medium"])
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Login", command=login,
                 bg=self.colors["success"], fg=self.colors["bg_dark"],
                 font=("Arial", 11, "bold"), width=15).pack(pady=5)
        tk.Button(btn_frame, text="Create Account", command=create_account,
                 bg=self.colors["accent"], fg=self.colors["text"],
                 font=("Arial", 10), width=15).pack(pady=5)
        
        username_entry.focus()
        self.root.bind('<Return>', lambda e: login())
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ============================================
    # رابط کاربری اصلی
    # ============================================
    def setup_main_ui(self):
        self.clear_window()
        self.root.configure(bg=self.colors["bg_dark"])
        
        # Desktop Canvas
        self.desktop_canvas = tk.Canvas(self.root, bg=self.colors["bg_dark"], highlightthickness=0)
        self.desktop_canvas.pack(fill=tk.BOTH, expand=True)
        
        # ایجاد گرادیان ساده برای پس‌زمینه
        self.create_desktop_background()
        
        # Taskbar
        self.taskbar = tk.Frame(self.root, bg=self.colors["bg_light"], height=45)
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Start Button
        start_btn = tk.Button(self.taskbar, text=" PyOS Start ", bg=self.colors["accent"], 
                             fg=self.colors["text"], font=("Arial", 10, "bold"), 
                             command=self.show_start_menu)
        start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Quick Launch
        quick_launch = tk.Frame(self.taskbar, bg=self.colors["bg_light"])
        quick_launch.pack(side=tk.LEFT, padx=10)
        
        apps = [
            ("🌐", self.open_browser),
            ("📁", self.open_file_manager),
            ("📝", self.open_notepad),
            ("🎮", self.open_snake_game),
        ]
        for icon, cmd in apps:
            btn = tk.Button(quick_launch, text=icon, bg=self.colors["bg_light"], 
                           fg=self.colors["text"], font=("Arial", 14), 
                           command=cmd, width=3)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Running Tasks Area
        self.taskbar_tasks = tk.Frame(self.taskbar, bg=self.colors["bg_light"])
        self.taskbar_tasks.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # System Tray
        sys_tray = tk.Frame(self.taskbar, bg=self.colors["bg_light"])
        sys_tray.pack(side=tk.RIGHT, padx=10)
        
        self.clock_label = tk.Label(sys_tray, text="", bg=self.colors["bg_light"], 
                                    fg=self.colors["text"], font=("Arial", 10))
        self.clock_label.pack(side=tk.LEFT, padx=5)
        
        user_btn = tk.Button(sys_tray, text=f" 👤 {self.current_user} ", 
                            bg=self.colors["bg_light"], fg=self.colors["text"], 
                            font=("Arial", 9), command=self.show_user_menu)
        user_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_clock()
        self.setup_desktop_icons()
        self.start_idle_monitor()
        self.load_desktop_items() 
        
        # منوی راست کلیک دسکتاپ
        self.desktop_canvas.bind("<Button-3>", self.show_desktop_menu)
    
    def create_desktop_background(self):
        """ایجاد پس‌زمینه گرادیان بدون Pillow"""
        width = 1024
        height = 768
        
        for i in range(height):
            color_value = int(26 + (22 * i / height))  # 1a1a2e to 16213e
            color = f'#{color_value:02x}{color_value:02x}{46 + (i//20):02x}'
            self.desktop_canvas.create_line(0, i, width, i, fill=color, width=1)
    
    def setup_desktop_icons(self):
        # این تابع رو خالی بذار چون کارش رو load_desktop_items انجام میده
        pass
    def create_desktop_icon(self, text, x, y, command):
        frame = tk.Frame(self.desktop_canvas, bg=self.colors["bg_light"], 
                        width=80, height=75, relief=tk.RAISED, bd=1)
        frame.pack_propagate(False)
        
        # آیکون
        icon_label = tk.Label(frame, text=text.split()[0], bg=self.colors["bg_light"],
                             fg=self.colors["text"], font=("Arial", 20))
        icon_label.pack(pady=5)
        
        # متن
        text_label = tk.Label(frame, text=' '.join(text.split()[1:]) if len(text.split()) > 1 else text,
                             bg=self.colors["bg_light"], fg=self.colors["text"],
                             font=("Arial", 8), wraplength=75)
        text_label.pack()
        
        # قابلیت کلیک
        frame.bind("<Button-1>", lambda e: command())
        icon_label.bind("<Button-1>", lambda e: command())
        text_label.bind("<Button-1>", lambda e: command())
        
        # Drag & Drop
        frame.bind("<Button-3>", lambda e: self.show_icon_menu(e, frame))
        
        window_id = self.desktop_canvas.create_window(x, y, window=frame, anchor="nw")
        self.desktop_icons.append({"id": window_id, "frame": frame, "x": x, "y": y})
        
        # قابلیت جابجایی
        self.make_draggable(frame)
    
    def make_draggable(self, widget):
        widget.bind("<Button-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.stop_drag)
    
    def start_drag(self, event):
        self.drag_data["widget"] = event.widget
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def on_drag(self, event):
        widget = self.drag_data["widget"]
        x = widget.winfo_x() - self.drag_data["x"] + event.x
        y = widget.winfo_y() - self.drag_data["y"] + event.y
        widget.place(x=x, y=y)
    
    def stop_drag(self, event):
        self.drag_data = {"widget": None, "x": 0, "y": 0}
    
    def show_desktop_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["bg_medium"], fg=self.colors["text"])
        menu.add_command(label="Refresh", command=self.refresh_desktop)
        menu.add_command(label="New Folder", command=lambda: self.create_new_folder())
        menu.add_command(label="New Text File", command=lambda: self.create_new_file())
        menu.add_separator()
        menu.add_command(label="Personalize", command=self.open_settings)
        menu.post(event.x_root, event.y_root)
    
    def show_icon_menu(self, event, frame):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["bg_medium"], fg=self.colors["text"])
        menu.add_command(label="Remove from Desktop", command=lambda: frame.destroy())
        menu.post(event.x_root, event.y_root)
    
    def refresh_desktop(self):
        for icon in self.desktop_icons:
            try:
                icon["frame"].destroy()
            except:
                pass
        self.desktop_icons.clear()
        self.setup_desktop_icons()
    
    def update_clock(self):
        self.clock_label.config(text=datetime.datetime.now().strftime("%H:%M %p"))
        self.root.after(1000, self.update_clock)
    
    # ============================================
    # سیستم مدیریت بیکاری و Screen Saver
    # ============================================
    def start_idle_monitor(self):
        self.idle_seconds = 0
        self.root.bind('<Motion>', self.reset_idle)
        self.root.bind('<Key>', self.reset_idle)
        self.check_idle()
    
    def reset_idle(self, event=None):
        self.idle_seconds = 0
        if self.screensaver_active:
            self.stop_screensaver()
    
    def check_idle(self):
        self.idle_seconds += 1
        if (self.idle_seconds >= self.settings["auto_screensaver"] and 
            not self.screensaver_active):
            self.start_screensaver()
        self.root.after(1000, self.check_idle)
    
    def start_screensaver(self):
        self.screensaver_active = True
        self.screensaver_window = tk.Toplevel(self.root)
        self.screensaver_window.attributes('-fullscreen', True)
        self.screensaver_window.configure(bg='black')
        self.screensaver_window.bind('<Motion>', self.stop_screensaver)
        self.screensaver_window.bind('<Key>', self.stop_screensaver)
        
        canvas = tk.Canvas(self.screensaver_window, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # انیمیشن ساده با اشکال هندسی
        self.screensaver_shapes = []
        colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
        
        for _ in range(30):
            x = random.randint(0, 1024)
            y = random.randint(0, 768)
            size = random.randint(20, 80)
            color = random.choice(colors)
            shape_type = random.choice(['rect', 'oval'])
            
            if shape_type == 'rect':
                shape = canvas.create_rectangle(x, y, x+size, y+size, 
                                               fill=color, outline='')
            else:
                shape = canvas.create_oval(x, y, x+size, y+size, 
                                          fill=color, outline='')
            
            self.screensaver_shapes.append({
                "shape": shape, 
                "dx": random.randint(-8, 8), 
                "dy": random.randint(-8, 8),
                "canvas": canvas,
                "size": size
            })
        
        # نمایش ساعت
        self.screensaver_clock = canvas.create_text(512, 384, text="", 
                                                    fill="white", font=("Arial", 48))
        self.update_screensaver_clock(canvas)
        self.animate_screensaver()
    
    def update_screensaver_clock(self, canvas):
        if self.screensaver_active:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            canvas.itemconfig(self.screensaver_clock, text=current_time)
            self.root.after(1000, lambda: self.update_screensaver_clock(canvas))
    
    def animate_screensaver(self):
        if self.screensaver_active:
            for item in self.screensaver_shapes:
                canvas = item["canvas"]
                canvas.move(item["shape"], item["dx"], item["dy"])
                coords = canvas.coords(item["shape"])
                
                if coords[0] <= 0 or coords[2] >= 1024:
                    item["dx"] = -item["dx"]
                if coords[1] <= 0 or coords[3] >= 768:
                    item["dy"] = -item["dy"]
            
            self.root.after(50, self.animate_screensaver)
    
    def stop_screensaver(self, event=None):
        if self.screensaver_active:
            self.screensaver_active = False
            self.screensaver_window.destroy()
            self.idle_seconds = 0
    
    # ============================================
    # مرورگر وب ساده
    # ============================================
    def open_browser(self):
        browser_window = tk.Toplevel(self.root)
        browser_window.title("PyOS Browser")
        browser_window.geometry("900x600")
        browser_window.configure(bg=self.colors["bg_dark"])
        
        # نوار ابزار
        toolbar = tk.Frame(browser_window, bg=self.colors["bg_light"], height=40)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # نوار آدرس
        url_var = tk.StringVar(value="about:blank")
        url_entry = tk.Entry(toolbar, textvariable=url_var, bg=self.colors["bg_medium"], 
                            fg=self.colors["text"], font=("Arial", 11), 
                            insertbackground=self.colors["text"])
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        def navigate():
            url = url_var.get()
            if url.startswith("http://") or url.startswith("https://"):
                try:
                    webbrowser.open(url)
                    messagebox.showinfo("Browser", f"Opening {url} in system browser")
                except:
                    messagebox.showerror("Error", "Cannot open browser")
            else:
                messagebox.showinfo("Info", "Enter a valid URL starting with http:// or https://")
        
        tk.Button(toolbar, text="Go", command=navigate, bg=self.colors["success"], 
                 fg=self.colors["bg_dark"], font=("Arial", 10, "bold"), 
                 width=5).pack(side=tk.RIGHT, padx=5)
        
        # صفحه خوش‌آمدگویی
        welcome_frame = tk.Frame(browser_window, bg=self.colors["bg_medium"])
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        welcome_text = """
🌐 PyOS Web Browser

Quick Links (click to open):
"""
        
        text_widget = scrolledtext.ScrolledText(welcome_frame, bg=self.colors["bg_medium"], 
                                               fg=self.colors["text"], font=("Arial", 12), 
                                               wrap=tk.WORD, height=10)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=10)
        text_widget.insert(1.0, welcome_text)
        text_widget.config(state=tk.DISABLED)
        
        # دکمه‌های لینک سریع
        link_frame = tk.Frame(welcome_frame, bg=self.colors["bg_light"])
        link_frame.pack(fill=tk.X, pady=10)
        
        links = [
            ("Google", "https://www.google.com"),
            ("Wikipedia", "https://www.wikipedia.org"),
            ("YouTube", "https://www.youtube.com"),
            ("GitHub", "https://github.com"),
        ]
        
        for name, url in links:
            btn = tk.Button(link_frame, text=name, bg=self.colors["accent"], 
                          fg=self.colors["text"], width=12,
                          command=lambda u=url: url_var.set(u))
            btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        self.add_task("Browser", browser_window)
    
    # ============================================
    # File Manager با Copy/Paste و جستجو
    # ============================================
    def open_file_manager(self):
        fm_window = tk.Toplevel(self.root)
        fm_window.title("PyOS File Manager")
        fm_window.geometry("850x650")
        fm_window.configure(bg=self.colors["bg_dark"])
        
        # نوار ابزار
        toolbar = tk.Frame(fm_window, bg=self.colors["bg_light"], height=45)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # دکمه‌های عملیات
        actions_frame = tk.Frame(toolbar, bg=self.colors["bg_light"])
        actions_frame.pack(side=tk.LEFT, padx=5)
        
        actions = [
            ("📄 New File", lambda: self.create_new_file(fm_window)),
            ("📁 New Folder", lambda: self.create_new_folder(fm_window)),
            ("📋 Copy", lambda: self.copy_selected(fm_window)),
            ("📌 Paste", lambda: self.paste_file(fm_window)),
            ("✂️ Cut", lambda: self.cut_selected(fm_window)),
            ("🗑️ Delete", lambda: self.delete_selected(fm_window)),
            ("🔄 Refresh", lambda: self.refresh_file_list(fm_window, path_var)),
        ]
        
        for text, cmd in actions:
            btn = tk.Button(actions_frame, text=text, bg=self.colors["bg_light"], 
                           fg=self.colors["text"], command=cmd, font=("Arial", 9))
            btn.pack(side=tk.LEFT, padx=2)
        
        # نوار جستجو
        search_frame = tk.Frame(toolbar, bg=self.colors["bg_light"])
        search_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(search_frame, text="🔍", bg=self.colors["bg_light"], 
                fg=self.colors["text"]).pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, 
                               bg=self.colors["bg_medium"], fg=self.colors["text"], 
                               width=20, insertbackground=self.colors["text"])
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # نمایش مسیر
        path_frame = tk.Frame(fm_window, bg=self.colors["bg_medium"], height=35)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        path_var = tk.StringVar(value=str(self.current_path))
        path_label = tk.Label(path_frame, textvariable=path_var, bg=self.colors["bg_medium"], 
                             fg=self.colors["success"], font=("Courier", 10))
        path_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(path_frame, text="⬆ Up", 
                 command=lambda: self.go_up(fm_window, path_var),
                 bg=self.colors["accent"], fg=self.colors["text"]).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(path_frame, text="🏠 Home", 
                 command=lambda: self.go_home(fm_window, path_var),
                 bg=self.colors["accent"], fg=self.colors["text"]).pack(side=tk.RIGHT, padx=5)
        
        # لیست فایل‌ها با Treeview
        tree_frame = tk.Frame(fm_window, bg=self.colors["bg_medium"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        style = ttk.Style()
        style.configure("Treeview", background=self.colors["bg_medium"], 
                       foreground=self.colors["text"], fieldbackground=self.colors["bg_medium"])
        style.map('Treeview', background=[('selected', self.colors["accent"])])
        
        self.file_tree = ttk.Treeview(tree_frame, columns=("Type", "Size", "Modified"), 
                                      yscrollcommand=scrollbar.set)
        self.file_tree.heading("#0", text="Name")
        self.file_tree.heading("Type", text="Type")
        self.file_tree.heading("Size", text="Size")
        self.file_tree.heading("Modified", text="Modified")
        self.file_tree.column("#0", width=350)
        self.file_tree.column("Type", width=80)
        self.file_tree.column("Size", width=100)
        self.file_tree.column("Modified", width=150)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.file_tree.yview)
        
        # رویدادها
        self.file_tree.bind("<Double-1>", lambda e: self.open_selected_item(fm_window, path_var))
        self.file_tree.bind("<Button-3>", self.show_file_context_menu)
        
        # جستجوی زنده
        def on_search(*args):
            query = search_var.get().lower()
            self.refresh_file_list(fm_window, path_var, query)
        
        search_var.trace('w', on_search)
        
        self.refresh_file_list(fm_window, path_var)
        self.add_task("File Manager", fm_window)
    
    def refresh_file_list(self, window, path_var, query=""):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        path_var.set(str(self.current_path))
        
        try:
            items = list(self.current_path.iterdir())
        except PermissionError:
            messagebox.showerror("Error", "Access denied to this folder")
            return
        
        # فیلتر با جستجو
        if query:
            items = [i for i in items if query in i.name.lower()]
        
        # جدا کردن پوشه‌ها و فایل‌ها
        folders = [i for i in items if i.is_dir()]
        files = [i for i in items if i.is_file()]
        
        # اضافه کردن پوشه‌ها
        for folder in sorted(folders):
            self.file_tree.insert("", "end", text=f"📁 {folder.name}", 
                                 values=("Folder", "--", ""), tags=("folder",))
        
        # اضافه کردن فایل‌ها
        for file in sorted(files):
            size = file.stat().st_size
            size_str = self.format_size(size)
            modified = datetime.datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            file_type = file.suffix.upper()[1:] if file.suffix else "File"
            icon = self.get_file_icon(file.suffix)
            
            self.file_tree.insert("", "end", text=f"{icon} {file.name}",
                                 values=(file_type, size_str, modified), tags=("file",))
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def get_file_icon(self, ext):
        icons = {
            '.txt': '📝', '.py': '🐍', '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️',
            '.pdf': '📕', '.docx': '📘', '.doc': '📘', '.xlsx': '📊', '.xls': '📊',
            '.zip': '📦', '.rar': '📦', '.mp3': '🎵', '.mp4': '🎬', '.exe': '⚙️'
        }
        return icons.get(ext.lower(), '📄')
    
    def open_selected_item(self, window, path_var):
        selected = self.file_tree.selection()
        if not selected:
            return
        
        item_text = self.file_tree.item(selected[0])['text']
        name = item_text.split(' ', 1)[1]
        path = self.current_path / name
        
        if path.is_dir():
            self.current_path = path
            self.refresh_file_list(window, path_var)
        else:
            # اگر فایل .py بود اجراش کن
            if path.suffix == '.py':
                try:
                    exec(open(path, encoding='utf-8').read())
                    messagebox.showinfo("PyOS", f"App '{path.name}' executed!")
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot run app: {e}")
            else:
                try:
                    # اگه فایل پایتون بود، اجراش کن
                    if path.suffix == '.py':
                       with open(path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        exec(code, {"__name__": "__main__"})
                    else:
                        os.startfile(path)
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot open file: {e}")
    def show_file_context_menu(self, event):
        selected = self.file_tree.selection()
        if not selected:
            return
        
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["bg_medium"], fg=self.colors["text"])
        menu.add_command(label="Open", command=lambda: self.open_selected_item(None, None))
        menu.add_command(label="Copy", command=lambda: self.copy_selected(None))
        menu.add_command(label="Cut", command=lambda: self.cut_selected(None))
        menu.add_command(label="Paste", command=lambda: self.paste_file(None))
        menu.add_separator()
        menu.add_command(label="Rename", command=self.rename_item)
        menu.add_command(label="Delete", command=lambda: self.delete_selected(None))
        menu.add_separator()
        menu.add_command(label="Properties", command=self.show_file_properties)
        menu.post(event.x_root, event.y_root)
    
    def copy_selected(self, window):
        selected = self.file_tree.selection()
        if selected:
            item_text = self.file_tree.item(selected[0])['text']
            name = item_text.split(' ', 1)[1]
            self.clipboard = {"path": self.current_path / name, "operation": "copy"}
            messagebox.showinfo("Copy", f"'{name}' copied to clipboard")
    
    def cut_selected(self, window):
        selected = self.file_tree.selection()
        if selected:
            item_text = self.file_tree.item(selected[0])['text']
            name = item_text.split(' ', 1)[1]
            self.clipboard = {"path": self.current_path / name, "operation": "cut"}
            messagebox.showinfo("Cut", f"'{name}' cut to clipboard")
    
    def paste_file(self, window):
        if not self.clipboard:
            messagebox.showwarning("Paste", "Clipboard is empty")
            return
        
        source = self.clipboard["path"]
        if not source.exists():
            messagebox.showerror("Error", "Source file no longer exists")
            self.clipboard = None
            return
        
        dest = self.current_path / source.name
        counter = 1
        original_name = source.stem
        extension = source.suffix
        
        while dest.exists():
            dest = self.current_path / f"{original_name} - Copy{counter}{extension}"
            counter += 1
        
        try:
            if source.is_dir():
                if self.clipboard["operation"] == "cut":
                    shutil.move(str(source), str(dest))
                else:
                    shutil.copytree(str(source), str(dest))
            else:
                if self.clipboard["operation"] == "cut":
                    shutil.move(str(source), str(dest))
                else:
                    shutil.copy2(str(source), str(dest))
            
            if self.clipboard["operation"] == "cut":
                self.clipboard = None
            
            if window:
                self.refresh_file_list(window, None)
            messagebox.showinfo("Success", f"Pasted '{source.name}'")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot paste: {e}")
    
    def rename_item(self):
        selected = self.file_tree.selection()
        if selected:
            item_text = self.file_tree.item(selected[0])['text']
            old_name = item_text.split(' ', 1)[1]
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Rename")
            dialog.geometry("350x120")
            dialog.configure(bg=self.colors["bg_medium"])
            
            tk.Label(dialog, text=f"Rename '{old_name}' to:", bg=self.colors["bg_medium"], 
                    fg=self.colors["text"]).pack(pady=10)
            
            entry = tk.Entry(dialog, bg=self.colors["bg_light"], fg=self.colors["text"], width=40)
            entry.insert(0, old_name)
            entry.pack(pady=5)
            entry.select_range(0, tk.END)
            entry.focus()
            
            def do_rename():
                new_name = entry.get()
                if new_name and new_name != old_name:
                    old_path = self.current_path / old_name
                    new_path = self.current_path / new_name
                    try:
                        old_path.rename(new_path)
                        self.refresh_file_list(None, None)
                        dialog.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Cannot rename: {e}")
                else:
                    dialog.destroy()
            
            tk.Button(dialog, text="OK", command=do_rename, 
                     bg=self.colors["success"], fg=self.colors["bg_dark"], width=10).pack(pady=10)
            entry.bind('<Return>', lambda e: do_rename())
    
    def show_file_properties(self):
        selected = self.file_tree.selection()
        if selected:
            item_text = self.file_tree.item(selected[0])['text']
            name = item_text.split(' ', 1)[1]
            path = self.current_path / name
            
            props_window = tk.Toplevel(self.root)
            props_window.title(f"Properties - {name}")
            props_window.geometry("350x250")
            props_window.configure(bg=self.colors["bg_medium"])
            
            stats = path.stat()
            
            info = f"""
Name: {path.name}
Type: {'Folder' if path.is_dir() else 'File'}
Location: {path.parent}
Size: {self.format_size(stats.st_size) if path.is_file() else 'N/A'}
Created: {datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
Modified: {datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            tk.Label(props_window, text=info, bg=self.colors["bg_medium"], 
                    fg=self.colors["text"], font=("Arial", 10), justify=tk.LEFT).pack(pady=20)
            
            tk.Button(props_window, text="Close", command=props_window.destroy,
                     bg=self.colors["accent"], fg=self.colors["text"], width=10).pack()
    
    def create_new_file(self, window=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("New File")
        dialog.geometry("350x120")
        dialog.configure(bg=self.colors["bg_medium"])
        
        tk.Label(dialog, text="Enter file name:", bg=self.colors["bg_medium"], 
                fg=self.colors["text"]).pack(pady=10)
        
        entry = tk.Entry(dialog, bg=self.colors["bg_light"], fg=self.colors["text"], width=40)
        entry.pack(pady=5)
        entry.focus()
        
        def create():
            filename = entry.get()
            if filename:
                filepath = self.current_path / filename
                try:
                    filepath.touch()
                    if window:
                        self.refresh_file_list(window, None)
                    messagebox.showinfo("Success", f"File '{filename}' created!")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot create file: {e}")
        
        tk.Button(dialog, text="Create", command=create,
                 bg=self.colors["success"], fg=self.colors["bg_dark"], width=10).pack(pady=10)
        entry.bind('<Return>', lambda e: create())
    
    def create_new_folder(self, window=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Folder")
        dialog.geometry("350x120")
        dialog.configure(bg=self.colors["bg_medium"])
        
        tk.Label(dialog, text="Enter folder name:", bg=self.colors["bg_medium"], 
                fg=self.colors["text"]).pack(pady=10)
        
        entry = tk.Entry(dialog, bg=self.colors["bg_light"], fg=self.colors["text"], width=40)
        entry.pack(pady=5)
        entry.focus()
        
        def create():
            foldername = entry.get()
            if foldername:
                folderpath = self.current_path / foldername
                try:
                    folderpath.mkdir()
                    if window:
                        self.refresh_file_list(window, None)
                    messagebox.showinfo("Success", f"Folder '{foldername}' created!")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot create folder: {e}")
        
        tk.Button(dialog, text="Create", command=create,
                 bg=self.colors["success"], fg=self.colors["bg_dark"], width=10).pack(pady=10)
        entry.bind('<Return>', lambda e: create())
    
    def delete_selected(self, window):
        selected = self.file_tree.selection()
        if selected:
            item_text = self.file_tree.item(selected[0])['text']
            name = item_text.split(' ', 1)[1]
            if messagebox.askyesno("Confirm Delete", f"Delete '{name}' permanently?"):
                path = self.current_path / name
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    if window:
                        self.refresh_file_list(window, None)
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot delete: {e}")
    
    def go_up(self, window, path_var):
        if self.current_path != self.pyos_home:
            self.current_path = self.current_path.parent
            self.refresh_file_list(window, path_var)
    
    def go_home(self, window, path_var):
        self.current_path = self.user_folder
        self.refresh_file_list(window, path_var)
    
    # ============================================
    # Notepad پیشرفته
    # ============================================
    def open_notepad(self, filepath=None):
        notepad_window = tk.Toplevel(self.root)
        notepad_window.title("PyOS Notepad")
        notepad_window.geometry("750x550")
        notepad_window.configure(bg=self.colors["bg_dark"])
        
        # منو بار
        menubar = tk.Menu(notepad_window, bg=self.colors["bg_light"], fg=self.colors["text"])
        notepad_window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg_medium"], fg=self.colors["text"])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=lambda: text_area.delete(1.0, tk.END))
        file_menu.add_command(label="Open...", command=lambda: self.open_file_dialog(text_area))
        file_menu.add_command(label="Save", command=lambda: self.save_file_dialog(text_area))
        file_menu.add_command(label="Save As...", command=lambda: self.save_as_dialog(text_area))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=notepad_window.destroy)
        
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg_medium"], fg=self.colors["text"])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: text_area.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=lambda: text_area.tag_add(tk.SEL, "1.0", tk.END))
        
        # Text Area
        text_frame = tk.Frame(notepad_window, bg=self.colors["bg_dark"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD,
                                              bg=self.colors["bg_medium"], fg=self.colors["text"],
                                              insertbackground=self.colors["text"],
                                              font=("Consolas", 11), undo=True)
        text_area.pack(fill=tk.BOTH, expand=True)
        
        if filepath and Path(filepath).exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                text_area.insert(1.0, f.read())
            notepad_window.title(f"PyOS Notepad - {Path(filepath).name}")
        
        # Status Bar
        status_bar = tk.Label(notepad_window, text="Ready", bg=self.colors["bg_light"], 
                             fg=self.colors["text"], anchor=tk.W, font=("Arial", 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        def update_status():
            content = text_area.get(1.0, tk.END)
            lines = content.count('\n')
            words = len(content.split())
            chars = len(content) - 1
            cursor_pos = text_area.index(tk.INSERT)
            status_bar.config(text=f"Lines: {lines} | Words: {words} | Characters: {chars} | Position: {cursor_pos}")
            notepad_window.after(1000, update_status)
        
        update_status()
        self.add_task("Notepad", notepad_window)
    
    def open_file_dialog(self, text_area):
        file_path = filedialog.askopenfilename(
            initialdir=self.user_folder,
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            text_area.delete(1.0, tk.END)
            text_area.insert(1.0, content)
    
    def save_file_dialog(self, text_area):
        file_path = filedialog.asksaveasfilename(
            initialdir=self.user_folder,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_area.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Saved to {Path(file_path).name}")
    
    def save_as_dialog(self, text_area):
        self.save_file_dialog(text_area)
    
    # ============================================
    # Task Manager
    # ============================================
    def open_task_manager(self):
        tm_window = tk.Toplevel(self.root)
        tm_window.title("PyOS Task Manager")
        tm_window.geometry("600x450")
        tm_window.configure(bg=self.colors["bg_dark"])
        
        tk.Label(tm_window, text="Running Applications", font=("Arial", 14, "bold"),
                bg=self.colors["bg_dark"], fg=self.colors["success"]).pack(pady=10)
        
        # فریم اصلی
        main_frame = tk.Frame(tm_window, bg=self.colors["bg_medium"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # لیست تسک‌ها
        list_frame = tk.Frame(main_frame, bg=self.colors["bg_medium"])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_listbox = tk.Listbox(list_frame, bg=self.colors["bg_light"], 
                                       fg=self.colors["text"], font=("Arial", 10), 
                                       yscrollcommand=scrollbar.set, height=15)
        self.task_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)
        
        self.refresh_task_list()
        
        # دکمه‌های کنترل
        btn_frame = tk.Frame(tm_window, bg=self.colors["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def end_task():
            selected = self.task_listbox.curselection()
            if selected:
                index = selected[0]
                if index < len(self.running_tasks):
                    task = self.running_tasks[index]
                    try:
                        task['window'].destroy()
                    except:
                        pass
                    self.running_tasks.pop(index)
                    self.refresh_task_list()
                    self.update_taskbar()
        
        def switch_to_task():
            selected = self.task_listbox.curselection()
            if selected:
                index = selected[0]
                if index < len(self.running_tasks):
                    task = self.running_tasks[index]
                    task['window'].lift()
                    task['window'].focus_force()
        
        tk.Button(btn_frame, text="End Task", command=end_task,
                 bg=self.colors["accent"], fg=self.colors["text"], width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Switch To", command=switch_to_task,
                 bg=self.colors["bg_light"], fg=self.colors["text"], width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_task_list,
                 bg=self.colors["bg_light"], fg=self.colors["text"], width=15).pack(side=tk.LEFT, padx=5)
        
        self.add_task("Task Manager", tm_window)
    
    def add_task(self, name, window):
        self.running_tasks.append({"name": name, "window": window})
        self.update_taskbar()
        
        def on_close():
            for i, task in enumerate(self.running_tasks):
                if task['window'] == window:
                    self.running_tasks.pop(i)
                    break
            self.update_taskbar()
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_close)
    
    def update_taskbar(self):
        if hasattr(self, 'taskbar_tasks'):
            for widget in self.taskbar_tasks.winfo_children():
                widget.destroy()
            
            for task in self.running_tasks[-8:]:
                display_name = task['name'][:12] + ('...' if len(task['name']) > 12 else '')
                btn = tk.Button(self.taskbar_tasks, text=display_name, 
                               bg=self.colors["bg_medium"], fg=self.colors["text"], 
                               font=("Arial", 9), relief=tk.RAISED, bd=1,
                               command=lambda t=task: self.focus_task(t))
                btn.pack(side=tk.LEFT, padx=2, pady=5)
    
    def focus_task(self, task):
        try:
            task['window'].lift()
            task['window'].focus_force()
        except:
            pass
    
    def refresh_task_list(self):
        if hasattr(self, 'task_listbox'):
            self.task_listbox.delete(0, tk.END)
            for task in self.running_tasks:
                status = "Running"
                self.task_listbox.insert(tk.END, f"{task['name']} - {task['window'].title()} - [{status}]")
    
    # ============================================
    # بازی Snake
    # ============================================
    def open_snake_game(self):
        game_window = tk.Toplevel(self.root)
        game_window.title("PyOS Snake")
        game_window.geometry("450x500")
        game_window.configure(bg=self.colors["bg_dark"])
        game_window.resizable(False, False)
        
        # Score
        score_frame = tk.Frame(game_window, bg=self.colors["bg_dark"])
        score_frame.pack(pady=5)
        
        score_label = tk.Label(score_frame, text="Score: 0", bg=self.colors["bg_dark"], 
                              fg=self.colors["text"], font=("Arial", 14, "bold"))
        score_label.pack(side=tk.LEFT, padx=20)
        
        high_score_label = tk.Label(score_frame, text="High Score: 0", bg=self.colors["bg_dark"], 
                                   fg=self.colors["success"], font=("Arial", 14, "bold"))
        high_score_label.pack(side=tk.LEFT, padx=20)
        
        # Canvas بازی
        canvas = tk.Canvas(game_window, bg=self.colors["bg_medium"], width=400, height=400)
        canvas.pack(pady=10)
        
        # متغیرهای بازی
        snake = [(200, 200), (190, 200), (180, 200)]
        direction = "Right"
        next_direction = "Right"
        food = None
        score = 0
        high_score = self.load_high_score()
        high_score_label.config(text=f"High Score: {high_score}")
        game_running = True
        game_paused = False
        speed = 100
        
        def create_food():
            nonlocal food
            while True:
                x = random.randint(1, 38) * 10
                y = random.randint(1, 38) * 10
                if (x, y) not in snake:
                    food = (x, y)
                    canvas.create_oval(x-5, y-5, x+5, y+5, fill=self.colors["accent"], tags="food")
                    break
        
                def open_snake_game(self):
                 game_window = tk.Toplevel(self.root)
                 game_window.title("PyOS Snake")
        # ... (کدهای اولیه تا قبل از move_snake)
        
        # اول تابع رو کامل تعریف کن
        def move_snake():
            nonlocal snake, direction, next_direction, food, score, game_running, high_score, speed
            
            if not game_running or game_paused:
                game_window.after(speed, move_snake)
                return
            
            direction = next_direction
            head = snake[0]
            
            if direction == "Right":
                new_head = (head[0] + 10, head[1])
            elif direction == "Left":
                new_head = (head[0] - 10, head[1])
            elif direction == "Up":
                new_head = (head[0], head[1] - 10)
            else:
                new_head = (head[0], head[1] + 10)
            
            if (new_head[0] < 0 or new_head[0] >= 400 or 
                new_head[1] < 0 or new_head[1] >= 400):
                game_over()
                return
            
            if new_head in snake:
                game_over()
                return
            
            snake.insert(0, new_head)
            
            if food and new_head == food:
                score += 10
                score_label.config(text=f"Score: {score}")
                canvas.delete("food")
                create_food()
                speed = max(50, speed - 2)
            else:
                snake.pop()
            
            canvas.delete("snake")
            for i, segment in enumerate(snake):
                color = self.colors["success"] if i == 0 else "#00cc66"
                canvas.create_rectangle(segment[0]-5, segment[1]-5, 
                                       segment[0]+5, segment[1]+5,
                                       fill=color, outline="", tags="snake")
            
            game_window.after(speed, move_snake)
            game_window.after(speed, move_snake)
        
        def change_direction(new_dir):
            nonlocal next_direction
            opposites = {"Right": "Left", "Left": "Right", "Up": "Down", "Down": "Up"}
            if opposites[new_dir] != direction:
                next_direction = new_dir
        
        def toggle_pause():
            nonlocal game_paused
            game_paused = not game_paused
            pause_btn.config(text="▶ Resume" if game_paused else "⏸ Pause")
        
        def restart_game():
            nonlocal snake, direction, next_direction, food, score, game_running, game_paused, speed
            snake = [(200, 200), (190, 200), (180, 200)]
            direction = "Right"
            next_direction = "Right"
            score = 0
            game_running = True
            game_paused = False
            speed = 100
            score_label.config(text="Score: 0")
            pause_btn.config(text="⏸ Pause")
            canvas.delete("all")
            create_food()
        
        def game_over():
            nonlocal game_running, high_score
            game_running = False
            if score > high_score:
                high_score = score
                self.save_high_score(high_score)
                high_score_label.config(text=f"High Score: {high_score}")
            
            canvas.create_text(200, 180, text="GAME OVER", fill=self.colors["accent"],
                             font=("Arial", 24, "bold"))
            canvas.create_text(200, 220, text=f"Final Score: {score}", fill=self.colors["text"],
                             font=("Arial", 14))
        
        # کنترل‌ها
        control_frame = tk.Frame(game_window, bg=self.colors["bg_dark"])
        control_frame.pack(pady=5)
        
        pause_btn = tk.Button(control_frame, text="⏸ Pause", command=toggle_pause,
                             bg=self.colors["bg_light"], fg=self.colors["text"], width=10)
        pause_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="🔄 Restart", command=restart_game,
                 bg=self.colors["bg_light"], fg=self.colors["text"], width=10).pack(side=tk.LEFT, padx=5)
        
        # راهنما
        help_text = "Use Arrow Keys to Move | Space to Pause"
        tk.Label(game_window, text=help_text, bg=self.colors["bg_dark"], 
                fg=self.colors["text"], font=("Arial", 9)).pack(pady=5)
        
        # بایند کلیدها
        game_window.bind("<Right>", lambda e: change_direction("Right"))
        game_window.bind("<Left>", lambda e: change_direction("Left"))
        game_window.bind("<Up>", lambda e: change_direction("Up"))
        game_window.bind("<Down>", lambda e: change_direction("Down"))
        game_window.bind("<space>", lambda e: toggle_pause())
        game_window.bind("r", lambda e: restart_game())
        
        create_food()
        move_snake()
        self.add_task("Snake Game", game_window)
    
    def load_high_score(self):
        hs_file = self.settings_dir / "snake_highscore.txt"
        if hs_file.exists():
            try:
                with open(hs_file, 'r') as f:
                    return int(f.read())
            except:
                return 0
        return 0
    
    def save_high_score(self, score):
        hs_file = self.settings_dir / "snake_highscore.txt"
        with open(hs_file, 'w') as f:
            f.write(str(score))
    
    # ============================================
    # تنظیمات
    # ============================================
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("PyOS Settings")
        settings_window.geometry("400x350")
        settings_window.configure(bg=self.colors["bg_dark"])
        
        tk.Label(settings_window, text="System Settings", font=("Arial", 16, "bold"),
                bg=self.colors["bg_dark"], fg=self.colors["success"]).pack(pady=20)
        
        # فریم تنظیمات
        settings_frame = tk.Frame(settings_window, bg=self.colors["bg_medium"])
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Screensaver timeout
        tk.Label(settings_frame, text="Screensaver timeout (seconds):", 
                bg=self.colors["bg_medium"], fg=self.colors["text"]).grid(row=0, column=0, pady=10, sticky="w")
        
        timeout_var = tk.IntVar(value=self.settings["auto_screensaver"])
        timeout_scale = tk.Scale(settings_frame, from_=30, to=300, orient=tk.HORIZONTAL,
                                variable=timeout_var, bg=self.colors["bg_medium"], 
                                fg=self.colors["text"], length=200)
        timeout_scale.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(settings_frame, text=f"{timeout_var.get()}s", bg=self.colors["bg_medium"], 
                fg=self.colors["text"], textvariable=timeout_var).grid(row=0, column=2)
        
        # اطلاعات سیستم
        info_frame = tk.Frame(settings_window, bg=self.colors["bg_light"], relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        info_text = f"""
System Information:
• Current User: {self.current_user}
• User Folder: {self.user_folder}
• System Folder: {self.pyos_home}
• Python Version: {os.sys.version.split()[0]}
"""
        
        tk.Label(info_frame, text=info_text, bg=self.colors["bg_light"], fg=self.colors["text"],
                font=("Courier", 9), justify=tk.LEFT).pack(padx=10, pady=10)
        
        # دکمه‌ها
        btn_frame = tk.Frame(settings_window, bg=self.colors["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_settings():
            self.settings["auto_screensaver"] = timeout_var.get()
            self.save_settings()
            messagebox.showinfo("Settings", "Settings saved successfully!")
            settings_window.destroy()
        
        tk.Button(btn_frame, text="Save", command=save_settings,
                 bg=self.colors["success"], fg=self.colors["bg_dark"], 
                 font=("Arial", 10, "bold"), width=12).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=settings_window.destroy,
                 bg=self.colors["accent"], fg=self.colors["text"], 
                 width=12).pack(side=tk.RIGHT, padx=5)
    
    # ============================================
    # منوها
    # ============================================
    def show_start_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["bg_medium"], fg=self.colors["text"])
        
        # Programs
        programs_menu = tk.Menu(menu, tearoff=0, bg=self.colors["bg_light"], fg=self.colors["text"])
        menu.add_cascade(label="Programs", menu=programs_menu)
        programs_menu.add_command(label="🌐 Browser", command=self.open_browser)
        programs_menu.add_command(label="📁 File Manager", command=self.open_file_manager)
        programs_menu.add_command(label="📝 Notepad", command=self.open_notepad)
        programs_menu.add_command(label="📊 Task Manager", command=self.open_task_manager)
        programs_menu.add_separator()
        programs_menu.add_command(label="🎮 Snake Game", command=self.open_snake_game)
        # Documents
        docs_menu = tk.Menu(menu, tearoff=0, bg=self.colors["bg_light"], fg=self.colors["text"])
        menu.add_cascade(label="Documents", menu=docs_menu)
        docs_menu.add_command(label="📁 My Documents", 
                             command=lambda: self.open_folder(self.user_folder / "Documents"))
        docs_menu.add_command(label="🖼️ My Pictures", 
                             command=lambda: self.open_folder(self.user_folder / "Pictures"))
        docs_menu.add_command(label="⬇️ Downloads", 
                             command=lambda: self.open_folder(self.user_folder / "Downloads"))
        
        # Settings
        menu.add_separator()
        menu.add_command(label="👤 Account", command=self.account_settings)
        menu.add_separator()
        menu.add_command(label="🔧 Settings", command=self.open_settings)
        menu.add_separator()
        menu.add_command(label="⚙️ Control Panel", command=self.open_control_panel)
        programs_menu.add_command(label="🔐 Password Generator", command=self.open_password_gen)
        programs_menu.add_command(label="📊 System Monitor", command=self.open_sys_monitor)
        
        menu.add_separator()
        menu.add_command(label="🚪 Logout", command=self.setup_login_screen)
        menu.add_command(label="⏻ Shutdown", command=self.root.quit)
        
        x = self.root.winfo_rootx() + 10
        y = self.root.winfo_rooty() + self.root.winfo_height() - 250
        menu.post(x, y)
    
    def show_user_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["bg_medium"], fg=self.colors["text"])
        menu.add_command(label="👤 Account Settings", command=self.account_settings)
        menu.add_command(label="🔒 Lock", command=self.start_screensaver)
        menu.add_separator()
        menu.add_command(label="🚪 Logout", command=self.setup_login_screen)
        
        x = self.root.winfo_rootx() + self.root.winfo_width() - 120
        y = self.root.winfo_rooty() + self.root.winfo_height() - 50
        menu.post(x, y)
    
    def account_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Account Settings")
        dialog.geometry("350x250")
        dialog.configure(bg=self.colors["bg_dark"])
        
        tk.Label(dialog, text=f"Username: {self.current_user}", font=("Arial", 12, "bold"),
                bg=self.colors["bg_dark"], fg=self.colors["success"]).pack(pady=20)
        
        def change_password():
            old_pass = simpledialog.askstring("Change Password", "Current password:", show="•")
            if old_pass and old_pass == self.settings["users"][self.current_user]["password"]:
                new_pass = simpledialog.askstring("Change Password", "New password:", show="•")
                if new_pass:
                    confirm = simpledialog.askstring("Change Password", "Confirm new password:", show="•")
                    if new_pass == confirm:
                        self.settings["users"][self.current_user]["password"] = new_pass
                        self.save_settings()
                        messagebox.showinfo("Success", "Password changed successfully!")
                    else:
                        messagebox.showerror("Error", "Passwords don't match")
            elif old_pass:
                messagebox.showerror("Error", "Incorrect current password")
        
        tk.Button(dialog, text="Change Password", command=change_password,
                 bg=self.colors["accent"], fg=self.colors["text"], 
                 font=("Arial", 10), width=20).pack(pady=10)
        
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg=self.colors["bg_light"], fg=self.colors["text"], 
                 width=20).pack(pady=10)
    
    def open_folder(self, path):
        self.current_path = path
        self.open_file_manager()
    
    def open_recycle_bin(self):
        recycle_path = self.pyos_home / "RecycleBin"
        recycle_path.mkdir(exist_ok=True)
        self.current_path = recycle_path
        self.open_file_manager()
    
    def run(self):
        self.root.mainloop()
        def open_app_launcher(self):
         """run installed programs"""
        launcher_window = tk.Toplevel(self.root)
        launcher_window.title("PyOS App Launcher")
        launcher_window.geometry("500x400")
        launcher_window.configure(bg=self.colors["bg_dark"])
        
        tk.Label(launcher_window, text="📱 Installed Applications", 
                font=("Arial", 14, "bold"), bg=self.colors["bg_dark"], 
                fg=self.colors["success"]).pack(pady=10)
        
        # فریم لیست برنامه‌ها
        list_frame = tk.Frame(launcher_window, bg=self.colors["bg_medium"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        app_listbox = tk.Listbox(list_frame, bg=self.colors["bg_light"], 
                                fg=self.colors["text"], font=("Arial", 11),
                                yscrollcommand=scrollbar.set, height=12)
        app_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=app_listbox.yview)
        
        # پیدا کردن فایل‌های .py در پوشه Apps
        app_files = list(self.apps_dir.glob("*.py"))
        
        for app_file in app_files:
            app_name = app_file.stem.replace("_", " ").title()
            app_listbox.insert(tk.END, f"📄 {app_name}")
        
        if not app_files:
            app_listbox.insert(tk.END, "No apps found. Add .py files to Apps folder.")
        
        # دکمه‌های کنترل
        btn_frame = tk.Frame(launcher_window, bg=self.colors["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def run_selected_app():
            selected = app_listbox.curselection()
            if selected and app_files:
                index = selected[0]
                if index < len(app_files):
                    app_path = app_files[index]
                    try:
                        # اجرای فایل پایتون
                        exec(open(app_path, encoding='utf-8').read())
                        messagebox.showinfo("Success", f"{app_path.name} executed!")
                    except Exception as e:
                        messagebox.showerror("Error", f"Cannot run app: {e}")
        
        def open_apps_folder():
            self.current_path = self.apps_dir
            self.open_file_manager()
        
        def create_new_app():
            dialog = tk.Toplevel(launcher_window)
            dialog.title("Create New App")
            dialog.geometry("400x300")
            dialog.configure(bg=self.colors["bg_medium"])
            
            tk.Label(dialog, text="App Name:", bg=self.colors["bg_medium"], 
                    fg=self.colors["text"]).pack(pady=5)
            name_entry = tk.Entry(dialog, bg=self.colors["bg_light"], 
                                  fg=self.colors["text"], width=30)
            name_entry.pack(pady=5)
            
            tk.Label(dialog, text="Python Code:", bg=self.colors["bg_medium"], 
                    fg=self.colors["text"]).pack(pady=5)
            code_text = scrolledtext.ScrolledText(dialog, bg=self.colors["bg_light"], 
                                                  fg=self.colors["text"], height=10)
            code_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
            
            # کد نمونه
            sample_code = '''import tkinter as tk

def main():
    win = tk.Toplevel()
    win.title("My App")
    win.geometry("300x200")
    win.configure(bg="#1a1a2e")
    
    tk.Label(win, text="Hello from PyOS!", 
             font=("Arial", 14), bg="#1a1a2e", fg="#00ff88").pack(expand=True)
    
    win.mainloop()

if __name__ == "__main__":
    main()
else:
    main()'''
            
            code_text.insert(1.0, sample_code)
            
            def save_app():
                app_name = name_entry.get().strip()
                if not app_name:
                    messagebox.showerror("Error", "Enter app name")
                    return
                
                filename = app_name.replace(" ", "_") + ".py"
                filepath = self.apps_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code_text.get(1.0, tk.END))
                
                messagebox.showinfo("Success", f"App saved to {filename}")
                dialog.destroy()
                launcher_window.destroy()
                self.open_app_launcher()
            
            tk.Button(dialog, text="Save App", command=save_app,
                     bg=self.colors["success"], fg=self.colors["bg_dark"],
                     width=15).pack(pady=10)
        
        tk.Button(btn_frame, text="▶ Run", command=run_selected_app,
                 bg=self.colors["success"], fg=self.colors["bg_dark"], width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📁 Open Folder", command=open_apps_folder,
                 bg=self.colors["bg_light"], fg=self.colors["text"], width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="➕ New App", command=create_new_app,
                 bg=self.colors["accent"], fg=self.colors["text"], width=12).pack(side=tk.LEFT, padx=5)
        
        self.add_task("App Launcher", launcher_window)
    
    def adjust_color(self, hex_color, amount):
        """تیره یا روشن کردن رنگ"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"
    
    def generate_report(self):
        """گزارش سیستم"""
        report_path = self.user_folder / "system_report.txt"
        with open(report_path, 'w') as f:
            f.write(f"PyOS System Report\n")
            f.write(f"Generated: {datetime.datetime.now()}\n")
            f.write(f"{'='*50}\n")
            f.write(f"User: {self.current_user}\n")
            f.write(f"Home: {self.pyos_home}\n")
            f.write(f"Running Tasks: {len(self.running_tasks)}\n")
        messagebox.showinfo("Report", f"Report saved to {report_path}")
    def load_desktop_items(self):
        """بارگذاری فایل‌های پوشه Desktop روی دسکتاپ"""
        # پاک کردن آیکون‌های قبلی
        for icon in self.desktop_icons:
            try:
                icon["frame"].destroy()
            except:
                pass
        self.desktop_icons.clear()
        
        desktop_path = self.user_folder / "Desktop"
        if not desktop_path.exists():
            return
        
        # آیکون‌های سیستمی
        system_icons = [
            ("📁 My Computer", self.open_file_manager, 0),
            ("📁 Documents", lambda: self.open_folder(self.user_folder / "Documents"), 1),
            ("🖼️ Pictures", lambda: self.open_folder(self.user_folder / "Pictures"), 2),
            ("🌐 Browser", self.open_browser, 3),
            ("📝 Notepad", self.open_notepad, 4),
            ("🎮 Snake", self.open_snake_game, 5),
            ("🗑️ Recycle Bin", self.open_recycle_bin, 7),
        ]
        
        y_pos = 20
        for text, cmd, idx in system_icons:
            self.create_desktop_icon(text, 20, y_pos, cmd)
            y_pos += 85
        
        # بارگذاری فایل‌های واقعی از پوشه Desktop
        x_pos = 120
        y_pos = 20
        
        for item in desktop_path.iterdir():
            if item.is_file():
                icon_text = f"📄 {item.name[:15]}"
                cmd = lambda p=item: self.open_file_from_desktop(p)
            else:
                icon_text = f"📁 {item.name[:15]}"
                cmd = lambda p=item: self.open_folder_from_desktop(p)
            
            self.create_desktop_icon(icon_text, x_pos, y_pos, cmd, draggable=True)
            x_pos += 100
            if x_pos > 800:
                x_pos = 120
                y_pos += 85
    
    def create_desktop_icon(self, text, x, y, command, draggable=True):
        """ساخت آیکون دسکتاپ با قابلیت جابجایی"""
        frame = tk.Frame(self.desktop_canvas, bg=self.colors["bg_light"], 
                        width=85, height=80, relief=tk.RAISED, bd=1)
        frame.pack_propagate(False)
        
        # آیکون
        icon_char = text.split()[0]
        tk.Label(frame, text=icon_char, bg=self.colors["bg_light"],
                fg=self.colors["text"], font=("Arial", 22)).pack(pady=5)
        
        # متن
        display_text = ' '.join(text.split()[1:]) if len(text.split()) > 1 else text
        tk.Label(frame, text=display_text, bg=self.colors["bg_light"], 
                fg=self.colors["text"], font=("Arial", 7), wraplength=80).pack()
        
        # قابلیت کلیک
        frame.bind("<Button-1>", lambda e: command())
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e: command())
        
        # Drag & Drop
        if draggable:
            self.make_draggable(frame)
        
        # منوی راست کلیک
        frame.bind("<Button-3>", lambda e: self.show_desktop_icon_menu(e, frame))
        
        window_id = self.desktop_canvas.create_window(x, y, window=frame, anchor="nw")
        self.desktop_icons.append({"id": window_id, "frame": frame, "x": x, "y": y})
    
    def open_file_from_desktop(self, path):
        """باز کردن فایل از دسکتاپ"""
        try:
            # اگه فایل پایتون بود، اجراش کن
            if path.suffix == '.py':
                with open(path, 'r', encoding='utf-8') as f:
                    code = f.read()
                exec(code, {"__name__": "__main__"})
            else:
                # بقیه فایل‌ها با برنامه پیش‌فرض باز بشن
                os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")
    
    def open_folder_from_desktop(self, path):
        """باز کردن پوشه از دسکتاپ"""
        self.current_path = path
        self.open_file_manager()
    
    def show_desktop_icon_menu(self, event, frame):
        """منوی راست کلیک روی آیکون دسکتاپ"""
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["bg_medium"], fg=self.colors["text"])
        menu.add_command(label="Remove from Desktop", command=lambda: frame.destroy())
        menu.add_command(label="Refresh", command=self.load_desktop_items)
        menu.post(event.x_root, event.y_root)
    def open_control_panel(self):
        """کنترل پنل پیشرفته سیستم"""
        cp_window = tk.Toplevel(self.root)
        cp_window.title("PyOS Control Panel")
        cp_window.geometry("700x500")
        cp_window.configure(bg=self.colors["bg_dark"])
        
        # عنوان
        tk.Label(cp_window, text="⚙️ Control Panel", font=("Arial", 18, "bold"),
                bg=self.colors["bg_dark"], fg=self.colors["success"]).pack(pady=15)
        
        # Notebook برای تب‌ها
        notebook = ttk.Notebook(cp_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # استایل Notebook
        style = ttk.Style()
        style.theme_create("pyos_theme", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": self.colors["bg_medium"]}},
            "TNotebook.Tab": {
                "configure": {"padding": [10, 5], "background": self.colors["bg_light"], 
                             "foreground": self.colors["text"]},
                "map": {"background": [("selected", self.colors["accent"])],
                       "foreground": [("selected", self.colors["text"])]}
            }
        })
        style.theme_use("pyos_theme")
        
        # === تب Personalization ===
        personal_tab = tk.Frame(notebook, bg=self.colors["bg_medium"])
        notebook.add(personal_tab, text="🎨 Personalization")
        
        # Wallpaper
        tk.Label(personal_tab, text="Desktop Background", font=("Arial", 12, "bold"),
                bg=self.colors["bg_medium"], fg=self.colors["success"]).pack(pady=10)
        
        wp_frame = tk.Frame(personal_tab, bg=self.colors["bg_medium"])
        wp_frame.pack(pady=5)
        
        def change_wallpaper_color():
            colors = ["#1a1a2e", "#2d2d44", "#1e3a3a", "#3a1e3a", "#2e1e3a"]
            color = simpledialog.askstring("Color", "Enter hex color (e.g., #1a1a2e):")
            if color and color.startswith("#"):
                self.colors["bg_dark"] = color
                self.colors["bg_medium"] = self.adjust_color(color, 10)
                self.save_settings()
                messagebox.showinfo("Success", "Restart PyOS to apply changes")
        
        def select_wallpaper_image():
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                self.settings["wallpaper_path"] = file_path
                self.save_settings()
                messagebox.showinfo("Success", "Wallpaper selected! Restart to apply")
        
        tk.Button(wp_frame, text="Change Color", command=change_wallpaper_color,
                 bg=self.colors["bg_light"], fg=self.colors["text"], width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(wp_frame, text="Select Image", command=select_wallpaper_image,
                 bg=self.colors["bg_light"], fg=self.colors["text"], width=15).pack(side=tk.LEFT, padx=5)
        
        # Theme
        tk.Label(personal_tab, text="Theme", font=("Arial", 12, "bold"),
                bg=self.colors["bg_medium"], fg=self.colors["success"]).pack(pady=10)
        
        theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        themes = [("Dark", "dark"), ("Light", "light"), ("Cyberpunk", "cyberpunk")]
        
        for text, value in themes:
            tk.Radiobutton(personal_tab, text=text, variable=theme_var, value=value,
                          bg=self.colors["bg_medium"], fg=self.colors["text"],
                          selectcolor=self.colors["bg_light"], command=lambda: None).pack()
        
        # === تب Display ===
        display_tab = tk.Frame(notebook, bg=self.colors["bg_medium"])
        notebook.add(display_tab, text="🖥️ Display")
        
        tk.Label(display_tab, text="Screen Resolution", font=("Arial", 12, "bold"),
                bg=self.colors["bg_medium"], fg=self.colors["success"]).pack(pady=10)
        
        res_frame = tk.Frame(display_tab, bg=self.colors["bg_medium"])
        res_frame.pack(pady=10)
        
        resolutions = ["800x600", "1024x768", "1280x720", "1366x768", "1440x900", "1920x1080"]
        res_var = tk.StringVar(value="1024x768")
        
        res_menu = ttk.Combobox(res_frame, textvariable=res_var, values=resolutions, 
                                state="readonly", width=15)
        res_menu.pack()
        
        def apply_resolution():
            res = res_var.get()
            w, h = map(int, res.split('x'))
            self.root.geometry(f"{w}x{h}")
            messagebox.showinfo("Display", f"Resolution changed to {res}")
        
        tk.Button(display_tab, text="Apply Resolution", command=apply_resolution,
                 bg=self.colors["accent"], fg=self.colors["text"]).pack(pady=5)
        
        # === تب Sound & Mic ===
        sound_tab = tk.Frame(notebook, bg=self.colors["bg_medium"])
        notebook.add(sound_tab, text="🔊 Sound")
        
        tk.Label(sound_tab, text="Microphone Settings", font=("Arial", 12, "bold"),
                bg=self.colors["bg_medium"], fg=self.colors["success"]).pack(pady=10)
        
        mic_frame = tk.Frame(sound_tab, bg=self.colors["bg_medium"])
        mic_frame.pack(pady=10)
        
        mic_var = tk.IntVar(value=50)
        
        def record_audio():
            """ضبط صدا بدون نیاز به pyaudio - با winsound و wave"""
            try:
                import wave
                import struct
                import winsound
                
                # ساخت یه فایل صوتی ساده (بیپ)
                filename = self.user_folder / f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                
                # پارامترهای فایل صوتی
                duration = 3  # ثانیه
                freq = 440  # فرکانس (Hz)
                sample_rate = 44100
                num_samples = duration * sample_rate
                
                # ساخت موج سینوسی ساده
                with wave.open(str(filename), 'w') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)   # 2 bytes per sample
                    wav_file.setframerate(sample_rate)
                    
                    for i in range(num_samples):
                        value = int(32767.0 * 0.3 * 
                                   (i * freq / sample_rate) % 1.0 * 2 - 1)  # موج دندانه‌ای
                        data = struct.pack('<h', value)
                        wav_file.writeframes(data)
                
                # پخش صدای ضبط شده
                winsound.PlaySound(str(filename), winsound.SND_FILENAME)
                
                messagebox.showinfo("Success", f"Audio sample created and played!\nSaved to: {filename.name}")
                
            except Exception as e:
                # روش دوم: فقط بیپ سیستم
                try:
                    import winsound
                    winsound.Beep(440, 500)  # بیپ 440Hz برای 0.5 ثانیه
                    winsound.Beep(880, 500)  # بیپ 880Hz
                    messagebox.showinfo("Info", "System beep test played (No real microphone input)")
                except:
                    # روش سوم: بیپ ترمینال
                    print('\a')
                    messagebox.showinfo("Info", "Terminal beep sound (No microphone available)")
        tk.Label(sound_tab, text="Microphone Volume:", bg=self.colors["bg_medium"],
                fg=self.colors["text"]).pack()
        tk.Scale(sound_tab, from_=0, to=100, variable=mic_var, orient=tk.HORIZONTAL,
                bg=self.colors["bg_medium"], fg=self.colors["text"], length=200).pack()
        
        tk.Button(sound_tab, text="🎤 Test Microphone (5s)", command=record_audio,
                 bg=self.colors["accent"], fg=self.colors["text"], width=20).pack(pady=10)
        
        # System Sounds
        tk.Label(sound_tab, text="System Sounds", font=("Arial", 12, "bold"),
                bg=self.colors["bg_medium"], fg=self.colors["success"]).pack(pady=10)
        
        def play_beep():
            try:
                import winsound
                winsound.Beep(440, 500)
            except:
                print('\a')  # Fallback beep
        
        sound_var = tk.BooleanVar(value=True)
        tk.Checkbutton(sound_tab, text="Enable system sounds", variable=sound_var,
                      bg=self.colors["bg_medium"], fg=self.colors["text"],
                      selectcolor=self.colors["bg_light"]).pack()
        tk.Button(sound_tab, text="Test Sound", command=play_beep,
                 bg=self.colors["bg_light"], fg=self.colors["text"]).pack(pady=5)
        
        # === تب System ===
        system_tab = tk.Frame(notebook, bg=self.colors["bg_medium"])
        notebook.add(system_tab, text="💻 System")
        
        # اطلاعات سیستم
        info_frame = tk.Frame(system_tab, bg=self.colors["bg_light"], relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        import platform
        sys_info = f"""
System Information:
• OS: {platform.system()} {platform.release()}
• Machine: {platform.machine()}
• Processor: {platform.processor()}
• Python: {platform.python_version()}
• PyOS User: {self.current_user}
• Home Directory: {self.pyos_home}
"""
        
        tk.Label(info_frame, text=sys_info, bg=self.colors["bg_light"], fg=self.colors["text"],
                font=("Courier", 9), justify=tk.LEFT).pack(padx=10, pady=10)
        
        # دکمه‌های سیستم
        btn_frame = tk.Frame(system_tab, bg=self.colors["bg_medium"])
        btn_frame.pack(pady=10)
        
        def clear_temp():
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir()
                messagebox.showinfo("Success", "Temporary files cleared!")
            except:
                messagebox.showerror("Error", "Cannot clear temp files")
        
        tk.Button(btn_frame, text="🧹 Clear Temp Files", command=clear_temp,
                 bg=self.colors["bg_light"], fg=self.colors["text"], width=18).pack(pady=3)
        tk.Button(btn_frame, text="📊 System Report", command=self.generate_report,
                 bg=self.colors["bg_light"], fg=self.colors["text"], width=18).pack(pady=3)
        
        # دکمه‌های پایین
        bottom_frame = tk.Frame(cp_window, bg=self.colors["bg_dark"])
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def apply_all():
            self.settings["theme"] = theme_var.get()
            self.settings["resolution"] = res_var.get()
            self.save_settings()
            messagebox.showinfo("Settings", "All settings saved!")
            cp_window.destroy()
        
        tk.Button(bottom_frame, text="Apply All", command=apply_all,
                 bg=self.colors["success"], fg=self.colors["bg_dark"],
                 font=("Arial", 10, "bold"), width=15).pack(side=tk.RIGHT, padx=5)
        tk.Button(bottom_frame, text="Cancel", command=cp_window.destroy,
                 bg=self.colors["accent"], fg=self.colors["text"], width=15).pack(side=tk.RIGHT)
        
        self.add_task("Control Panel", cp_window)
    
    def adjust_color(self, hex_color, amount):
        """تیره یا روشن کردن رنگ"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"
    
    def generate_report(self):
        """گزارش سیستم"""
        report_path = self.user_folder / "system_report.txt"
        with open(report_path, 'w') as f:
            f.write(f"PyOS System Report\n")
            f.write(f"Generated: {datetime.datetime.now()}\n")
            f.write(f"{'='*50}\n")
            f.write(f"User: {self.current_user}\n")
            f.write(f"Home: {self.pyos_home}\n")
            f.write(f"Running Tasks: {len(self.running_tasks)}\n")
        messagebox.showinfo("Report", f"Report saved to {report_path}")
    def open_password_gen(self):
        try:
            exec(open(self.apps_dir / "Password_Generator.py", encoding='utf-8').read())
        except:
            messagebox.showerror("Error", "Password Generator not found")
    
    def open_sys_monitor(self):
        try:
            exec(open(self.apps_dir / "System_Monitor.py", encoding='utf-8').read())
        except:
            messagebox.showerror("Error", "System Monitor not found")
# ============================================
# اجرای برنامه
# ============================================
if __name__ == "__main__":
    os_system = PyOSComplete()
    os_system.run()
