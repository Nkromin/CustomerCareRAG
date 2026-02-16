"""
Tools for the agent
"""
from langchain_core.tools import tool
import random
import string
from datetime import datetime


@tool
def create_hr_ticket(issue: str) -> str:
    """
    Creates an HR support ticket for employee issues.

    Args:
        issue: Description of the issue or request

    Returns:
        Ticket ID and confirmation message
    """
    # Generate random ticket ID
    ticket_id = 'TKT-' + ''.join(random.choices(string.digits, k=6))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""✓ HR Ticket Created Successfully

Ticket ID: {ticket_id}
Issue: {issue}
Status: Open
Created: {timestamp}
Priority: Normal

Your ticket has been submitted to the HR team. You will receive a response within 24-48 hours."""


@tool
def check_leave_balance(employee_id: str) -> str:
    """
    Checks the leave balance for an employee.

    Args:
        employee_id: Employee ID or email

    Returns:
        Leave balance information
    """
    # Mock data - in production, this would query a database
    leave_data = {
        "annual_leave": random.randint(5, 20),
        "sick_leave": random.randint(3, 10),
        "personal_leave": random.randint(2, 5)
    }

    return f"""📊 Leave Balance for Employee: {employee_id}

Annual Leave: {leave_data['annual_leave']} days
Sick Leave: {leave_data['sick_leave']} days
Personal Leave: {leave_data['personal_leave']} days

Total Available: {sum(leave_data.values())} days

Note: Balance updates at the start of each month."""


# List of all tools
ALL_TOOLS = [create_hr_ticket, check_leave_balance]

# Tool mapping for easy access
TOOL_MAP = {
    "create_hr_ticket": create_hr_ticket,
    "check_leave_balance": check_leave_balance
}

