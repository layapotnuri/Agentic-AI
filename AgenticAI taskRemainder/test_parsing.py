#!/usr/bin/env python3

from datetime import datetime, timedelta
import re

def test_parsing():
    """Test the natural language parsing function"""
    
    test_cases = [
        "Call mom today at 12pm",
        "Submit project tomorrow at 3:30pm", 
        "Gym workout this evening",
        "Meeting tomorrow morning",
        "Dinner tonight at 7pm",
        "Study session at 2pm"
    ]
    
    print("Testing Natural Language Parsing:")
    print("=" * 50)
    
    for test_input in test_cases:
        result = parse_natural_language_fallback(test_input, "test@example.com")
        print(f"Input: '{test_input}'")
        print(f"Task: {result['task']}")
        print(f"Time: {result['suggested_time']}")
        print(f"Reasoning: {result['reasoning']}")
        print("-" * 30)

def parse_natural_language_fallback(user_input, email):
    """Simple fallback parsing when AI is unavailable"""
    # Simple keyword-based parsing
    user_input_lower = user_input.lower()
    
    # Extract common time keywords
    time_keywords = {
        'today': 0,
        'tomorrow': 1,
        'morning': 9,
        'afternoon': 14,
        'evening': 18,
        'night': 20
    }
    
    # Default to tomorrow at 9 AM
    days_ahead = 1
    hour = 9
    minute = 0
    
    # Check for specific time patterns like "12pm", "3:30pm", etc.
    time_pattern = r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)'
    time_match = re.search(time_pattern, user_input_lower)
    
    if time_match:
        hour = int(time_match.group(1))
        if time_match.group(3) == 'pm' and hour != 12:
            hour += 12
        elif time_match.group(3) == 'am' and hour == 12:
            hour = 0
        if time_match.group(2):
            minute = int(time_match.group(2))
    
    # Check for day keywords
    for keyword, value in time_keywords.items():
        if keyword in user_input_lower:
            if keyword in ['today', 'tomorrow']:
                days_ahead = value
            elif hour == 9:  # Only use default hour if no specific time was found
                hour = value
    
    # Calculate suggested time
    suggested_time = datetime.now() + timedelta(days=days_ahead)
    suggested_time = suggested_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If the suggested time is in the past, move to next day
    if suggested_time <= datetime.now():
        suggested_time += timedelta(days=1)
    
    # Extract task name (remove time-related words)
    task_words = []
    for word in user_input.split():
        word_lower = word.lower()
        if (word_lower not in time_keywords and 
            not re.match(time_pattern, word_lower) and
            word_lower not in ['at', 'on', 'by', 'for', 'to', 'this']):
            task_words.append(word)
    
    task_name = ' '.join(task_words) if task_words else "Task"
    
    return {
        "task": task_name,
        "suggested_time": suggested_time.strftime('%Y-%m-%d %H:%M'),
        "priority": "normal",
        "reasoning": f"Parsed '{user_input}' - scheduled for {suggested_time.strftime('%Y-%m-%d %H:%M')}",
        "confidence": 0.5
    }

if __name__ == "__main__":
    test_parsing() 