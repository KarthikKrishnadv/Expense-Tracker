import os
import csv
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, Entry, StringVar, messagebox, Toplevel, Frame
from tkinter import ttk  # Import ttk to avoid NameError
from tkcalendar import DateEntry

# Constants
DATA_FILE = "expenses.csv"
CATEGORIES_FILE = "categories.txt"

# Function to initialize files
def initialize_files():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Amount", "Description"])

    if not os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "w") as file:
            file.write("Food\nRent\nEntertainment\nUtilities\n")

# Function to load categories
def load_categories():
    with open(CATEGORIES_FILE, "r") as file:
        return [line.strip() for line in file]

# Function to add a custom category
def add_category_via_dialog(category_dropdown):
    def save_new_category():
        new_category = new_category_var.get().strip()
        if not new_category:
            messagebox.showerror("Error", "Category name cannot be empty!")
            return

        categories = load_categories()
        if new_category in categories:
            messagebox.showerror("Error", "Category already exists!")
            return

        with open(CATEGORIES_FILE, "a") as file:
            file.write(new_category + "\n")

        category_dropdown['values'] = load_categories() + ["Add Custom Category"]
        messagebox.showinfo("Success", "Category added successfully!")
        add_category_window.destroy()

    add_category_window = Toplevel()
    add_category_window.title("Add Custom Category")
    add_category_window.geometry("300x150")

    Label(add_category_window, text="Enter new category:").pack(pady=10)
    new_category_var = StringVar()
    Entry(add_category_window, textvariable=new_category_var).pack(pady=5)
    Button(add_category_window, text="Add", command=save_new_category).pack(pady=10)

# Function to add an expense
def add_expense(date, category, amount, description):
    if not (date and category and amount and description):
        messagebox.showerror("Error", "All fields are required!")
        return

    if category == "Add Custom Category":
        messagebox.showerror("Error", "Please select a valid category!")
        return

    try:
        amount = float(amount)
        with open(DATA_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, category, amount, description])
        messagebox.showinfo("Success", "Expense added successfully!")
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")

