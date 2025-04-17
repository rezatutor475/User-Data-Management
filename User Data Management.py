import tkinter as tk
from tkinter import messagebox
import hashlib
import mysql.connector
import subprocess
import csv
from fpdf import FPDF
import os
import sys
from datetime import datetime

# ------------------------ Cross-Platform File Opener ------------------------ #
def open_file(filepath):
    try:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))
    except Exception as e:
        messagebox.showerror("Open File Error", f"Could not open file: {e}")

# ------------------------ Database Connection ------------------------ #
def connect_db():
    try:
        return mysql.connector.connect(
            host="your_host",
            user="your_user",
            password="your_password",
            database="your_database"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Connection failed: {err}")
        return None

def execute_query(query, params=(), fetch=False):
    connection = connect_db()
    if not connection:
        return None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        connection.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Query Error", f"Error: {err}")
    finally:
        connection.close()

# ------------------------ CRUD Operations ------------------------ #
def login_window():
    login_win = tk.Toplevel(root)
    login_win.title("Admin Login")
    login_win.geometry("300x180")

    tk.Label(login_win, text="Username").pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack()

    tk.Label(login_win, text="Password").pack(pady=5)
    password_entry = tk.Entry(login_win, show='*')
    password_entry.pack()

    def attempt_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        result = execute_query(
            "SELECT role FROM admins WHERE username=%s AND password=%s",
            (username, password),
            fetch=True
        )
        if result:
            role = result[0][0]
            messagebox.showinfo("Login Success", f"Logged in as {role.capitalize()}")
            if role == 'admin':
                launch_admin_panel()
            else:
                messagebox.showinfo("User Access", "Limited access granted.")
            login_win.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(login_win, text="Login", command=attempt_login).pack(pady=10)

def launch_admin_panel():
    admin_win = tk.Toplevel(root)
    admin_win.title("Admin Panel")
    admin_win.geometry("300x300")

    tk.Label(admin_win, text="Welcome, Admin!", font=('Arial', 14, 'bold')).pack(pady=10)

    tk.Button(admin_win, text="View All Users", command=fetch_data).pack(fill='x', padx=10, pady=5)
    tk.Button(admin_win, text="Export Logs", command=lambda: open_file("pdf_export_log.txt")).pack(fill='x', padx=10, pady=5)
    tk.Button(admin_win, text="Add Another Admin", command=add_new_admin_window).pack(fill='x', padx=10, pady=5)

def add_new_admin_window():
    add_win = tk.Toplevel(root)
    add_win.title("Add Admin")
    add_win.geometry("300x200")

    tk.Label(add_win, text="New Username").pack(pady=5)
    new_user = tk.Entry(add_win)
    new_user.pack()

    tk.Label(add_win, text="New Password").pack(pady=5)
    new_pass = tk.Entry(add_win, show='*')
    new_pass.pack()

    def add_admin():
        user = new_user.get().strip()
        pwd = new_pass.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Username and password required")
            return
        execute_query(
            "INSERT INTO admins (username, password, role) VALUES (%s, %s, 'admin')",
            (user, pwd)
        )
        messagebox.showinfo("Success", f"Admin '{user}' added successfully.")
        add_win.destroy()

    tk.Button(add_win, text="Add Admin", command=add_admin).pack(pady=10)
    tk.Button(root, text="Admin Login", command=login_window).pack(fill='x', padx=10, pady=5)

def launch_user_panel():
    user_win = tk.Toplevel(root)
    user_win.title("User Panel")
    user_win.geometry("300x250")

    tk.Label(user_win, text="Welcome, User!", font=('Arial', 14, 'bold')).pack(pady=10)

    tk.Button(user_win, text="Submit My Info", command=submit_data).pack(fill='x', padx=10, pady=5)
    tk.Button(user_win, text="View My Data", command=view_own_data).pack(fill='x', padx=10, pady=5)
    tk.Button(user_win, text="Logout", command=user_win.destroy).pack(fill='x', padx=10, pady=5)

def view_own_data():
    # Fetch data for the currently logged-in user only
    username = current_user.get("username")
    result = execute_query("SELECT * FROM users WHERE name = %s", (username,), fetch=True)
    
    if result:
        data_str = "\n".join([f"{col}: {val}" for col, val in zip(required_fields, result[0])])
        messagebox.showinfo("Your Data", data_str)
    else:
        messagebox.showinfo("No Data", "No data found for your account.")

def log_activity(action, actor="system"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {actor.upper()} - {action}\n"
    with open("activity_log.txt", "a") as log_file:
        log_file.write(log_entry)
        log_activity("Submitted data", actor="user123")
        log_activity("Exported PDF", actor="admin")

def view_logs():
    log_win = tk.Toplevel(root)
    log_win.title("Activity Log")
    log_win.geometry("500x400")

    tk.Label(log_win, text="Activity Logs", font=("Arial", 12, "bold")).pack(pady=10)

    log_text = tk.Text(log_win, wrap='word')
    log_text.pack(expand=True, fill='both', padx=10, pady=5)

    try:
        with open("activity_log.txt", "r") as log_file:
            content = log_file.read()
            log_text.insert('1.0', content)
    except FileNotFoundError:
        log_text.insert('1.0', "No log file found.")
        tk.Button(admin_win, text="View Activity Logs", command=view_logs).pack(fill='x', padx=10, pady=5)

current_user = {}

# Inside login logic
current_user["username"] = username
current_user["role"] = role

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def validate_required_fields():
    missing_fields = []
    for field in required_fields:
        value = entries[field].get().strip()
        if not value:
            missing_fields.append(field)
            entries[field].config(bg='misty rose')
        else:
            entries[field].config(bg='white')
    if missing_fields:
        messagebox.showerror(
            "Validation Error",
            "Please fill in the following required fields:\n- " + "\n- ".join(missing_fields)
        )
        return False
    return True

def submit_data():
    if not validate_required_fields():
        return
    data = [entries[field].get().strip() for field in required_fields]
    query = """
        INSERT INTO users (name, age, birth_place, height, weight, measurements, body_type, buttock_type, breast_size)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    execute_query(query, tuple(data))
    messagebox.showinfo("Success", "User data submitted successfully.")

def fetch_data():
    records = execute_query("SELECT * FROM users", fetch=True)
    if records:
        display_records(records)

def update_data():
    user_id = entries["User ID"].get().strip()
    name = entries["Name"].get().strip()
    age = entries["Age"].get().strip()
    if not all([user_id, name, age]):
        messagebox.showerror("Input Error", "User ID, Name, and Age are required.")
        return
    query = "UPDATE users SET name = %s, age = %s WHERE id = %s"
    execute_query(query, (name, age, user_id))
    messagebox.showinfo("Success", "User record updated.")

def delete_data():
    user_id = entries["User ID"].get().strip()
    if not user_id:
        messagebox.showerror("Input Error", "User ID is required.")
        return
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user ID {user_id}?")
    if not confirm:
        return
    result = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch=True)
    if not result:
        messagebox.showinfo("Not Found", f"No user found with ID {user_id}.")
        return
    execute_query("DELETE FROM users WHERE id = %s", (user_id,))
    messagebox.showinfo("Success", "User record deleted.")

def search_user():
    term = entries["Search by Name"].get().strip()
    if not term:
        messagebox.showerror("Input Error", "Search term required.")
        return
    query = "SELECT * FROM users WHERE name LIKE %s"
    records = execute_query(query, (f"%{term}%",), fetch=True)
    if records:
        display_records(records)

# ------------------------ Export Functions ------------------------ #
def export_to_csv():
    records = execute_query("SELECT * FROM users", fetch=True)
    if records:
        with open("users_data.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Age", "Birth Place", "Height", "Weight", "Measurements", "Body Type", "Buttock Type", "Breast Size"])
            writer.writerows(records)
        messagebox.showinfo("Success", "Data exported to users_data.csv")

def export_to_pdf():
    records = execute_query("SELECT * FROM users", fetch=True)
    if records:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"users_data_{timestamp}.pdf"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="User Data Report", ln=True, align="C")
        pdf.ln(10)
        headers = ["ID", "Name", "Age", "Birth Place", "Height", "Weight", "Measurements", "Body Type", "Buttock Type", "Breast Size"]
        col_widths = [10, 30, 10, 30, 15, 15, 25, 25, 25, 25]
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 10, h, border=1)
        pdf.ln()
        for row in records:
            for i, item in enumerate(row):
                pdf.cell(col_widths[i], 10, str(item), border=1)
            pdf.ln()
        pdf.output(pdf_filename)
        open_file(pdf_filename)
        messagebox.showinfo("Success", f"Data exported to {pdf_filename}")

        with open("pdf_export_log.txt", "a") as log:
            log.write(f"Exported {pdf_filename} at {datetime.now()}\n")

def export_latest_pdf_only_selected_fields(fields):
    records = execute_query("SELECT * FROM users", fetch=True)
    if not records:
        messagebox.showinfo("No Data", "No records to export.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"selected_fields_{timestamp}.pdf"

    headers = [h for h in ["ID", "Name", "Age", "Birth Place", "Height", "Weight", "Measurements", "Body Type", "Buttock Type", "Breast Size"] if h in fields]
    col_widths = [30 for _ in headers]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Selected User Data", ln=True, align="C")
    pdf.ln(10)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 10, h, border=1)
    pdf.ln()
    for row in records:
        user_data = dict(zip(["ID", "Name", "Age", "Birth Place", "Height", "Weight", "Measurements", "Body Type", "Buttock Type", "Breast Size"], row))
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 10, str(user_data[h]), border=1)
        pdf.ln()
    pdf.output(pdf_filename)
    open_file(pdf_filename)
    messagebox.showinfo("Success", f"Selected fields exported to {pdf_filename}")

# ------------------------ Build Executable ------------------------ #
def create_executable():
    try:
        subprocess.run(["pyinstaller", "--onefile", "--windowed", "your_script.py"], check=True)
        messagebox.showinfo("Success", "Executable created successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Executable creation failed: {e}")

# ------------------------ UI Display Helper ------------------------ #
def display_records(records):
    win = tk.Toplevel(root)
    win.title("User Records")
    for record in records:
        tk.Label(win, text=str(record), anchor="w", justify="left").pack(fill='x', padx=5, pady=2)

# ------------------------ GUI Setup ------------------------ #
root = tk.Tk()
root.title("User Data Management")
root.geometry("420x700")

entries = {}
required_fields = [
    "Name", "Age", "Birth Place", "Height", "Weight",
    "Measurements", "Body Type", "Buttock Type", "Breast Size"
]
all_fields = required_fields + ["User ID", "Search by Name"]

def create_entry(label):
    frame = tk.Frame(root)
    frame.pack(fill='x', padx=5, pady=2)
    tk.Label(frame, text=label + ":", width=18, anchor='w').pack(side='left')
    entry = tk.Entry(frame)
    entry.pack(side='left', expand=True, fill='x')
    return entry

for field in all_fields:
    entries[field] = create_entry(field)

buttons = [
    ("Submit", submit_data),
    ("Fetch Data", fetch_data),
    ("Update Record", update_data),
    ("Delete Record", delete_data),
    ("Search User", search_user),
    ("Export to CSV", export_to_csv),
    ("Export to PDF", export_to_pdf),
    ("Create Executable", create_executable)
]

for text, cmd in buttons:
    tk.Button(root, text=text, command=cmd).pack(fill='x', padx=10, pady=3)

root.mainloop()
