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


@tool
def check_ticket_status(ticket_id: str = None) -> str:
    """
    Checks the status of an HR ticket. If no ticket ID provided, returns recent tickets.

    Args:
        ticket_id: Ticket ID (optional, format: TKT-XXXXXX)

    Returns:
        Ticket status information
    """
    # Mock data - in production, this would query a database
    statuses = ["Open", "In Progress", "Pending", "Resolved"]
    priorities = ["Low", "Normal", "High"]

    if ticket_id:
        # Check specific ticket
        status = random.choice(statuses)
        priority = random.choice(priorities)
        days_ago = random.randint(1, 10)

        return f"""🎫 Ticket Status

Ticket ID: {ticket_id}
Status: {status}
Priority: {priority}
Created: {days_ago} day(s) ago
Last Updated: {random.randint(0, days_ago)} day(s) ago

{f"Expected Resolution: Within 24-48 hours" if status in ["Open", "In Progress"] else "Ticket has been resolved. Check your email for details."}

For urgent matters, please contact HR directly."""
    else:
        # Return recent tickets
        num_tickets = random.randint(1, 3)
        tickets = []
        for i in range(num_tickets):
            tid = 'TKT-' + ''.join(random.choices(string.digits, k=6))
            status = random.choice(statuses)
            days_ago = random.randint(1, 15)
            tickets.append(f"  • {tid} - {status} (Created {days_ago} days ago)")

        tickets_list = '\n'.join(tickets)
        return f"""🎫 Your Recent Tickets

{tickets_list}

To check a specific ticket status, please provide the ticket ID.
For urgent matters, contact HR directly at hr@company.com"""


# List of all tools
ALL_TOOLS = [create_hr_ticket, check_leave_balance, check_ticket_status]

# Tool mapping for easy access
TOOL_MAP = {
    "create_hr_ticket": create_hr_ticket,
    "check_leave_balance": check_leave_balance,
    "check_ticket_status": check_ticket_status
}

