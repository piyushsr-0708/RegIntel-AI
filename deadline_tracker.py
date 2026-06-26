import re
from datetime import datetime

class DeadlineTracker:
    """
    Parses deadline strings from requirements and determines urgency status.
    """
    
    @staticmethod
    def parse_deadline(deadline_str: str) -> str:
        """
        Returns a normalized deadline string.
        """
        if not deadline_str or not str(deadline_str).strip():
            return "TBD"
        return str(deadline_str).strip()

    @staticmethod
    def determine_urgency(deadline_str: str) -> str:
        """
        Determines the urgency of a deadline.
        In a production system this would parse dates and compare to today.
        For this prototype, we'll use a basic heuristic based on common RBI phrases,
        and default to 'Unknown' if a specific timeframe isn't recognized, or 'No Deadline' if TBD.
        """
        if not deadline_str or deadline_str == "TBD":
            return "No Deadline"
            
        deadline_lower = deadline_str.lower()
        if "immediate" in deadline_lower or "forthwith" in deadline_lower or "overdue" in deadline_lower:
            return "Overdue"
        elif "days" in deadline_lower or "month" in deadline_lower or "quarter" in deadline_lower:
            return "Upcoming"
        elif re.search(r'20\d{2}', deadline_lower):
            # Contains a year
            return "Scheduled"
            
        return "Unknown"