# Function to view expenses
def view_expenses(tree):
    for row in tree.get_children():
        tree.delete(row)

    with open(DATA_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        for row in reader:
            tree.insert("", "end", values=row)

# Function to delete a selected expense
def delete_expense(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No item selected!")
        return

    row_values = tree.item(selected_item, "values")
    tree.delete(selected_item)

    # Rewrite the file excluding the deleted row
    with open(DATA_FILE, "r") as file:
        rows = list(csv.reader(file))
    
    with open(DATA_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(rows[0])  # Write header
        for row in rows[1:]:
            if row != list(row_values):
                writer.writerow(row)

    messagebox.showinfo("Success", "Expense deleted successfully!")

# Function to update a selected expense
def update_expense(tree, date, category, amount, description):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No item selected!")
        return

    if not (date and category and amount and description):
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        amount = float(amount)
        row_values = tree.item(selected_item, "values")

        # Update the file
        with open(DATA_FILE, "r") as file:
            rows = list(csv.reader(file))

        with open(DATA_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(rows[0])  # Write header
            for row in rows[1:]:
                if row == list(row_values):
                    writer.writerow([date, category, amount, description])
                else:
                    writer.writerow(row)

        # Update the treeview
        tree.item(selected_item, values=(date, category, amount, description))
        messagebox.showinfo("Success", "Expense updated successfully!")
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")

# Function to populate fields for updating
def populate_fields(tree, date_entry, category_var, amount_entry, description_entry):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No item selected!")
        return

    row_values = tree.item(selected_item, "values")
    date_entry.set_date(row_values[0])
    category_var.set(row_values[1])
    amount_entry.delete(0, "end")
    amount_entry.insert(0, row_values[2])
    description_entry.delete(0, "end")
    description_entry.insert(0, row_values[3])

# Function to generate a report
def generate_report():
    categories = {}

    with open(DATA_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        for row in reader:
            category = row[1]
            amount = float(row[2])
            categories[category] = categories.get(category, 0) + amount

    if categories:
        plt.figure(figsize=(6, 6))
        plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        plt.title("Expense Distribution by Category")
        plt.axis('equal')  # Equal aspect ratio ensures the pie is a circle.
        plt.show()
    else:
        messagebox.showinfo("Info", "No expenses to report.")

# GUI Application
def main():
    initialize_files()

    # Create the main window
    root = Tk()
    root.title("Expense Tracker")
    root.geometry("850x650")
    root.configure(bg="#f7f7f7")

    # Create a frame for input fields
    input_frame = Frame(root, bg="#ffffff", bd=2, relief="solid")
    input_frame.place(relx=0.5, rely=0.1, anchor="n")

    Label(input_frame, text="Date:", bg="#ffffff").grid(row=0, column=0, padx=10, pady=5)
    date_entry = DateEntry(input_frame, date_pattern="yyyy-mm-dd", width=12)
    date_entry.grid(row=0, column=1, padx=10, pady=5)

    Label(input_frame, text="Category:", bg="#ffffff").grid(row=1, column=0, padx=10, pady=5)
    category_var = StringVar()
    category_dropdown = ttk.Combobox(input_frame, textvariable=category_var, state="readonly", width=20)
    category_dropdown['values'] = load_categories() + ["Add Custom Category"]
    category_dropdown.grid(row=1, column=1, padx=10, pady=5)

    Label(input_frame, text="Amount:", bg="#ffffff").grid(row=2, column=0, padx=10, pady=5)
    amount_entry = Entry(input_frame)
    amount_entry.grid(row=2, column=1, padx=10, pady=5)

    Label(input_frame, text="Description:", bg="#ffffff").grid(row=3, column=0, padx=10, pady=5)
    description_entry = Entry(input_frame)
    description_entry.grid(row=3, column=1, padx=10, pady=5)

    # Buttons for actions
    Button(input_frame, text="Add Expense", bg="#4CAF50", fg="white", command=lambda: add_expense(
        date_entry.get(), category_var.get(), amount_entry.get(), description_entry.get()
    )).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

    # Create a frame for the table and buttons
    table_frame = Frame(root, bg="#ffffff", bd=2, relief="solid")
    table_frame.place(relx=0.5, rely=0.35, anchor="n", relwidth=0.9, relheight=0.55)

    # Expense table
    tree = ttk.Treeview(table_frame, columns=("Date", "Category", "Amount", "Description"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("Category", text="Category")
    tree.heading("Amount", text="Amount")
    tree.heading("Description", text="Description")
    tree.pack(pady=10, padx=10, fill="both", expand=True)

    Button(table_frame, text="View Expenses", bg="#2196F3", fg="white", command=lambda: view_expenses(tree)).pack(side="left", padx=5, pady=10)
    Button(table_frame, text="Delete Expense", bg="#f44336", fg="white", command=lambda: delete_expense(tree)).pack(side="left", padx=5, pady=10)
    Button(table_frame, text="Populate Fields", bg="#FF9800", fg="white", command=lambda: populate_fields(tree, date_entry, category_var, amount_entry, description_entry)).pack(side="left", padx=5, pady=10)
    Button(table_frame, text="Update Expense", bg="#4CAF50", fg="white", command=lambda: update_expense(
        tree, date_entry.get(), category_var.get(), amount_entry.get(), description_entry.get()
    )).pack(side="left", padx=5, pady=10)

    Button(root, text="Generate Report", bg="#673AB7", fg="white", command=generate_report).place(relx=0.5, rely=0.92, anchor="center")

    # Add custom category action when "Add Custom Category" is selected
    category_dropdown.bind("<<ComboboxSelected>>", lambda e: add_category_via_dialog(category_dropdown) if category_var.get() == "Add Custom Category" else None)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
