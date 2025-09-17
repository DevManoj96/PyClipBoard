import pyperclip
import tkinter as tk
from tkinter import font, simpledialog, messagebox

default_font = ("Segoe UI", 12)
FILENAME = "clipboard_history.txt"
counter = {'n': 1}

raw_clip = []

class PyClipBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("PyClipBoard") 
        self.root.geometry('480x480')
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        self.current_font = font.Font(family="Segoe UI", size=12)
        
        self.last_clip = None

        # File Menu Entries
        self.filemenu = tk.Menu(self.menubar, tearoff=0, font=default_font)
        self.filemenu.add_command(label="New Item", command=self.new_item, font=default_font)
        self.filemenu.add_command(label="Save", command=self.save_clipboard, font=default_font)
        self.filemenu.add_command(label="Exit", command=self.quit_clipboard, font=default_font)

        # Edit Menu Entries
        self.editmenu = tk.Menu(self.menubar, tearoff=0, font=default_font)
        self.editmenu.add_command(label="Find", command=self.find_text, font=default_font)
        self.editmenu.add_command(label="Sort Items", command=self.sort_items, font=default_font)
        self.editmenu.add_command(label="Reverse Items", command=self.reverse_items, font=default_font)
        self.editmenu.add_command(label="Copy", command=self.copy_text, font=default_font)
        self.editmenu.add_command(label="Paste", command=self.paste_text, font=default_font)
        self.editmenu.add_command(label="Toggle Theme", command=self.toggle_theme, font=default_font)

        # Item Menu Entries
        self.itemmenu = tk.Menu(self.menubar, tearoff=0, font=default_font)
        self.itemmenu.add_command(label="Remove", command=self.remove_text, font=default_font)
        self.itemmenu.add_command(label="Remove All", command=self.remove_all, font=default_font)


        # Help Menu Entries
        self.helpmenu = tk.Menu(self.menubar, tearoff=0, font=default_font)
        self.helpmenu.add_command(label="About", command=self.show_about, font=default_font)
        self.helpmenu.add_command(label="Help", command=self.show_help, font=default_font)
        self.helpmenu.add_command(label="Shortcuts", command=self.show_shortcuts, font=default_font)

        # Main Menu
        self.menubar.add_cascade(label="File", menu=self.filemenu, font=default_font)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu, font=default_font)
        self.menubar.add_cascade(label="Items", menu=self.itemmenu, font=default_font)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu, font=default_font)
        
        self.textarea = tk.Text(self.root, font=self.current_font)
        self.textarea.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.textarea.config(state='disabled')

        self.is_dark = False
        self.toggle_theme()
        self.clipboard_inputs()

        self.bindings()

    def clipboard_inputs(self):
        try:
            text = self.root.clipboard_get()
            if text and text != self.last_clip and text.strip():
                self.add_numbered_multiline(text)
                raw_clip.append(text)
            self.last_clip = text
        except tk.TclError:
            pass

        self.root.after(500, self.clipboard_inputs)

    def new_item(self):
        item = simpledialog.askstring("New Item", "Text: ")
        if item:
            self.add_numbered_multiline(item)
            raw_clip.append(item)

    def add_numbered_multiline(self, s):
        for line in s.splitlines():
            if line.strip():
                self.textarea.config(state='normal')
                self.textarea.insert('end', f"{counter['n']}. {line}\n")
                counter['n'] += 1
        self.textarea.config(state='disabled')
        

    def save_clipboard(self):
        try:
            with open(FILENAME, "w") as f:
                content = self.textarea.get(0, tk.END)
                if content:
                    f.write(content.strip() + "\n")
                    messagebox.showinfo("Saved", "File Saved Successfully.")
        except Exception as e:
            print(f"[Error]: {e}")

    def find_text(self):
        find_txt = simpledialog.askstring("Find", "Enter text to find:", parent=self.root)
        self.textarea.tag_remove('found', '1.0', tk.END)
        if find_txt:
            start_index = self.textarea.search(find_txt, "1.0", stopindex="end")
            if start_index:
                end_index = f"{start_index}+{len(find_txt)}c"
                self.textarea.tag_add('found', start_index, end_index)
                self.textarea.see(start_index)

            self.textarea.tag_config('found', foreground='white', background='blue')

        self.root.after(15000, lambda: self.textarea.tag_delete('found'))

    def sort_items(self):
        content = list(raw_clip)        
        content.sort()
        
        self.textarea.config(state='normal')
        self.textarea.delete("1.0", "end")
        counter['n'] = 1
        raw_clip.clear()
        for i in content:
            self.add_numbered_multiline(i)
            raw_clip.append(i)
        self.textarea.config(state='disabled')

    def reverse_items(self):
        clip = list(raw_clip)
        rev_item = list(reversed(clip))
        print(f"REVERSE: {rev_item}")

        self.textarea.config(state='normal')
        self.textarea.delete("1.0", "end")
        counter['n'] = 1
        raw_clip.clear()
        for i in rev_item:
            self.add_numbered_multiline(i)
            raw_clip.append(i)
        self.textarea.config(state='disabled')

    def copy_text(self):
        try:
            text = self.textarea.selection_get()
            pyperclip.copy(text)
        except tk.TclError:
            pass

    def paste_text(self):
        text = self.root.clipboard_get()
        if not text:
            text = simpledialog.askstring("Paste", "Enter text to paste:")

        self.add_numbered_multiline(text)
        raw_clip.append(text)

    def remove_text(self):
        rm_idx = simpledialog.askinteger("Remove", "Enter index to remove:")
        if rm_idx is None:
            return

        pattern = rf"^{rm_idx}\.\s"
        pos = self.textarea.search(pattern, "1.0", tk.END, regexp=True)

        if not pos:
            return

        start = pos
        end = f"{pos} lineend+1c"
        self.textarea.config(state='normal')
        self.textarea.delete(start, end)

        lines = self.textarea.get("1.0", "end-1c").splitlines()

        self.textarea.delete("1.0", "end")

        counter['n'] = 1
        raw_clip.clear()
        for line in lines:
            parts = line.split(maxsplit=1)
            if parts and parts[0].endswith('.'):
                text = parts[1] if len(parts) >1 else ""
            else:
                text = line
            self.add_numbered_multiline(text)
            raw_clip.append(text)

        self.textarea.config(state='disabled')


    def remove_all(self):
        raw_clip.clear()
        counter['n'] = 1
        self.textarea.config(state='normal')
        self.textarea.delete("1.0", tk.END)
        self.textarea.config(state='disabled')

    def toggle_theme(self):
        dark_theme = {
            "background": "#222831",       # dark gray-blue
            "foreground": "#EEEEEE",       # soft white
            "insertbackground": "#00ADB5", # teal caret
            "txt_background": "#393E46",   # editor background
            "txt_foreground": "#FFFFFF",   # text color
            "highlight": "#58A6FF",      # semi-transparent teal selection
            "status": "#222831"            # status bar
        }

        light_theme = {
            "background": "#F8F9FA",       # light gray
            "foreground": "#212529",       # dark text
            "insertbackground": "#0D6EFD", # blue caret
            "txt_background": "#FFFFFF",   # editor background
            "txt_foreground": "#212529",   # text color
            "highlight": "#58A6FF",        # light blue selection
            "status": "#E9ECEF"            # status bar
        }       

        self.is_dark = not self.is_dark
        theme = dark_theme if self.is_dark else light_theme

        self.root.config(bg=theme["background"])
        self.menubar.config(fg=theme["foreground"], bg=theme["background"], activebackground=theme["highlight"])
        self.filemenu.config(fg=theme["foreground"], bg=theme["background"], activebackground=theme["highlight"])
        self.editmenu.config(fg=theme["foreground"], bg=theme["background"], activebackground=theme["highlight"])
        self.itemmenu.config(fg=theme["foreground"], bg=theme["background"], activebackground=theme["highlight"])
        self.helpmenu.config(fg=theme["foreground"], bg=theme["background"], activebackground=theme["highlight"])

        self.textarea.config(
            fg=theme["txt_foreground"],
            bg=theme["txt_background"],
            insertbackground=theme["insertbackground"],
            selectbackground=theme["highlight"]
        )

    def bindings(self):
        self.root.bind('<Control-n>', lambda _: self.new_item())
        self.root.bind('<Control-s>', lambda _: self.save_clipboard())
        self.root.bind('<Control-q>', lambda _: self.quit_clipboard())
        self.root.bind('<Control-f>', lambda _: self.find_text())
        self.root.bind('<Control-Shift-S>', lambda _: self.sort_items())
        self.root.bind('<Control-Shift-R>', lambda _: self.reverse_items())
        self.root.bind('<Control-c>', lambda _: self.copy_text())
        self.root.bind('<Control-v>', lambda _: self.paste_text())
        self.root.bind('<Control-t>', lambda _: self.toggle_theme())
        self.root.bind('<Delete>', lambda _: self.remove_text())
        self.root.bind('<Shift-Delete>', lambda _: self.remove_all())
        self.root.bind('<Control-a>', lambda _: self.show_about())
        self.root.bind('<Control-h>', lambda _: self.show_help())

    def quit_clipboard(self):
        self.save_clipboard()
        self.root.quit()

    def show_about(self):
        about = """PyClipBoard v1.0
        
PyClipBoard is a lightweight clipboard manager made for storing all the content very easily, it's main goal to provide users a light and easy to use clipboard manager.

Feel free to help me improve it.
github: {URL}
        """
        messagebox.showinfo(
            "About",
            about
        )

    def show_help(self):
        help_txt = """Help Menu:

New item: Make a new item in clipboard manager
Save: Saves the clipboard as 'clipboard_history.txt'.

Find: Finds a perticular word in clipboard and highlights it.
Sort items: Sort all the items of clipboard.
Reverse items: Reverse all the items of clipboard.
Copy: Copy selected text.
Paste: Paste text from system clipboard.
Toggle theme: Toggle Theme between dark mode and light mode

Remove: Remove a perticular line in clipboard.
Remove All: Remove all the items from the clipboard.

About: Show about.
Help: Show help.
        """

        messagebox.showinfo(
            "Help",
            help_txt
        )

    def show_shortcuts(self):
        shortcuts = """Shortcuts:

Ctrl + n: New item.
Ctrl + s: Save clipboard as a file.
Ctrl + q: Quits the clipboard.
Ctrl + f: Find.
Ctrl + Shift + S: Sort Items.
Ctrl + Shift + R: Reverse Items.
Ctrl + c: Copy Text.
Ctrl + v: Paste Text.
Ctrl + t: Toggle Theme.
Delete: Delete a line.
Shift + Delete: Delete all the items.
Ctrl + a: Show About.
Ctrl + h: Show Help.
        """

        messagebox.showinfo(
            "Shortcuts",
            shortcuts
        )
if __name__ == "__main__":
    root = tk.Tk()
    app = PyClipBoard(root)
    root.mainloop()