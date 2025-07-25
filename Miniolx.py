import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

# Connect to SQLite database
conn = sqlite3.connect("olx.db")
c = conn.cursor()

# Create users table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')

# Create listings table with category and image_path
c.execute('''
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        price REAL,
        contact TEXT,
        category TEXT,
        image_path TEXT,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

conn.commit()

# Main window setup
root = tk.Tk()
root.title("Mini OLX")
root.geometry("600x600")
current_user = None

# Utility: Clear all widgets from the window
def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

# Login page
def login_page():
    clear_window()
    tk.Label(root, text="Login / Register", font=("Arial", 20)).pack(pady=20)

    tk.Label(root, text="Username").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Password").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def register():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Registered Successfully!")
            except:
                messagebox.showerror("Error", "Username already exists!")
        else:
            messagebox.showwarning("Warning", "All fields are required.")

    def login():
        global current_user
        username = username_entry.get()
        password = password_entry.get()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            current_user = user
            messagebox.showinfo("Success", f"Welcome {username}!")
            dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    tk.Button(root, text="Login", command=login).pack(pady=10)
    tk.Button(root, text="Register", command=register).pack()

# Dashboard
def dashboard():
    clear_window()
    tk.Label(root, text="Welcome to Mini OLX", font=("Arial", 20)).pack(pady=20)

    tk.Button(root, text="Post New Item", width=20, command=post_item).pack(pady=10)
    tk.Button(root, text="View Listings", width=20, command=view_listings).pack(pady=10)
    tk.Button(root, text="Logout", width=20, command=login_page).pack(pady=10)

# Post Item with Image and Category
def post_item():
    clear_window()
    tk.Label(root, text="Post New Item", font=("Arial", 18)).pack(pady=10)

    tk.Label(root, text="Title").pack()
    title_entry = tk.Entry(root)
    title_entry.pack()

    tk.Label(root, text="Description").pack()
    desc_entry = tk.Entry(root)
    desc_entry.pack()

    tk.Label(root, text="Price").pack()
    price_entry = tk.Entry(root)
    price_entry.pack()

    tk.Label(root, text="Contact").pack()
    contact_entry = tk.Entry(root)
    contact_entry.pack()

    tk.Label(root, text="Category").pack()
    category_entry = tk.Entry(root)
    category_entry.pack()

    # File dialog to select image
    image_path = None
    def select_image():
        nonlocal image_path
        image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if image_path:
            img = Image.open(image_path)
            img.thumbnail((100, 100))
            img = ImageTk.PhotoImage(img)
            tk.Label(root, image=img).pack()
            root.image = img

    tk.Button(root, text="Select Image", command=select_image).pack(pady=10)

    def submit_item():
        title = title_entry.get()
        desc = desc_entry.get()
        price = price_entry.get()
        contact = contact_entry.get()
        category = category_entry.get()

        if all([title, desc, price, contact, category]) and image_path:
            try:
                c.execute("INSERT INTO listings (title, description, price, contact, category, image_path, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (title, desc, float(price), contact, category, image_path, current_user[0]))
                conn.commit()
                messagebox.showinfo("Success", "Item posted successfully!")
                dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to post item.\n{e}")
        else:
            messagebox.showwarning("Warning", "All fields are required and image must be selected.")

    tk.Button(root, text="Submit", command=submit_item).pack(pady=10)
    tk.Button(root, text="Back", command=dashboard).pack()

# View Listings with Category Filter
def view_listings():
    clear_window()
    tk.Label(root, text="All Listings", font=("Arial", 18)).pack(pady=10)

    # Category filter
    tk.Label(root, text="Filter by Category").pack()
    category_filter_entry = tk.Entry(root)
    category_filter_entry.pack()

    def filter_listings():
        category = category_filter_entry.get()
        c.execute("SELECT title, description, price, contact, category, image_path FROM listings WHERE category LIKE ?", ('%' + category + '%',))
        listings = c.fetchall()
        display_listings(listings)

    tk.Button(root, text="Filter", command=filter_listings).pack(pady=10)

    # Fetch all listings
    c.execute("SELECT title, description, price, contact, category, image_path FROM listings")
    listings = c.fetchall()

    if listings:
        display_listings(listings)
    else:
        tk.Label(root, text="No listings available.").pack()

    tk.Button(root, text="Back", command=dashboard).pack(pady=10)

def display_listings(listings):
    for item in listings:
        frame = tk.Frame(root, relief="solid", borderwidth=1, padx=10, pady=10)
        frame.pack(pady=5, padx=10, fill="x")
        tk.Label(frame, text=f"Title: {item[0]}", font=("Arial", 14, "bold")).pack(anchor="w")
        tk.Label(frame, text=f"Description: {item[1]}", wraplength=500).pack(anchor="w")
        tk.Label(frame, text=f"Price: ₹{item[2]}").pack(anchor="w")
        tk.Label(frame, text=f"Contact: {item[3]}").pack(anchor="w")
        tk.Label(frame, text=f"Category: {item[4]}").pack(anchor="w")
        if item[5]:
            img = Image.open(item[5])
            img.thumbnail((100, 100))
            img = ImageTk.PhotoImage(img)
            tk.Label(frame, image=img).pack()
            frame.image = img

# Start the app
login_page()
root.mainloop()
