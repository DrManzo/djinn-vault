---
subject: business/career-strategies/python-project-development
tags:
  - business/career-growth/skills-development
  - business/investment-strategy/dividend-investing
created: 2026-05-23
source: Perplexity export
---

# Personal Expense Tracker Python Project

## Summary
This note outlines the steps to build a personal expense tracker using Python, covering fundamental concepts like variables, data types, functions, lists, dictionaries, file I/O, loops, conditionals, and basic error handling.

## Key Points
- **Project Overview**: Create a command-line expense tracker.
- **Phase 1**: Add single expenses (Days 1-2).
- **Phase 2**: Store multiple expenses and view all in table format (Days 3-4).
- **Phase 3**: Save and load data from file using CSV.

## Details
### Phase 1: Basic Structure & Adding Single Expenses

**Core Concepts**
- Variables, input/output, data types, basic data structures.

**Code Example**
```python
def get_expense():
    print("--- Add New Expense ---")
    date = input("Enter date (YYYY-MM-DD): ")
    category = input("Enter category (Food/Transport/Entertainment/Other): ")
    description = input("Enter description: ")
    amount = float(input("Enter amount: $"))
    
    expense = {
        'date': date,
        'category': category,
        'description': description,
        'amount': amount
    }
    
    return expense

# Test it
expense = get_expense()
print("\nExpense recorded:")
print(f"Date: {expense['date']}")
print(f"Category: {expense['category']}")
print(f"Description: {expense['description']}")
print(f"Amount: ${expense['amount']:.2f}")
```

**Common Mistakes**
- Forgetting to convert `amount` to `float()`.
- Typos in dictionary keys.
- Not using `.2f` for currency formatting.

### Phase 2: Store Multiple Expenses & View All

**Core Concepts**
- Lists, loops, functions, string formatting.

**Code Example**
```python
expenses = [] # Create empty list to store all expenses

def add_expense():
    expense = get_expense()
    expenses.append(expense)
    print(f"\n✓ Added: {expense['description']} - ${expense['amount']:.2f}")

def view_expenses():
    if not expenses:
        print("\nNo expenses recorded yet.")
        return
    
    print("\n--- All Expenses ---")
    print(f"{'Date':<12} {'Category':<15} {'Description':<20} {'Amount':>10}")
    print("-" * 60)
    
    for expense in expenses:
        print(f"{expense['date']:<12} {expense['category']:<15} "
              f"{expense['description']:<20} ${expense['amount']:>9.2f}")

# Simple menu
while True:
    print("\n1. Add Expense")
    print("2. View All Expenses")
    print("3. Exit")
    
    choice = input("\nChoice: ")
    
    if choice == "1":
        add_expense()
    elif choice == "2":
        view_expenses()
    elif choice == "3":
        break
    else:
        print("Invalid choice. Try again.")
```

**Common Mistakes**
- Forgetting to initialize `expenses = []` at the top.
- Not checking if list is empty before looping (causes no output).
- String formatting alignment issues.

### Phase 3: Save & Load from File

**Core Concepts**
- File I/O, CSV format, error handling, persistence.

## References
- [dailypythonprojects.substack.com](https://dailypythonprojects.substack.com/p/build-an-expense-tracker-with-python)
- [bitemyapp.com/blog/review-learn-python-hard-way/]

## Related
- [[Python-Basics-Guide]] — For more Python basics.
- [[Data-Structures-and-Algorithms]] — To deepen understanding of data structures.