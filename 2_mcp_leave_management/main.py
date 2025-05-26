from mcp.server.fastmcp import FastMCP
from typing import List
import matplotlib.pyplot as plt
import io
import base64

# ----- Mock Databases -----
# In-memory mock database for leave management
employee_leaves = {
    "E001": {"balance": 18, "history": ["2024-12-25", "2025-01-01"]},
    "E002": {"balance": 20, "history": []}
}

# In-memory mock database for work tracking
employee_tasks = {
    "E001": {"tasks": ["Prepare report", "Attend meeting"], "completed": ["Prepare report"]},
    "E002": {"tasks": ["Update website", "Backup database"], "completed": []}
}

# Create MCP server
mcp = FastMCP("EmployeeManager")  # Updated name

# ----- Leave Management Tools -----

@mcp.tool()
def get_leave_balance(employee_id: str) -> str:
    """Check how many leave days are left for the employee"""
    data = employee_leaves.get(employee_id)
    if data:
        return f"{employee_id} has {data['balance']} leave days remaining."
    return "Employee ID not found."

@mcp.tool()
def apply_leave(employee_id: str, leave_dates: List[str]) -> str:
    """Apply leave for specific dates"""
    if employee_id not in employee_leaves:
        return "Employee ID not found."

    requested_days = len(leave_dates)
    available_balance = employee_leaves[employee_id]["balance"]

    if available_balance < requested_days:
        return f"Insufficient leave balance. You requested {requested_days} day(s) but have only {available_balance}."

    employee_leaves[employee_id]["balance"] -= requested_days
    employee_leaves[employee_id]["history"].extend(leave_dates)

    return f"Leave applied for {requested_days} day(s). Remaining balance: {employee_leaves[employee_id]['balance']}."

@mcp.tool()
def get_leave_history(employee_id: str) -> str:
    """Get leave history for the employee"""
    data = employee_leaves.get(employee_id)
    if data:
        history = ', '.join(data['history']) if data['history'] else "No leaves taken."
        return f"Leave history for {employee_id}: {history}"
    return "Employee ID not found."

@mcp.tool()
def visualize_leave_summary() -> str:
    """Visual summary of all employees' leave balances"""
    summary_lines = []
    summary_lines.append("🗂️ Leave Balances Summary:\n")
    for emp_id, data in employee_leaves.items():
        bar = "🟩" * data["balance"] + "⬜" * (20 - data["balance"])
        summary_lines.append(f"{emp_id}: {bar} ({data['balance']} days left)")
    return "\n".join(summary_lines)

@mcp.tool()
def plot_leave_balances() -> str:
    """Generate a bar chart of leave balances and return as a base64 image string"""
    employees = list(employee_leaves.keys())
    balances = [data['balance'] for data in employee_leaves.values()]

    plt.figure(figsize=(8, 5))
    plt.bar(employees, balances, color='skyblue')
    plt.ylim(0, 20)
    plt.title('Employee Leave Balances')
    plt.xlabel('Employee ID')
    plt.ylabel('Leave Days Remaining')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    return f"data:image/png;base64,{image_base64}"

# ----- Work Tracking Tools -----

@mcp.tool()
def assign_task(employee_id: str, task: str) -> str:
    """Assign a new task to an employee"""
    if employee_id not in employee_tasks:
        return "Employee ID not found."

    employee_tasks[employee_id]["tasks"].append(task)
    return f"Task '{task}' assigned to {employee_id}."

@mcp.tool()
def complete_task(employee_id: str, task: str) -> str:
    """Mark a specific task as completed"""
    if employee_id not in employee_tasks:
        return "Employee ID not found."

    if task not in employee_tasks[employee_id]["tasks"]:
        return f"Task '{task}' not found for {employee_id}."

    if task in employee_tasks[employee_id]["completed"]:
        return f"Task '{task}' is already marked as completed."

    employee_tasks[employee_id]["completed"].append(task)
    return f"Task '{task}' marked as completed for {employee_id}."

@mcp.tool()
def view_tasks(employee_id: str) -> str:
    """View pending and completed tasks for an employee"""
    if employee_id not in employee_tasks:
        return "Employee ID not found."

    pending = [task for task in employee_tasks[employee_id]["tasks"] if task not in employee_tasks[employee_id]["completed"]]
    completed = employee_tasks[employee_id]["completed"]

    pending_list = ', '.join(pending) if pending else "No pending tasks."
    completed_list = ', '.join(completed) if completed else "No tasks completed yet."

    return (
        f"Tasks for {employee_id}:\n"
        f"✅ Completed: {completed_list}\n"
        f"🕒 Pending: {pending_list}"
    )

# ----- Greeting Resource -----

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! Welcome to the Employee Manager. How can I assist you today?"

# ----- Start Server -----

if __name__ == "__main__":
    mcp.run()
