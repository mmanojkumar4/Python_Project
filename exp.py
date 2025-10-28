

import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

# file operation

def load_expenses():
    """Load all expenses from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

def save_expenses(expenses):
    """Save all expenses to the JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(expenses, file, indent=4)


# crud

def add_expense_endpoint(name, category, amount):
    """Add a new expense."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    expense = {
        "name": name,
        "category": category,
        "amount": float(amount),
        "date": date
    }

    expenses = load_expenses()
    expenses.append(expense)
    save_expenses(expenses)
    return {"status": "success", "message": f"Added expense '{name}' successfully!"}


def get_expenses_endpoint():
    """Return all expenses."""
    return load_expenses()


def update_expense_endpoint(index, new_name=None, new_category=None, new_amount=None):
    """Update an existing expense by index (1-based)."""
    expenses = load_expenses()

    if 1 <= index <= len(expenses):
        exp = expenses[index - 1]
        if new_name:
            exp["name"] = new_name
        if new_category:
            exp["category"] = new_category
        if new_amount:
            exp["amount"] = float(new_amount)
        save_expenses(expenses)
        return {"status": "success", "updated": exp}
    else:
        return {"status": "error", "message": "Invalid expense number."}


def delete_expense_endpoint(index):
    """Delete an expense by index."""
    expenses = load_expenses()
    if 1 <= index <= len(expenses):
        deleted = expenses.pop(index - 1)
        save_expenses(expenses)
        return {"status": "success", "deleted": deleted}
    else:
        return {"status": "error", "message": "Invalid expense number."}


# summaryy

def summary_endpoint():
    """Return total, today's spending, and category-wise summary."""
    expenses = load_expenses()
    if not expenses:
        return {"status": "empty", "message": "No expenses to summarize."}

    total = sum(exp["amount"] for exp in expenses)
    category_summary = {}
    for exp in expenses:
        category_summary[exp["category"]] = category_summary.get(exp["category"], 0) + exp["amount"]

    today = datetime.now().strftime("%Y-%m-%d")
    today_total = sum(exp["amount"] for exp in expenses if exp["date"].startswith(today))

    return {
        "status": "success",
        "total_spent": total,
        "today_spent": today_total,
        "category_summary": category_summary,
        "total_items": len(expenses)
    }


# sort and filter

def sort_expenses_endpoint(by="date", reverse=False):
    """Sort expenses by amount or date."""
    expenses = load_expenses()
    if not expenses:
        return {"status": "empty", "message": "No expenses to sort."}

    if by not in ["date", "amount"]:
        return {"status": "error", "message": "Invalid sort key. Use 'date' or 'amount'."}

    sorted_expenses = sorted(expenses, key=lambda x: x[by], reverse=reverse)
    return {"status": "success", "sorted_by": by, "reverse": reverse, "data": sorted_expenses}


def filter_expenses_endpoint(category=None, start_date=None, end_date=None):
    """Filter expenses by category or date range."""
    expenses = load_expenses()
    if not expenses:
        return {"status": "empty", "message": "No expenses to filter."}

    filtered = expenses
    if category:
        filtered = [exp for exp in filtered if exp["category"].lower() == category.lower()]

    if start_date or end_date:
        start_date = start_date or "0000-00-00"
        end_date = end_date or "9999-12-31"
        filtered = [
            exp for exp in filtered
            if start_date <= exp["date"][:10] <= end_date
        ]

    return {"status": "success", "filtered_count": len(filtered), "data": filtered}


# =File export csv file

def export_to_csv(filename="expenses_report.csv"):
    """Export all expenses to a CSV file."""
    import csv
    expenses = load_expenses()
    if not expenses:
        return {"status": "empty", "message": "No data to export."}

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "category", "amount", "date"])
        writer.writeheader()
        writer.writerows(expenses)
    return {"status": "success", "message": f"Data exported to {filename}"}


# Menu

