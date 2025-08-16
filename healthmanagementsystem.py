import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class HealthDatabase:
    def __init__(self, db_name="health_records.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        code TEXT NOT NULL,
                        details TEXT,
                        status TEXT DEFAULT 'Active',
                        timestamp TEXT
                    )''')
        self.conn.commit()

    def add_record(self, name, code, details):
        c = self.conn.cursor()
        c.execute("INSERT INTO records (name, code, details, status, timestamp) VALUES (?, ?, ?, 'Active', ?)",
                  (name, code, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()

    def mark_as_cured(self, record_id):
        """Update status of a single record to Cured"""
        c = self.conn.cursor()
        c.execute("UPDATE records SET status = 'Cured' WHERE id = ?", (record_id,))
        self.conn.commit()

    def search_patient_history(self, name):
        """Return full history of a patient (Active + Cured)"""
        c = self.conn.cursor()
        c.execute("SELECT id, name, code, details, status, timestamp FROM records WHERE name LIKE ? ORDER BY id DESC",
                  ('%' + name + '%',))
        return c.fetchall()

    def close(self):
        self.conn.close()

class HealthRecordApp:
    def __init__(self, root):
        self.db = HealthDatabase()
        self.root = root
        self.root.title("Health Record Management System")

        self.build_ui()

    def build_ui(self):
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack()

        tk.Label(input_frame, text="Patient Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Patient Code:").grid(row=1, column=0, padx=5, pady=5)
        self.code_entry = tk.Entry(input_frame)
        self.code_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Details:").grid(row=2, column=0, padx=5, pady=5)
        self.details_entry = tk.Entry(input_frame)
        self.details_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(input_frame, text="Add Record", command=self.add_record).grid(row=3, columnspan=2, pady=10)

        search_frame = tk.Frame(self.root, pady=10)
        search_frame.pack()

        tk.Label(search_frame, text="Search Patient by Name:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(search_frame, text="Search", command=self.search_patient).grid(row=0, column=2, padx=5, pady=5)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Code", "Details", "Status", "Timestamp"),
                                 show="headings")
        for col in ("ID", "Name", "Code", "Details", "Status", "Timestamp"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(self.root, text="Mark Selected as Cured", command=self.mark_selected_as_cured).pack(pady=5)

    def add_record(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        details = self.details_entry.get().strip()

        if name and code:
            self.db.add_record(name, code, details)
            messagebox.showinfo("Success", "Record added successfully as Active.")
            self.clear_inputs()
        else:
            messagebox.showwarning("Input Error", "Name and Code are required.")

    def search_patient(self):
        name = self.search_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Enter a patient name to search.")
            return

        records = self.db.search_patient_history(name)
        self.refresh_records(records)

    def refresh_records(self, records):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for record in records:
            self.tree.insert("", "end", values=record)

    def mark_selected_as_cured(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Select a record to mark as cured.")
            return

        record = self.tree.item(selected_item)["values"]
        record_id, status = record[0], record[4]

        if status == "Cured":
            messagebox.showinfo("Info", "This record is already marked as Cured.")
            return

        self.db.mark_as_cured(record_id)
        messagebox.showinfo("Success", "Record updated to Cured.")

        self.search_patient()

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.code_entry.delete(0, tk.END)
        self.details_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthRecordApp(root)
    root.mainloop()
