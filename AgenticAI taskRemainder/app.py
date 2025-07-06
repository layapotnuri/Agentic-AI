from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from apscheduler.schedulers.background import BackgroundScheduler
import yagmail
from datetime import datetime, timedelta
import os
import json
from openai import OpenAI
from agentic_ai_agent import AgenticReminderAgent
import sqlite3
import re

app = Flask(__name__)
app.secret_key = '148fa85b227a841e5683cc19135c6588a75b7f13023b5b3d3367017e80b396ad'

# Configure your Gmail credentials here
GMAIL_USER = os.environ.get('GMAIL_USER', 'layamaheswari2003@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD','dcskojosqtalnzqw')

# Configure OpenAI API
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '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')

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize agentic AI agent
agentic_agent = AgenticReminderAgent(OPENAI_API_KEY)

# Initialize email and scheduler
yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
scheduler = BackgroundScheduler()
scheduler.start()

def send_intelligent_reminder(email, task_name, task_id):
    """Send intelligent email reminder with AI-generated content"""
    try:
        # Get user patterns for personalized messaging
        patterns = agentic_agent.analyze_user_patterns(email)
        
        # Generate personalized reminder content using AI
        prompt = f"""
        Generate a personalized email reminder for this task:
        
        Task: {task_name}
        User Email: {email}
        User Patterns: {json.dumps(patterns, indent=2)}
        
        Create a friendly, motivating reminder that:
        1. Acknowledges the user's productivity patterns
        2. Provides context about why this time was chosen
        3. Includes a productivity tip based on their history
        4. Encourages completion
        
        Return JSON: {{"subject": "subject line", "body": "email body"}}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        
        ai_content = json.loads(response.choices[0].message.content.strip())
        subject = ai_content.get("subject", f"Task Reminder: {task_name}")
        body = ai_content.get("body", f"This is a reminder for your task: {task_name}")
        
        # Send the email
        yag.send(email, subject, body)
        
        # Log the reminder sent
        agentic_agent._log_decision(email, "reminder_sent", f"Sent reminder for {task_name}", f"Subject: {subject}")
        
        print(f"Intelligent reminder sent to {email} for task: {task_name}")
        
    except Exception as e:
        print(f"Failed to send intelligent email: {e}")
        # Fallback to simple reminder
        try:
            yag.send(email, f"Task Reminder: {task_name}", f"This is a reminder for your task: {task_name}")
        except Exception as fallback_error:
            print(f"Fallback email also failed: {fallback_error}")

def parse_natural_language_with_agent(user_input, email):
    """Use agentic AI to parse natural language and make intelligent decisions"""
    try:
        prompt = f"""
        As an intelligent task scheduling agent, extract task details and make scheduling decisions:
        
        User Input: "{user_input}"
        User Email: {email}
        Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        Analyze the input and provide:
        1. Task name
        2. Suggested optimal time (consider user patterns)
        3. Priority level
        4. Any special considerations
        
        Return JSON: {{
            "task": "task_name",
            "suggested_time": "YYYY-MM-DD HH:MM",
            "priority": "low/medium/high",
            "reasoning": "explanation",
            "confidence": 0.0-1.0
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        
        # Use agentic AI to suggest optimal time based on user patterns
        ai_suggestion = agentic_agent.suggest_optimal_time(email, result["task"], result["suggested_time"])
        
        # Combine AI parsing with agentic suggestions
        final_result = {
            "task": result["task"],
            "suggested_time": ai_suggestion["suggested_time"],
            "priority": result["priority"],
            "reasoning": f"{result['reasoning']} + {ai_suggestion['reasoning']}",
            "confidence": (result["confidence"] + ai_suggestion["confidence"]) / 2
        }
        
        return final_result, None
        
    except Exception as e:
        # Fallback to simple parsing when AI is unavailable
        return parse_natural_language_fallback(user_input, email), None

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
            word_lower not in ['at', 'on', 'by', 'for', 'to']):
            task_words.append(word)
    
    task_name = ' '.join(task_words) if task_words else "Task"
    
    return {
        "task": task_name,
        "suggested_time": suggested_time.strftime('%Y-%m-%d %H:%M'),
        "priority": "normal",
        "reasoning": f"Parsed '{user_input}' - scheduled for {suggested_time.strftime('%Y-%m-%d %H:%M')}",
        "confidence": 0.5
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if user provided natural language input
        natural_input = request.form.get('natural_input', '').strip()
        
        if natural_input:
            # Use agentic AI to parse and make decisions
            result, error = parse_natural_language_with_agent(natural_input, email)
            if error:
                flash(f"AI couldn't understand your request: {error}", 'danger')
                return redirect(url_for('index'))
            
            task_name = result["task"]
            reminder_time = result["suggested_time"]
            priority = result["priority"]
            reasoning = result["reasoning"]
            
        else:
            # Use manual form inputs
            task_name = request.form['task_name']
            reminder_time = request.form['reminder_time']
            priority = "normal"
            reasoning = "Manual input"
        
        # Validate inputs
        if not task_name or not reminder_time:
            flash('Please provide both task name and reminder time.', 'danger')
            return redirect(url_for('index'))
        
        try:
            # Parse the reminder time - handle different formats
            try:
                reminder_dt = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
            except ValueError:
                # Try alternative formats
                try:
                    reminder_dt = datetime.strptime(reminder_time, '%Y-%m-%dT%H:%M')
                except ValueError:
                    try:
                        reminder_dt = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        flash('Invalid date/time format. Please use YYYY-MM-DD HH:MM format.', 'danger')
                        return redirect(url_for('index'))
            
            # Check if time is in the future
            if reminder_dt <= datetime.now():
                flash(f'Reminder time ({reminder_dt.strftime("%Y-%m-%d %H:%M")}) must be in the future. Current time is {datetime.now().strftime("%Y-%m-%d %H:%M")}.', 'danger')
                return redirect(url_for('index'))
            
            # Use agentic AI to make intelligent decisions
            decisions = agentic_agent.make_intelligent_decisions(email, task_name, reminder_time)
            
            # Store task in database for learning
            conn = sqlite3.connect(agentic_agent.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_behavior (email, task_name, scheduled_time)
                VALUES (?, ?, ?)
            ''', [email, task_name, reminder_dt])
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Schedule the intelligent reminder
            scheduler.add_job(
                send_intelligent_reminder, 
                'date', 
                run_date=reminder_dt, 
                args=[email, task_name, task_id],
                id=f"reminder_{task_id}"
            )
            
            # Generate AI confirmation with agentic insights
            confirmation_message = generate_agentic_confirmation(email, task_name, reminder_time, decisions)
            flash(confirmation_message, 'success')
            
            # Store session data for dashboard
            session['user_email'] = email
            
        except ValueError:
            flash('Invalid date/time format. Please use YYYY-MM-DD HH:MM format.', 'danger')
        except Exception as e:
            flash(f'Error scheduling reminder: {e}', 'danger')
        
        return redirect(url_for('index'))
    
    return render_template('index.html')

def generate_agentic_confirmation(email, task_name, reminder_time, decisions):
    """Generate intelligent confirmation message with agentic insights"""
    prompt = f"""
    Generate a friendly, intelligent confirmation message for a task reminder:
    
    Task: {task_name}
    Time: {reminder_time}
    Email: {email}
    Agent Decisions: {json.dumps(decisions, indent=2)}
    
    Include:
    1. Confirmation of the scheduled reminder
    2. Any intelligent suggestions from the agent
    3. Productivity tips if applicable
    4. Encouragement based on user patterns
    
    Keep it conversational and helpful.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except:
        return f"✅ Intelligent reminder set! I'll remind you about '{task_name}' at {reminder_time}"

@app.route('/dashboard')
def dashboard():
    """Show user's productivity dashboard with agentic insights"""
    email = session.get('user_email')
    if not email:
        flash('Please set a reminder first to view your dashboard.', 'info')
        return redirect(url_for('index'))
    
    # Get user's task history
    conn = sqlite3.connect(agentic_agent.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT task_name, scheduled_time, completion_status, created_at
        FROM user_behavior 
        WHERE email = ? 
        ORDER BY created_at DESC
        LIMIT 10
    ''', [email])
    tasks = cursor.fetchall()
    conn.close()
    
    # Get agentic insights
    insights = agentic_agent.get_productivity_insights(email)
    
    return render_template('dashboard.html', 
                         email=email, 
                         tasks=tasks, 
                         insights=insights)

@app.route('/complete_task', methods=['POST'])
def complete_task():
    """Mark a task as completed and let the agent learn"""
    data = request.get_json()
    email = data.get('email')
    task_name = data.get('task_name')
    outcome = data.get('outcome', 'completed')
    feedback = data.get('feedback', '')
    
    # Let the agentic AI learn from the outcome
    agentic_agent.learn_from_outcome(email, task_name, outcome, feedback)
    
    return jsonify({"status": "success", "message": "Task outcome recorded"})

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    """Get intelligent task suggestions from the agent"""
    data = request.get_json()
    email = data.get('email')
    task_name = data.get('task_name')
    scheduled_time = data.get('scheduled_time')
    
    # Get agentic suggestions
    suggestions = agentic_agent.suggest_task_modifications(email, task_name, scheduled_time)
    
    return jsonify({"suggestions": suggestions})

@app.route('/reschedule_task', methods=['POST'])
def reschedule_task():
    """Intelligently reschedule a task using agentic AI"""
    data = request.get_json()
    email = data.get('email')
    task_name = data.get('task_name')
    
    # Get optimal time suggestion from agentic AI
    suggestion = agentic_agent.suggest_optimal_time(email, task_name)
    
    return jsonify({
        "suggested_time": suggestion["suggested_time"],
        "reasoning": suggestion["reasoning"],
        "confidence": suggestion["confidence"]
    })

if __name__ == '__main__':
    app.run(debug=True) 