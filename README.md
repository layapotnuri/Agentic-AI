# Agentic-AI
# Agentic AI Task Reminder System

An intelligent task reminder system powered by agentic AI that learns from your behavior, makes autonomous decisions, and continuously improves your productivity.

## 🤖 What Makes This Agentic AI?

Unlike traditional reminder apps, this system features **true agentic AI** that:

### 🧠 **Learns & Adapts**
- Analyzes your productivity patterns over time
- Learns from task completion outcomes
- Adapts suggestions based on your behavior
- Builds personalized user profiles

### 🎯 **Makes Autonomous Decisions**
- Suggests optimal scheduling times without user input
- Prioritizes tasks based on your patterns
- Recommends task modifications for better success
- Automatically adjusts strategies based on outcomes

### 📊 **Provides Intelligent Insights**
- Generates personalized productivity insights
- Identifies improvement areas
- Suggests optimal working hours
- Tracks completion patterns and trends

### 🔄 **Continuous Improvement**
- Learns from every interaction
- Updates user preferences automatically
- Improves suggestions over time
- Adapts to changing work patterns

## 🚀 Features

### Natural Language Processing
- Describe tasks in plain English: *"Remind me to call John tomorrow at 3pm"*
- AI extracts task details and suggests optimal times
- Handles complex scheduling requests intelligently

### Intelligent Scheduling
- AI suggests optimal times based on your patterns
- Considers your workload and productivity windows
- Adapts to your preferred working hours
- Learns from successful vs. failed completions

### Personalized Reminders
- AI-generated email content based on your patterns
- Motivational messaging tailored to your style
- Productivity tips based on your history
- Context-aware suggestions

### Productivity Dashboard
- Real-time productivity score
- AI-generated insights and recommendations
- Task completion tracking
- Areas for improvement identification

### Agentic Decision Making
- Autonomous task prioritization
- Intelligent rescheduling suggestions
- Task modification recommendations
- Workload optimization

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Gmail account with app password

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-ai-task-reminder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file or set environment variables
   export OPENAI_API_KEY="your-openai-api-key"
   export GMAIL_USER="your-email@gmail.com"
   export GMAIL_APP_PASSWORD="your-gmail-app-password"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Start creating intelligent reminders!

## 📖 Usage Guide

### Creating Your First Reminder

1. **Natural Language Input** (Recommended)
   - Enter your email
   - Describe your task naturally: *"Call mom this evening"*
   - Let AI handle the scheduling

2. **Manual Input** (Alternative)
   - Fill in task name and time manually
   - AI will still provide intelligent suggestions

### Using the Dashboard

1. **View AI Insights**
   - Check your productivity score
   - Review AI recommendations
   - See areas for improvement

2. **Track Tasks**
   - Mark tasks as completed or missed
   - Provide feedback for AI learning
   - View task history

3. **Get AI Suggestions**
   - Ask for task optimization tips
   - Get rescheduling suggestions
   - Receive productivity insights

## 🧠 How the Agentic AI Works

### 1. Learning Phase
```
User creates task → AI analyzes patterns → Stores behavior data
```

### 2. Decision Making
```
New task request → AI reviews user patterns → Suggests optimal time
```

### 3. Continuous Improvement
```
Task completed → AI learns from outcome → Updates user profile
```

### 4. Autonomous Actions
```
AI monitors patterns → Suggests improvements → Adapts strategies
```

## 🔧 Technical Architecture

### Core Components

- **AgenticReminderAgent**: Main AI agent class
- **Flask Web App**: User interface and API endpoints
- **SQLite Database**: Stores user behavior and learning data
- **OpenAI GPT-4**: Powers natural language understanding and decision making
- **APScheduler**: Handles reminder scheduling
- **Yagmail**: Sends intelligent email reminders

### Database Schema

```sql
-- User behavior tracking
user_behavior (id, email, task_name, scheduled_time, completion_status, feedback)

-- Agent decisions and reasoning
agent_decisions (id, email, decision_type, reasoning, action_taken, outcome)

-- User preferences and patterns
user_preferences (id, email, preferred_times, task_categories, productivity_patterns)
```

## 🎯 AI Capabilities

### Natural Language Understanding
- Extracts task names from complex descriptions
- Understands time references and context
- Handles ambiguous requests intelligently

### Pattern Recognition
- Identifies preferred working hours
- Recognizes productivity patterns
- Learns from completion rates

### Decision Making
- Suggests optimal scheduling times
- Prioritizes tasks based on patterns
- Recommends task modifications

### Personalization
- Generates personalized email content
- Adapts suggestions to user style
- Provides contextual recommendations

## 🔮 Future Enhancements

### Planned Features
- **Advanced Analytics**: Detailed productivity reports and trends
- **Integration APIs**: Connect with calendar and productivity tools
- **Mobile App**: Native mobile experience
- **Team Features**: Collaborative task management
- **Voice Interface**: Voice-activated task creation

### AI Improvements
- **Predictive Scheduling**: Anticipate user needs
- **Context Awareness**: Consider external factors (weather, events)
- **Emotional Intelligence**: Adapt to user mood and stress levels
- **Proactive Suggestions**: Suggest tasks before user thinks of them

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:
- Code style and standards
- Testing requirements
- Documentation updates
- Feature proposals

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 API
- Flask community for the web framework
- All contributors and users who provide feedback

---

**Ready to experience true agentic AI? Start creating intelligent reminders today!** 🚀 
