"""The utility window: open a journal, sort the entries with the model, save the result to Excel."""
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from journal_ai import process_journal, write_summary
from journal_io import read_journal, save_results
from local_llm import load_chat

ROOT = Path(__file__).resolve().parent


class JournalApp:
    def __init__(self, window: tk.Tk, model):
        self.window = window
        self.model = model
        self.path = None
        self.entries, self.results, self.summary = [], [], ''
        # The model works in a separate thread and reports progress through a queue.
        self.events = queue.Queue()
        window.title("The cat's mischief journal")
        buttons = ttk.Frame(window, padding=8)
        buttons.pack(fill='x')
        self.open_button = ttk.Button(buttons, text='Open journal', command=self.open_file)
        self.run_button = ttk.Button(buttons, text='Sort entries', command=self.start, state='disabled')
        self.save_button = ttk.Button(buttons, text='Save to Excel', command=self.save, state='disabled')
        for button in (self.open_button, self.run_button, self.save_button):
            button.pack(side='left', padx=4)
        self.status = ttk.Label(buttons, text='Open a journal file')
        self.status.pack(side='left', padx=12)
        self.table = ttk.Treeview(window, columns=('date', 'author', 'text', 'category', 'severity'),
                                  show='headings', height=12)
        for column, title, width in (('date', 'Date', 90), ('author', 'Who', 90), ('text', 'What happened', 420),
                                     ('category', 'Category', 100), ('severity', 'Severity', 90)):
            self.table.heading(column, text=title)
            self.table.column(column, width=width)
        self.table.pack(fill='both', expand=True, padx=8)
        self.text = tk.Text(window, height=7, wrap='word')
        self.text.pack(fill='x', padx=8, pady=8)

    def open_file(self):
        name = filedialog.askopenfilename(initialdir=ROOT / 'data', filetypes=[('Excel', '*.xlsx')])
        if not name:
            return
        self.path = Path(name)
        self.entries = read_journal(self.path)
        self.show(self.entries)
        self.status.config(text=f'Entries: {len(self.entries)}')
        self.run_button.config(state='normal')

    def show(self, rows):
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert('', 'end', values=(row['date'], row['author'], row['text'],
                                                 row.get('category', ''), row.get('severity', '')))

    def start(self):
        for button in (self.open_button, self.run_button, self.save_button):
            button.config(state='disabled')
        self.status.config(text='The model is sorting the entries...')
        threading.Thread(target=self.work, daemon=True).start()
        self.window.after(100, self.poll)

    def work(self):
        try:
            results = process_journal(self.model, self.entries,
                                      lambda done, total: self.events.put(('progress', f'{done} of {total}')))
            self.events.put(('progress', 'bulletin...'))
            self.events.put(('done', results, write_summary(self.model, results)))
        except Exception as error:  # Show any error in the window, not only in the console.
            self.events.put(('error', str(error)))

    def poll(self):
        # The window is changed only here, in the main tkinter thread.
        while not self.events.empty():
            kind, *data = self.events.get()
            if kind == 'progress':
                self.status.config(text='Sorted: ' + data[0])
            elif kind == 'done':
                self.results, self.summary = data
                self.show(self.results)
                self.text.delete('1.0', 'end')
                self.text.insert('1.0', self.summary)
                self.status.config(text='Done')
                self.open_button.config(state='normal')
                self.save_button.config(state='normal')
                return
            else:
                messagebox.showerror('Error', data[0])
                self.open_button.config(state='normal')
                return
        self.window.after(100, self.poll)

    def save(self):
        save_results(self.path, self.results, self.summary)
        messagebox.showinfo('Saved', f'The "Review" sheet was written to {self.path.name}')


def main():
    with load_chat() as model:
        window = tk.Tk()
        window.geometry('900x560')
        JournalApp(window, model)
        window.mainloop()


if __name__ == '__main__':
    main()
