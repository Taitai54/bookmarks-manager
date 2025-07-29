import json
import os
import datetime
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import shutil

class BookmarkManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bookmark Manager")
        self.root.geometry("1000x700")

        # Store the original bookmarks file path
        self.bookmarks_file = os.path.join(
            os.getenv('LOCALAPPDATA'),
            'Google/Chrome/User Data/Default/Bookmarks'
        )

        # Load bookmarks
        self.load_bookmarks()

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create search frame
        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_bookmarks)
        ttk.Label(self.search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Create folder filter combobox
        ttk.Label(self.search_frame, text="Filter by Folder:").grid(row=0, column=2, padx=5)
        self.folder_var = tk.StringVar()
        self.folder_combo = ttk.Combobox(self.search_frame, textvariable=self.folder_var, width=30)
        self.folder_combo.grid(row=0, column=3, padx=5)
        self.folder_combo.bind('<<ComboboxSelected>>', self.filter_bookmarks)
        self.update_folder_list()

        # Create treeview with multi-selection enabled
        self.tree = ttk.Treeview(self.main_frame, columns=('Name', 'URL', 'Folder'), show='headings', selectmode='extended')
        self.tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure treeview columns
        self.tree.heading('Name', text='Name', command=lambda: self.sort_treeview('Name', False))
        self.tree.heading('URL', text='URL', command=lambda: self.sort_treeview('URL', False))
        self.tree.heading('Folder', text='Folder', command=lambda: self.sort_treeview('Folder', False))
        self.tree.column('Name', width=250)
        self.tree.column('URL', width=450)
        self.tree.column('Folder', width=200)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Buttons frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # Buttons
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected, style='Delete.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Backup Bookmarks", command=self.backup_bookmarks).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Style configuration
        style = ttk.Style()
        style.configure('Delete.TButton', foreground='red')

        # Populate treeview
        self.populate_tree()

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.search_frame.columnconfigure(1, weight=1)

    def load_bookmarks(self):
        try:
            with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.bookmarks = []
            self.process_node(self.data['roots']['bookmark_bar'], "Bookmark Bar")
            self.process_node(self.data['roots']['other'], "Other Bookmarks")
            self.process_node(self.data['roots']['synced'], "Mobile Bookmarks")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bookmarks: {str(e)}")
            self.bookmarks = []

    def process_node(self, node, parent_folder=""):
        if node.get('type') == 'url':
            self.bookmarks.append({
                'name': node.get('name', ''),
                'url': node.get('url', ''),
                'folder': parent_folder,
                'id': node.get('id', '')
            })
        elif node.get('type') == 'folder':
            for child in node.get('children', []):
                self.process_node(child, node.get('name', ''))

    def update_folder_list(self):
        folders = sorted(list(set(b['folder'] for b in self.bookmarks)))
        folders.insert(0, "All Folders")
        self.folder_combo['values'] = folders
        self.folder_combo.set("All Folders")

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for bookmark in self.bookmarks:
            self.tree.insert('', 'end', values=(
                bookmark['name'],
                bookmark['url'],
                bookmark['folder']
            ))

        self.update_status()

    def filter_bookmarks(self, *args):
        search_term = self.search_var.get().lower()
        selected_folder = self.folder_var.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for bookmark in self.bookmarks:
            if selected_folder != "All Folders" and bookmark['folder'] != selected_folder:
                continue

            if (search_term in bookmark['name'].lower() or
                search_term in bookmark['url'].lower() or
                search_term in bookmark['folder'].lower()):
                self.tree.insert('', 'end', values=(
                    bookmark['name'],
                    bookmark['url'],
                    bookmark['folder']
                ))

        self.update_status()

    def backup_bookmarks(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'bookmarks_backup_{timestamp}.json'
        try:
            shutil.copy2(self.bookmarks_file, backup_file)
            messagebox.showinfo("Success", f"Bookmarks backed up to {backup_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to backup bookmarks: {str(e)}")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No bookmarks selected for deletion!")
            return

        if not messagebox.askyesno("Confirm Deletion",
                                   "Are you sure you want to delete the selected bookmarks? This cannot be undone!"):
            return

        # Backup before deletion
        self.backup_bookmarks()

        # Get the URLs of selected items
        selected_urls = set()
        for item in selected_items:
            values = self.tree.item(item)['values']
            selected_urls.add(values[1])  # URL is at index 1

        # Remove selected bookmarks from self.bookmarks
        self.bookmarks = [b for b in self.bookmarks if b['url'] not in selected_urls]

        # Update Chrome's bookmark file
        self.update_chrome_bookmarks()

        # Refresh the display
        self.populate_tree()
        messagebox.showinfo("Success", "Selected bookmarks have been deleted")

    def update_chrome_bookmarks(self):
        """Update the Chrome bookmarks file."""
        def remove_bookmarks(node):
            if 'children' in node:
                node['children'] = [remove_bookmarks(child) for child in node['children'] if child.get('url') not in selected_urls]
                node['children'] = [child for child in node['children'] if child]  # Remove None entries
            return node

        selected_urls = {b['url'] for b in self.bookmarks}
        self.data['roots']['bookmark_bar'] = remove_bookmarks(self.data['roots']['bookmark_bar'])
        self.data['roots']['other'] = remove_bookmarks(self.data['roots']['other'])
        self.data['roots']['synced'] = remove_bookmarks(self.data['roots']['synced'])

        try:
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
            print("Bookmarks file updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update bookmarks: {str(e)}")

    def sort_treeview(self, column, reverse):
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        items.sort(reverse=reverse)
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        self.tree.heading(column, command=lambda: self.sort_treeview(column, not reverse))

    def select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def deselect_all(self):
        for item in self.tree.get_children():
            self.tree.selection_remove(item)

    def update_status(self):
        visible_items = len(self.tree.get_children())
        total_items = len(self.bookmarks)
        self.status_var.set(f"Showing {visible_items} of {total_items} bookmarks")

def main():
    root = tk.Tk()
    app = BookmarkManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()