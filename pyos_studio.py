import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog, colorchooser
from pathlib import Path
import os
import re
import subprocess
import sys

class ProfessionalIDE:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("PyOS Studio")
        self.root.geometry("1000x700")
        
        # متغیرها
        self.open_tabs = {}  # {tab_id: {"file": path, "content": text_widget, "modified": bool}}
        self.current_tab = None
        self.current_theme = "dark"
        self.current_language = "python"
        self.workspace_path = Path.home()
        
        # رنگ‌های تم
        self.themes = {
            "dark": {
                "bg": "#1e1e2e", "editor_bg": "#282a36", "sidebar_bg": "#21222c",
                "text": "#f8f8f2", "keyword": "#ff79c6", "string": "#f1fa8c",
                "comment": "#6272a4", "function": "#50fa7b", "number": "#bd93f9",
                "line_numbers": "#6272a4", "selection": "#44475a"
            },
            "light": {
                "bg": "#f5f5f5", "editor_bg": "#ffffff", "sidebar_bg": "#e8e8e8",
                "text": "#000000", "keyword": "#0000ff", "string": "#a31515",
                "comment": "#008000", "function": "#795e26", "number": "#098658",
                "line_numbers": "#237893", "selection": "#add6ff"
            }
        }
        
        self.setup_ui()
        self.setup_syntax_keywords()
        self.bind_shortcuts()
        
    def setup_syntax_keywords(self):
        self.keywords = {
            "python": {
                "keywords": ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break',
                            'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
                            'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
                            'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'],
                "builtins": ['abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir', 'divmod',
                            'enumerate', 'filter', 'float', 'format', 'getattr', 'hasattr', 'hash',
                            'hex', 'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len',
                            'list', 'map', 'max', 'min', 'next', 'oct', 'open', 'ord', 'pow', 'print',
                            'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
                            'str', 'sum', 'tuple', 'type', 'vars', 'zip']
            },
            "html": {
                "keywords": ['html', 'head', 'body', 'div', 'span', 'p', 'a', 'img', 'ul', 'ol', 'li',
                            'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'script', 'style']
            },
            "javascript": {
                "keywords": ['break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default',
                            'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function',
                            'if', 'import', 'in', 'instanceof', 'new', 'return', 'super', 'switch',
                            'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield']
            }
        }
        
    def setup_ui(self):
        colors = self.themes[self.current_theme]
        self.root.configure(bg=colors["bg"])
        
        # ========== منو بار ==========
        menubar = tk.Menu(self.root, bg=colors["sidebar_bg"], fg=colors["text"])
        self.root.config(menu=menubar)
        
        # منوی File
        file_menu = tk.Menu(menubar, tearoff=0, bg=colors["sidebar_bg"], fg=colors["text"])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=lambda: self.new_file(), accelerator="Ctrl+N")
        file_menu.add_command(label="Open File...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Folder...", command=self.open_folder, accelerator="Ctrl+K Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Save All", command=self.save_all, accelerator="Ctrl+K S")
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", command=self.close_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Exit", command=self.root.destroy, accelerator="Alt+F4")
        
        # منوی Edit
        edit_menu = tk.Menu(menubar, tearoff=0, bg=colors["sidebar_bg"], fg=colors["text"])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.show_find_replace, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=lambda: self.show_find_replace(replace=True), accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Format Document", command=self.format_code, accelerator="Shift+Alt+F")
        
        # منوی View
        view_menu = tk.Menu(menubar, tearoff=0, bg=colors["sidebar_bg"], fg=colors["text"])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Sidebar", command=self.toggle_sidebar, accelerator="Ctrl+B")
        view_menu.add_command(label="Toggle Terminal", command=self.toggle_terminal, accelerator="Ctrl+`")
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl+=")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_separator()
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0, bg=colors["sidebar_bg"], fg=colors["text"])
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Dark", command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label="Light", command=lambda: self.change_theme("light"))
        
        # Language submenu
        lang_menu = tk.Menu(view_menu, tearoff=0, bg=colors["sidebar_bg"], fg=colors["text"])
        view_menu.add_cascade(label="Language", menu=lang_menu)
        lang_menu.add_command(label="Python", command=lambda: self.change_language("python"))
        lang_menu.add_command(label="HTML", command=lambda: self.change_language("html"))
        lang_menu.add_command(label="JavaScript", command=lambda: self.change_language("javascript"))
        lang_menu.add_command(label="Plain Text", command=lambda: self.change_language("text"))
        
        # منوی Run
        run_menu = tk.Menu(menubar, tearoff=0, bg=colors["sidebar_bg"], fg=colors["text"])
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run File", command=self.run_file, accelerator="F5")
        run_menu.add_command(label="Run with Arguments", command=self.run_with_args)
        run_menu.add_separator()
        run_menu.add_command(label="Stop Execution", command=self.stop_execution, accelerator="Ctrl+F5")
        
        # ========== نوار ابزار اصلی ==========
        self.toolbar = tk.Frame(self.root, bg=colors["sidebar_bg"], height=35)
        self.toolbar.pack(fill=tk.X, side=tk.TOP)
        
        tools = [
            ("📄", self.new_file), ("📂", self.open_file), ("💾", self.save_file),
            ("✂️", self.cut), ("📋", self.copy), ("📌", self.paste),
            ("↩️", self.undo), ("↪️", self.redo), ("▶", self.run_file)
        ]
        for icon, cmd in tools:
            btn = tk.Button(self.toolbar, text=icon, command=cmd, bg=colors["sidebar_bg"],
                           fg=colors["text"], relief=tk.FLAT, font=("Arial", 12), width=3)
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # ========== Paned Window اصلی ==========
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=colors["bg"])
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        
        # ========== Sidebar (File Explorer) ==========
        self.sidebar = tk.Frame(self.main_pane, bg=colors["sidebar_bg"], width=200)
        self.main_pane.add(self.sidebar, width=200)
        
        # هدر File Explorer
        sidebar_header = tk.Frame(self.sidebar, bg=colors["sidebar_bg"], height=30)
        sidebar_header.pack(fill=tk.X)
        tk.Label(sidebar_header, text="EXPLORER", bg=colors["sidebar_bg"], fg=colors["text"],
                font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=10)
        
        # Treeview فایل‌ها
        self.file_tree = ttk.Treeview(self.sidebar, show="tree", height=20)
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_tree.bind("<Double-1>", self.open_from_tree)
        
        # ========== Editor Area ==========
        self.editor_pane = tk.PanedWindow(self.main_pane, orient=tk.VERTICAL, bg=colors["bg"])
        self.main_pane.add(self.editor_pane)
        
        # Tab Control برای فایل‌های باز
        self.tab_control = ttk.Notebook(self.editor_pane)
        self.editor_pane.add(self.tab_control, height=500)
        
        # استایل تب‌ها
        style = ttk.Style()
        style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=colors["sidebar_bg"], 
                       foreground=colors["text"], padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", colors["keyword"])])
        
        # ========== Terminal Panel ==========
        self.terminal_frame = tk.Frame(self.editor_pane, bg=colors["editor_bg"], height=150)
        self.editor_pane.add(self.terminal_frame)
        
        terminal_header = tk.Frame(self.terminal_frame, bg=colors["sidebar_bg"], height=25)
        terminal_header.pack(fill=tk.X)
        tk.Label(terminal_header, text="TERMINAL", bg=colors["sidebar_bg"], fg=colors["text"],
                font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.terminal = scrolledtext.ScrolledText(self.terminal_frame, 
                                                  bg=colors["editor_bg"], fg=colors["text"],
                                                  font=("Consolas", 10), height=6)
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
        # ========== Status Bar ==========
        self.status_bar = tk.Label(self.root, text="Ready", bg=colors["sidebar_bg"], 
                                   fg=colors["text"], anchor=tk.W, font=("Arial", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # تب اول (welcome)
        self.new_file()
        
    def create_editor_tab(self, title="Untitled", content=""):
        colors = self.themes[self.current_theme]
        
        # فریم تب
        tab_frame = tk.Frame(self.tab_control, bg=colors["editor_bg"])
        self.tab_control.add(tab_frame, text=title)
        
        # شماره خطوط
        line_numbers = tk.Text(tab_frame, width=4, padx=5, pady=5,
                              bg=colors["editor_bg"], fg=colors["line_numbers"],
                              font=("Consolas", 11), state=tk.DISABLED, wrap=tk.NONE)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # ادیتور اصلی
        text_widget = scrolledtext.ScrolledText(tab_frame, 
                                               bg=colors["editor_bg"], fg=colors["text"],
                                               insertbackground=colors["text"],
                                               font=("Consolas", 11),
                                               undo=True, maxundo=100,
                                               wrap=tk.NONE)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, content)
        
        # ذخیره اطلاعات تب
        tab_id = str(len(self.open_tabs))
        self.open_tabs[tab_id] = {
            "frame": tab_frame,
            "text": text_widget,
            "line_numbers": line_numbers,
            "file": None,
            "modified": False,
            "language": "python"
        }
        
        # تنظیمات syntax highlighting
        self.setup_editor_tags(text_widget)
        
        # Bindings
        text_widget.bind("<KeyRelease>", lambda e, tid=tab_id: self.on_text_change(tid))
        text_widget.bind("<ButtonRelease-1>", lambda e, tid=tab_id: self.update_status(tid))
        text_widget.bind("<<Modified>>", lambda e, tid=tab_id: self.on_modify(tid))
        
        # انتخاب تب جدید
        self.tab_control.select(tab_frame)
        self.current_tab = tab_id
        text_widget.focus()
        
        return tab_id
    
    def setup_editor_tags(self, text_widget):
        colors = self.themes[self.current_theme]
        text_widget.tag_config("keyword", foreground=colors["keyword"])
        text_widget.tag_config("string", foreground=colors["string"])
        text_widget.tag_config("comment", foreground=colors["comment"])
        text_widget.tag_config("function", foreground=colors["function"])
        text_widget.tag_config("number", foreground=colors["number"])
        text_widget.tag_config("selection", background=colors["selection"])
    
    def on_text_change(self, tab_id):
        if tab_id not in self.open_tabs:
            return
        tab = self.open_tabs[tab_id]
        self.update_line_numbers(tab_id)
        self.highlight_syntax(tab_id)
        self.update_status(tab_id)
    
    def update_line_numbers(self, tab_id):
        tab = self.open_tabs[tab_id]
        lines = tab["text"].get(1.0, tk.END).count('\n')
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))
        
        tab["line_numbers"].config(state=tk.NORMAL)
        tab["line_numbers"].delete(1.0, tk.END)
        tab["line_numbers"].insert(1.0, line_numbers_text)
        tab["line_numbers"].config(state=tk.DISABLED)
    
    def highlight_syntax(self, tab_id):
        tab = self.open_tabs[tab_id]
        text_widget = tab["text"]
        lang = tab["language"]
        
        # پاک کردن رنگ‌های قبلی
        for tag in ["keyword", "string", "comment", "function", "number"]:
            text_widget.tag_remove(tag, 1.0, tk.END)
        
        if lang not in self.keywords:
            return
            
        content = text_widget.get(1.0, tk.END)
        keyword_list = self.keywords[lang].get("keywords", [])
        
        # رنگ‌آمیزی کلمات کلیدی
        for keyword in keyword_list:
            start = 1.0
            while True:
                pos = text_widget.search(r'\y' + keyword + r'\y', start, tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                text_widget.tag_add("keyword", pos, end)
                start = end
        
        # رنگ‌آمیزی رشته‌ها (با regex ساده)
        self.highlight_pattern(text_widget, r'"[^"\\]*(\\.[^"\\]*)*"', "string")
        self.highlight_pattern(text_widget, r"'[^'\\]*(\\.[^'\\]*)*'", "string")
        
        # رنگ‌آمیزی کامنت‌ها
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '#' in line:
                pos = line.find('#')
                if pos >= 0:
                    start = f"{i+1}.{pos}"
                    end = f"{i+1}.{len(line)}"
                    text_widget.tag_add("comment", start, end)
        
        # رنگ‌آمیزی اعداد
        self.highlight_pattern(text_widget, r'\b\d+\b', "number")
    
    def highlight_pattern(self, text_widget, pattern, tag):
        start = 1.0
        while True:
            pos = text_widget.search(pattern, start, tk.END, regexp=True)
            if not pos:
                break
            end = f"{pos}+{len(text_widget.get(pos, f'{pos} lineend'))}c"
            text_widget.tag_add(tag, pos, end)
            start = end
    
    def on_modify(self, tab_id):
        tab = self.open_tabs[tab_id]
        if tab["text"].edit_modified():
            tab["modified"] = True
            self.update_tab_title(tab_id)
            tab["text"].edit_modified(False)
    
    def update_tab_title(self, tab_id):
        tab = self.open_tabs[tab_id]
        filename = Path(tab["file"]).name if tab["file"] else "Untitled"
        modified = " ●" if tab["modified"] else ""
        self.tab_control.tab(tab["frame"], text=f"{filename}{modified}")
    
    def update_status(self, tab_id):
        if tab_id not in self.open_tabs:
            return
        tab = self.open_tabs[tab_id]
        content = tab["text"].get(1.0, tk.END)
        lines = content.count('\n')
        chars = len(content) - 1
        cursor_pos = tab["text"].index(tk.INSERT)
        
        lang = tab["language"].upper()
        self.status_bar.config(text=f"Ln {cursor_pos.split('.')[0]}, Col {cursor_pos.split('.')[1]} | "
                               f"Lines: {lines} | Chars: {chars} | {lang}")
    
    def new_file(self):
        self.create_editor_tab("Untitled")
    
    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            tab_id = self.create_editor_tab(Path(path).name, content)
            self.open_tabs[tab_id]["file"] = path
            self.open_tabs[tab_id]["modified"] = False
            
            # تشخیص زبان
            ext = Path(path).suffix
            if ext == '.py':
                self.open_tabs[tab_id]["language"] = "python"
            elif ext in ['.html', '.htm']:
                self.open_tabs[tab_id]["language"] = "html"
            elif ext == '.js':
                self.open_tabs[tab_id]["language"] = "javascript"
            
            self.update_tab_title(tab_id)
            self.highlight_syntax(tab_id)
    
    def open_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.workspace_path = Path(path)
            self.refresh_file_tree()
    
    def refresh_file_tree(self):
        self.file_tree.delete(*self.file_tree.get_children())
        root_node = self.file_tree.insert("", "end", text=self.workspace_path.name, 
                                          open=True, values=[str(self.workspace_path)])
        self.add_tree_nodes(root_node, self.workspace_path)
    
    def add_tree_nodes(self, parent, path):
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                node = self.file_tree.insert(parent, "end", text=item.name, values=[str(item)])
                if item.is_dir():
                    self.add_tree_nodes(node, item)
        except PermissionError:
            pass
    
    def open_from_tree(self, event):
        selection = self.file_tree.selection()
        if selection:
            path = self.file_tree.item(selection[0])['values'][0]
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tab_id = self.create_editor_tab(Path(path).name, content)
                self.open_tabs[tab_id]["file"] = path
                self.update_tab_title(tab_id)
    
    def save_file(self):
        if not self.current_tab:
            return
        tab = self.open_tabs[self.current_tab]
        
        if not tab["file"]:
            self.save_as_file()
            return
        
        with open(tab["file"], 'w', encoding='utf-8') as f:
            f.write(tab["text"].get(1.0, tk.END))
        tab["modified"] = False
        self.update_tab_title(self.current_tab)
        self.terminal.insert(tk.END, f"✓ Saved: {tab['file']}\n")
    
    def save_as_file(self):
        if not self.current_tab:
            return
        path = filedialog.asksaveasfilename()
        if path:
            tab = self.open_tabs[self.current_tab]
            tab["file"] = path
            self.save_file()
    
    def save_all(self):
        for tab_id in self.open_tabs:
            if self.open_tabs[tab_id]["modified"]:
                self.current_tab = tab_id
                self.save_file()
    
    def close_tab(self):
        if len(self.open_tabs) <= 1:
            return
        if self.current_tab:
            self.tab_control.forget(self.open_tabs[self.current_tab]["frame"])
            del self.open_tabs[self.current_tab]
            if self.open_tabs:
                self.current_tab = list(self.open_tabs.keys())[-1]
    
    def undo(self):
        if self.current_tab:
            self.open_tabs[self.current_tab]["text"].edit_undo()
    
    def redo(self):
        if self.current_tab:
            self.open_tabs[self.current_tab]["text"].edit_redo()
    
    def cut(self):
        if self.current_tab:
            self.open_tabs[self.current_tab]["text"].event_generate("<<Cut>>")
    
    def copy(self):
        if self.current_tab:
            self.open_tabs[self.current_tab]["text"].event_generate("<<Copy>>")
    
    def paste(self):
        if self.current_tab:
            self.open_tabs[self.current_tab]["text"].event_generate("<<Paste>>")
    
    def select_all(self):
        if self.current_tab:
            self.open_tabs[self.current_tab]["text"].tag_add(tk.SEL, 1.0, tk.END)
    
    def show_find_replace(self, replace=False):
        if not self.current_tab:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Find and Replace" if replace else "Find")
        dialog.geometry("400x150")
        colors = self.themes[self.current_theme]
        dialog.configure(bg=colors["bg"])
        
        tk.Label(dialog, text="Find:", bg=colors["bg"], fg=colors["text"]).pack(pady=5)
        find_entry = tk.Entry(dialog, bg=colors["editor_bg"], fg=colors["text"], width=40)
        find_entry.pack(pady=5)
        find_entry.focus()
        
        if replace:
            tk.Label(dialog, text="Replace with:", bg=colors["bg"], fg=colors["text"]).pack(pady=5)
            replace_entry = tk.Entry(dialog, bg=colors["editor_bg"], fg=colors["text"], width=40)
            replace_entry.pack(pady=5)
        
        def do_find():
            text = find_entry.get()
            if text:
                tab = self.open_tabs[self.current_tab]
                start = tab["text"].search(text, 1.0, tk.END)
                if start:
                    end = f"{start}+{len(text)}c"
                    tab["text"].tag_remove(tk.SEL, 1.0, tk.END)
                    tab["text"].tag_add(tk.SEL, start, end)
                    tab["text"].mark_set(tk.INSERT, end)
                    tab["text"].see(start)
        
        btn_text = "Replace All" if replace else "Find Next"
        btn_cmd = do_find
        tk.Button(dialog, text=btn_text, command=btn_cmd, 
                 bg=colors["keyword"], fg=colors["text"]).pack(pady=10)
        find_entry.bind("<Return>", lambda e: btn_cmd())
    
    def format_code(self):
        # فرمت ساده (فعلاً indent مرتب)
        messagebox.showinfo("Format", "Auto-format coming soon!")
    
    def toggle_sidebar(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y, before=self.editor_pane)
    
    def toggle_terminal(self):
        if self.terminal_frame.winfo_viewable():
            self.terminal_frame.pack_forget()
        else:
            self.terminal_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    def zoom_in(self):
        if self.current_tab:
            tab = self.open_tabs[self.current_tab]
            font = tab["text"].cget("font")
            size = int(font[1]) + 2 if len(font) > 1 else 13
            tab["text"].config(font=("Consolas", size))
    
    def zoom_out(self):
        if self.current_tab:
            tab = self.open_tabs[self.current_tab]
            font = tab["text"].cget("font")
            size = max(8, int(font[1]) - 2) if len(font) > 1 else 11
            tab["text"].config(font=("Consolas", size))
    
    def change_theme(self, theme):
        self.current_theme = theme
        messagebox.showinfo("Theme", "Theme will apply after restart")
    
    def change_language(self, lang):
        if self.current_tab:
            self.open_tabs[self.current_tab]["language"] = lang
            self.highlight_syntax(self.current_tab)
            self.update_status(self.current_tab)
    
    def run_file(self):
        if not self.current_tab:
            return
        tab = self.open_tabs[self.current_tab]
        
        if tab["modified"]:
            self.save_file()
        
        if not tab["file"]:
            messagebox.showerror("Error", "Save file first")
            return
        
        self.terminal.insert(tk.END, f"\n> Running: {tab['file']}\n")
        self.terminal.insert(tk.END, "=" * 50 + "\n")
        
        try:
            result = subprocess.run([sys.executable, tab["file"]], 
                                   capture_output=True, text=True, timeout=10)
            self.terminal.insert(tk.END, result.stdout)
            if result.stderr:
                self.terminal.insert(tk.END, result.stderr)
        except Exception as e:
            self.terminal.insert(tk.END, f"Error: {e}\n")
        
        self.terminal.see(tk.END)
    
    def run_with_args(self):
        args = simpledialog.askstring("Arguments", "Enter arguments:")
        self.terminal.insert(tk.END, f"Arguments: {args}\n")
        self.run_file()
    
    def stop_execution(self):
        self.terminal.insert(tk.END, "\n> Execution stopped\n")
    
    def bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-w>', lambda e: self.close_tab())
        self.root.bind('<Control-f>', lambda e: self.show_find_replace())
        self.root.bind('<Control-h>', lambda e: self.show_find_replace(replace=True))
        self.root.bind('<F5>', lambda e: self.run_file())
        self.root.bind('<Control-b>', lambda e: self.toggle_sidebar())

def main():
    ide = ProfessionalIDE()
    ide.root.mainloop()

if __name__ == "__main__":
    main()
else:
    main()
