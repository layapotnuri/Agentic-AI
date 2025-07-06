import sqlite3
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from openai import OpenAI
import os
from typing import Dict, List, Tuple, Optional
import logging

class AgenticReminderAgent:
    """
    An agentic AI agent that autonomously manages task reminders,
    learns from user behavior, and makes intelligent decisions.
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.client = OpenAI(api_key=openai_api_key)
        self.db_path = "agentic_reminders.db"
        self.setup_database()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the agent's decisions and actions"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agentic_agent.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        """Initialize database for storing user behavior and learning data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User behavior tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behavior (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                task_name TEXT,
                scheduled_time DATETIME,
                completion_time DATETIME,
                completion_status TEXT,
                user_feedback TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Agent decisions and reasoning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                decision_type TEXT,
                reasoning TEXT,
                action_taken TEXT,
                outcome TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User preferences and patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                preferred_times TEXT,
                task_categories TEXT,
                productivity_patterns TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def analyze_user_patterns(self, email: str) -> Dict:
        """Analyze user's historical behavior to understand patterns"""
        conn = sqlite3.connect(self.db_path)
        
        # Get user's task history
        df = pd.read_sql_query('''
            SELECT * FROM user_behavior 
            WHERE email = ? 
            ORDER BY created_at DESC
        ''', conn, params=[email])
        
        conn.close()
        
        if df.empty:
            return {"patterns": "new_user", "preferred_times": [], "productivity_score": 0.5}
        
        # Analyze completion patterns
        completion_rate = len(df[df['completion_status'] == 'completed']) / len(df)
        
        # Analyze time patterns
        df['hour'] = pd.to_datetime(df['scheduled_time']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['scheduled_time']).dt.dayofweek
        
        # Find preferred hours
        hour_counts = df['hour'].value_counts()
        preferred_hours = hour_counts.head(3).index.tolist()
        
        # Find preferred days
        day_counts = df['day_of_week'].value_counts()
        preferred_days = day_counts.head(3).index.tolist()
        
        # Calculate productivity score based on completion rate and timing
        productivity_score = completion_rate * 0.7 + (1 - df['hour'].std() / 24) * 0.3
        
        return {
            "patterns": "established_user",
            "completion_rate": completion_rate,
            "preferred_hours": preferred_hours,
            "preferred_days": preferred_days,
            "productivity_score": productivity_score,
            "total_tasks": len(df)
        }
        
    def suggest_optimal_time(self, email: str, task_name: str, user_preferred_time: str = None) -> str:
        """Use AI to suggest the optimal time for a task based on user patterns"""
        patterns = self.analyze_user_patterns(email)
        
        # Try AI first, fallback to heuristics if quota exceeded
        try:
            prompt = f"""
            As an intelligent task scheduling agent, suggest the optimal time for this task:
            
            Task: {task_name}
            User Email: {email}
            User Patterns: {json.dumps(patterns, indent=2)}
            User's Preferred Time: {user_preferred_time if user_preferred_time else "Not specified"}
            Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            
            Consider:
            1. User's historical completion patterns
            2. Preferred working hours
            3. Task complexity and estimated duration
            4. Current workload and schedule
            5. Optimal productivity windows
            
            Return ONLY a JSON object: {{"suggested_time": "YYYY-MM-DD HH:MM", "reasoning": "explanation", "confidence": 0.0-1.0}}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            self.logger.info(f"AI suggested time for {task_name}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error suggesting optimal time: {e}")
            # Fallback to intelligent heuristics
            return self._fallback_time_suggestion(email, task_name, user_preferred_time, patterns)
    
    def _fallback_time_suggestion(self, email: str, task_name: str, user_preferred_time: str, patterns: Dict) -> Dict:
        """Fallback time suggestion using heuristics when AI is unavailable"""
        now = datetime.now()
        
        # If user provided a preferred time, use it
        if user_preferred_time:
            try:
                suggested_dt = datetime.strptime(user_preferred_time, '%Y-%m-%d %H:%M')
                return {
                    "suggested_time": user_preferred_time,
                    "reasoning": "Using your preferred time",
                    "confidence": 0.8
                }
            except:
                pass
        
        # Use user's preferred hours if available
        if patterns.get("preferred_hours") and patterns["patterns"] == "established_user":
            # Get the most preferred hour
            preferred_hour = patterns["preferred_hours"][0]
            
            # Schedule for today at preferred hour, or tomorrow if today's preferred hour has passed
            suggested_dt = now.replace(hour=preferred_hour, minute=0, second=0, microsecond=0)
            if suggested_dt <= now:
                suggested_dt += timedelta(days=1)
            
            return {
                "suggested_time": suggested_dt.strftime('%Y-%m-%d %H:%M'),
                "reasoning": f"Based on your preferred working hour ({preferred_hour}:00)",
                "confidence": 0.7
            }
        
        # Default fallback: schedule for tomorrow at 9 AM
        tomorrow = now + timedelta(days=1)
        suggested_dt = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        
        return {
            "suggested_time": suggested_dt.strftime('%Y-%m-%d %H:%M'),
            "reasoning": "Scheduled for tomorrow morning (9:00 AM) as a default time",
            "confidence": 0.5
        }
                
    def make_intelligent_decisions(self, email: str, task_name: str, scheduled_time: str) -> Dict:
        """Make autonomous decisions about task management"""
        patterns = self.analyze_user_patterns(email)
        
        # Analyze current workload
        conn = sqlite3.connect(self.db_path)
        current_tasks = pd.read_sql_query('''
            SELECT * FROM user_behavior 
            WHERE email = ? AND scheduled_time > ? AND completion_status IS NULL
        ''', conn, params=[email, datetime.now().strftime('%Y-%m-%d %H:%M')])
        conn.close()
        
        decisions = {
            "should_reschedule": False,
            "priority_level": "normal",
            "suggested_breaks": [],
            "productivity_tips": [],
            "reasoning": ""
        }
        
        # Decision 1: Check if user is overbooked
        if len(current_tasks) > 5:
            decisions["should_reschedule"] = True
            decisions["reasoning"] = "User has too many pending tasks. Suggesting rescheduling."
            
        # Decision 2: Determine priority based on patterns
        if patterns.get("completion_rate", 0) < 0.5:
            decisions["priority_level"] = "high"
            decisions["productivity_tips"].append("Consider breaking this task into smaller chunks")
            
        # Decision 3: Suggest breaks based on task timing
        scheduled_dt = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M')
        if scheduled_dt.hour >= 14:  # Afternoon tasks
            decisions["suggested_breaks"].append("Take a 15-minute break before this task")
            
        # Use AI for complex decision making
        ai_decisions = self._get_ai_decisions(email, task_name, scheduled_time, patterns, len(current_tasks))
        decisions.update(ai_decisions)
        
        # Log the decision
        self._log_decision(email, "task_scheduling", decisions["reasoning"], str(decisions))
        
        return decisions
        
    def _get_ai_decisions(self, email: str, task_name: str, scheduled_time: str, patterns: Dict, current_task_count: int) -> Dict:
        """Get AI-powered decisions for task management"""
        try:
            prompt = f"""
            As an intelligent task management agent, analyze this situation and make recommendations:
            
            Task: {task_name}
            Scheduled Time: {scheduled_time}
            User Patterns: {json.dumps(patterns, indent=2)}
            Current Pending Tasks: {current_task_count}
            
            Provide recommendations for:
            1. Task priority (low/medium/high)
            2. Whether to suggest rescheduling
            3. Productivity tips
            4. Break suggestions
            5. Task optimization ideas
            
            Return JSON: {{
                "priority_level": "low/medium/high",
                "should_reschedule": true/false,
                "productivity_tips": ["tip1", "tip2"],
                "suggested_breaks": ["break1", "break2"],
                "task_optimization": "suggestion"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.4
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            self.logger.error(f"Error getting AI decisions: {e}")
            return self._fallback_decisions(email, task_name, scheduled_time, patterns, current_task_count)
    
    def _fallback_decisions(self, email: str, task_name: str, scheduled_time: str, patterns: Dict, current_task_count: int) -> Dict:
        """Fallback decisions using heuristics when AI is unavailable"""
        decisions = {
            "priority_level": "normal",
            "should_reschedule": False,
            "productivity_tips": [],
            "suggested_breaks": [],
            "task_optimization": "Consider breaking this task into smaller steps if it seems complex"
        }
        
        # Simple heuristics
        if current_task_count > 5:
            decisions["should_reschedule"] = True
            decisions["productivity_tips"].append("You have many pending tasks. Consider rescheduling some.")
        
        if patterns.get("completion_rate", 0) < 0.5:
            decisions["priority_level"] = "high"
            decisions["productivity_tips"].append("Based on your patterns, this task might need extra attention.")
        
        # Suggest breaks for afternoon tasks
        try:
            scheduled_dt = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M')
            if scheduled_dt.hour >= 14:
                decisions["suggested_breaks"].append("Take a short break before this afternoon task.")
        except:
            pass
        
        return decisions
            
    def learn_from_outcome(self, email: str, task_name: str, outcome: str, feedback: str = None):
        """Learn from task outcomes to improve future decisions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update task completion status
        cursor.execute('''
            UPDATE user_behavior 
            SET completion_status = ?, user_feedback = ?, completion_time = ?
            WHERE email = ? AND task_name = ? AND completion_status IS NULL
            ORDER BY created_at DESC LIMIT 1
        ''', [outcome, feedback, datetime.now(), email, task_name])
        
        # Update user preferences based on outcome
        if outcome == "completed":
            # Learn successful patterns
            self._update_user_preferences(email, "successful_completion", task_name)
        else:
            # Learn from failures
            self._update_user_preferences(email, "failed_completion", task_name)
            
        conn.commit()
        conn.close()
        
        self.logger.info(f"Learned from outcome: {email} - {task_name} - {outcome}")
        
    def _update_user_preferences(self, email: str, outcome_type: str, task_name: str):
        """Update user preferences based on task outcomes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current preferences
        cursor.execute('SELECT * FROM user_preferences WHERE email = ?', [email])
        result = cursor.fetchone()
        
        if result:
            # Update existing preferences
            preferences = json.loads(result[3]) if result[3] else {}
        else:
            # Create new preferences
            preferences = {}
            cursor.execute('''
                INSERT INTO user_preferences (email, task_categories, productivity_patterns)
                VALUES (?, ?, ?)
            ''', [email, '{}', '{}'])
            
        # Update based on outcome
        if outcome_type == "successful_completion":
            if "successful_tasks" not in preferences:
                preferences["successful_tasks"] = []
            preferences["successful_tasks"].append(task_name)
        else:
            if "challenging_tasks" not in preferences:
                preferences["challenging_tasks"] = []
            preferences["challenging_tasks"].append(task_name)
            
        # Update database
        cursor.execute('''
            UPDATE user_preferences 
            SET task_categories = ?, last_updated = ?
            WHERE email = ?
        ''', [json.dumps(preferences), datetime.now(), email])
        
        conn.commit()
        conn.close()
        
    def _log_decision(self, email: str, decision_type: str, reasoning: str, action: str):
        """Log agent decisions for transparency and learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_decisions (email, decision_type, reasoning, action_taken)
            VALUES (?, ?, ?, ?)
        ''', [email, decision_type, reasoning, action])
        
        conn.commit()
        conn.close()
        
    def get_productivity_insights(self, email: str) -> Dict:
        """Provide intelligent insights about user's productivity patterns"""
        patterns = self.analyze_user_patterns(email)
        
        try:
            prompt = f"""
            Based on this user's productivity data, provide actionable insights:
            
            User Patterns: {json.dumps(patterns, indent=2)}
            
            Provide insights about:
            1. Best working hours
            2. Task completion patterns
            3. Areas for improvement
            4. Personalized recommendations
            
            Return JSON: {{
                "best_hours": "analysis",
                "completion_patterns": "analysis", 
                "improvement_areas": ["area1", "area2"],
                "recommendations": ["rec1", "rec2"],
                "productivity_score": 0.0-1.0
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            self.logger.error(f"Error getting productivity insights: {e}")
            return self._fallback_productivity_insights(patterns)
    
    def _fallback_productivity_insights(self, patterns: Dict) -> Dict:
        """Fallback productivity insights using heuristics"""
        if patterns["patterns"] == "new_user":
            return {
                "best_hours": "Start using the system to discover your optimal working hours",
                "completion_patterns": "No patterns yet - your data will help improve suggestions",
                "improvement_areas": ["Start tracking your tasks regularly"],
                "recommendations": ["Create your first few reminders to establish patterns"],
                "productivity_score": 0.5
            }
        
        # For established users, provide insights based on patterns
        completion_rate = patterns.get("completion_rate", 0)
        preferred_hours = patterns.get("preferred_hours", [])
        
        insights = {
            "productivity_score": completion_rate,
            "completion_patterns": f"You complete {completion_rate*100:.1f}% of your scheduled tasks",
            "recommendations": []
        }
        
        if preferred_hours:
            insights["best_hours"] = f"Your most productive hours are around {preferred_hours[0]}:00"
        else:
            insights["best_hours"] = "Continue using the system to identify your best working hours"
        
        if completion_rate < 0.7:
            insights["improvement_areas"] = ["Task completion rate could be improved"]
            insights["recommendations"].append("Try scheduling tasks during your preferred hours")
        else:
            insights["improvement_areas"] = ["You're doing great! Keep up the good work"]
            insights["recommendations"].append("Consider adding more challenging tasks")
        
        return insights
            
    def suggest_task_modifications(self, email: str, task_name: str, scheduled_time: str) -> List[str]:
        """Suggest intelligent modifications to improve task success"""
        patterns = self.analyze_user_patterns(email)
        
        try:
            prompt = f"""
            Suggest intelligent modifications for this task to improve success rate:
            
            Task: {task_name}
            Scheduled Time: {scheduled_time}
            User Patterns: {json.dumps(patterns, indent=2)}
            
            Consider:
            1. Breaking down complex tasks
            2. Optimal timing adjustments
            3. Preparation suggestions
            4. Related task grouping
            
            Return JSON array of suggestions: ["suggestion1", "suggestion2", "suggestion3"]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.4
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            self.logger.error(f"Error suggesting task modifications: {e}")
            return self._fallback_task_modifications(task_name, patterns)
    
    def _fallback_task_modifications(self, task_name: str, patterns: Dict) -> List[str]:
        """Fallback task modification suggestions using heuristics"""
        suggestions = ["Consider breaking this task into smaller steps"]
        
        # Add suggestions based on patterns
        if patterns.get("completion_rate", 0) < 0.6:
            suggestions.append("Schedule this task during your most productive hours")
        
        if len(task_name.split()) > 5:  # Long task name might indicate complexity
            suggestions.append("This seems like a complex task - consider preparation time")
        
        suggestions.append("Set aside dedicated time without distractions")
        
        return suggestions 