def cli_menu():
    while True:
        print("===  Expense Tracker ===")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Delete Expense")
        print("4. View Summary")
        print("5. Update Expense")
        print("6. Sort Expenses")
        print("7. Filter Expenses")
        print("8. Export to CSV")
        print("9. Exit")

        choice = input("Choose an option (1-9): ")
        print()

        if choice == "1":
            name = input("Enter expense name: ")
            category = input("Enter category: ")
            amount = input("Enter amount: ₹")
            res = add_expense_endpoint(name, category, amount)
            print(res["message"], "\n")

        elif choice == "2":
            expenses = get_expenses_endpoint()
            if not expenses:
                print("No expenses recorded yet.\n")
            else:
                print("\n All Expenses:")
                for i, exp in enumerate(expenses, 1):
                    print(f"{i}. {exp['name']} | ₹{exp['amount']} | {exp['category']} | {exp['date']}")
                print()

        elif choice == "3":
            expenses = get_expenses_endpoint()
            if not expenses:
                print("No expenses to delete.\n")
                continue
            for i, exp in enumerate(expenses, 1):
                print(f"{i}. {exp['name']} | ₹{exp['amount']} | {exp['category']}")
            try:
                num = int(input("Enter expense number to delete: "))
                res = delete_expense_endpoint(num)
                if res["status"] == "success":
                    print(f"Deleted: {res['deleted']['name']}\n")
                else:
                    print(res["message"], "\n")
            except ValueError:
                print(" Invalid input.\n")

        elif choice == "4":
            res = summary_endpoint()
            if res["status"] == "empty":
                print(res["message"], "\n")
            else:
                print(f"\n Total Spending: ₹{res['total_spent']:.2f}")
                print(f" Today's Spending: ₹{res['today_spent']:.2f}")
                print("\n Category Summary:")
                for cat, amt in res["category_summary"].items():
                    print(f" - {cat}: ₹{amt:.2f}")
                print()

        elif choice == "5":
            expenses = get_expenses_endpoint()
            if not expenses:
                print("No expenses to update.\n")
                continue
            for i, exp in enumerate(expenses, 1):
                print(f"{i}. {exp['name']} | ₹{exp['amount']} | {exp['category']}")
            try:
                num = int(input("Enter expense number to update: "))
                new_name = input("Enter new name (press Enter to keep same): ")
                new_cat = input("Enter new category (press Enter to keep same): ")
                new_amt = input("Enter new amount (press Enter to keep same): ")
                new_amt = float(new_amt) if new_amt else None
                res = update_expense_endpoint(num, new_name or None, new_cat or None, new_amt)
                if res["status"] == "success":
                    print(f"Updated: {res['updated']}\n")
                else:
                    print(res["message"], "\n")
            except ValueError:
                print(" Invalid input.\n")

        elif choice == "6":
            key = input("Sort by (date/amount): ").strip().lower()
            order = input("Order (asc/desc): ").strip().lower()
            reverse = True if order == "desc" else False
            res = sort_expenses_endpoint(by=key, reverse=reverse)
            if res["status"] == "success":
                print(f"\n Sorted by {key} ({'Descending' if reverse else 'Ascending'}):")
                for i, exp in enumerate(res["data"], 1):
                    print(f"{i}. {exp['name']} | ₹{exp['amount']} | {exp['category']} | {exp['date']}")
                print()
            else:
                print(res["message"], "\n")

        elif choice == "7":
            cat = input("Enter category (or press Enter to skip): ")
            sdate = input("Start date (YYYY-MM-DD or skip): ")
            edate = input("End date (YYYY-MM-DD or skip): ")
            res = filter_expenses_endpoint(category=cat or None, start_date=sdate or None, end_date=edate or None)
            if res["status"] == "success":
                print(f"\nFiltered Results ({res['filtered_count']} found):")
                for i, exp in enumerate(res["data"], 1):
                    print(f"{i}. {exp['name']} | ₹{exp['amount']} | {exp['category']} | {exp['date']}")
                print()
            else:
                print(res["message"], "\n")

        elif choice == "8":
            res = export_to_csv()
            print(res["message"], "\n")

        elif choice == "9":
            print(" Exiting... Goodbye!")
            break

        else:
            print("Invalid option, try again.\n")

#RUN 

if __name__ == "__main__":
    cli_menu()

