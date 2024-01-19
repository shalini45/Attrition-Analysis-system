import sqlite3
import datetime
import re  # Regular expressions

# Custom exception class for invalid employee IDs
class InvalidEmployeeIDError(Exception):
    pass

# Class for employee data (inheritance)
class Employee:
    def __init__(self, name, department, designation, joining_date):
        self.name = name
        self.department = department
        self.designation = designation
        self.joining_date = joining_date
#Database Connection:
conn = sqlite3.connect('attrition.db')
c = conn.cursor()
#Table Creation
c.execute(""" CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    designation TEXT,
    joining_date DATE,
    termination_date DATE,
    reason_for_leaving TEXT
);
""")
#Functions
def add_employee():
    name = input("Enter employee name: ")
    department = input("Enter employee department: ")
    designation = input("Enter employee designation: ")
    joining_date = input("Enter employee joining date (YYYY-MM-DD): ")
    # Validate date format
    joining_date_match = re.match(r"\d{4}-\d{2}-\d{2}", joining_date)
    if not joining_date_match:
        raise ValueError("Invalid date format. Please enter YYYY-MM-DD.")
    c.execute("INSERT INTO employees (name, department, designation, joining_date) VALUES (?, ?, ?, ?)", (name, department, designation, joining_date ))
    conn.commit()
    print("Employee added successfully!")

def record_termination():
    while True:
        try:
            employee_id = int(input("Enter employee ID to record termination: "))
            c.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            if c.fetchone() is None:
                raise InvalidEmployeeIDError
            break
        except InvalidEmployeeIDError:
            print("Invalid employee ID. Please try again.")
        except ValueError:
            print("Invalid input. Please enter an integer for employee ID.")
    termination_date = input("Enter termination date (YYYY-MM-DD): ")
    reason = input("Enter reason for leaving: ")
    c.execute("UPDATE employees SET termination_date = ?, reason_for_leaving = ? WHERE id = ?", (termination_date, reason, employee_id))
    conn.commit()
    print("Termination recorded successfully!")

def count_terminations(period="quarterly"):
    if period == "quarterly":
        start_date = datetime.date.today() - datetime.timedelta(days=90)
    elif period == "yearly":
        start_date = datetime.date.today() - datetime.timedelta(days=365)
    else:
        raise ValueError("Invalid period specified")
    c.execute("SELECT COUNT(*) FROM employees WHERE termination_date >= ?", (start_date,))
    return c.fetchone()[0]

def get_attrition_by_department():
    # List comprehension for department-termination pairs
    attrition_data = [(row[0], row[1]) for row in c.execute("SELECT department, COUNT(*) AS terminations FROM employees WHERE termination_date IS NOT NULL GROUP BY department")]
    return attrition_data

def get_attrition_by_designation():
    # Set to ensure unique designations
    attrition_data = {row[0]: row[1] for row in c.execute("SELECT designation, COUNT(*) AS terminations FROM employees WHERE termination_date IS NOT NULL GROUP BY designation")}
    return attrition_data

def get_top_reasons_for_leaving():
    # Generator expression for efficient iteration
    top_reasons = (
        row
        for row in c.execute(
            "SELECT reason_for_leaving, COUNT(*) AS count FROM employees WHERE reason_for_leaving IS NOT NULL GROUP BY reason_for_leaving ORDER BY count DESC LIMIT 5"
        )
    )

    # Lambda function to sort top reasons alphabetically while preserving count order
    top_reasons = sorted(top_reasons, key=lambda row: row[0])  # Sort by reason alphabetically
    return top_reasons

while True:
    print("\nChoose an action:")
    print("1. Add employee")
    print("2. Record termination")
    print("3. Get quarterly terminations")
    print("4. Get yearly terminations")
    print("5. Get attrition by department")
    print("6. Get attrition by designation")
    print("7. Get top reasons for leaving")
    print("8. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_employee()
    elif choice == "2":
        record_termination()
    elif choice == "3":
        period = input("Enter analysis period (quarterly ): ")
        quarterly_terminations = count_terminations(period)
        print("Quarterly terminations:", quarterly_terminations)
    elif choice == "4":
        period = input("Enter analysis period (yearly ): ")
        yearly_terminations = count_terminations(period)
        print("Yearly terminations:", yearly_terminations)
        
    elif choice == "5":
        attrition_by_department = get_attrition_by_department()
        print("Attrition by department:", attrition_by_department)
    elif choice == "6":
        attrition_by_designation = get_attrition_by_designation()
        print("Attrition by designation:", attrition_by_designation)
    elif choice == "7":
        top_reasons = get_top_reasons_for_leaving()
        print("Top reasons for leaving:")
        for reason, count in top_reasons:
            print(f"- {reason}: {count}")
    elif choice == "8":
        break
    else:
        print("Invalid choice. Please try again.")

conn.close()




