#!/usr/bin/env python3

try:
    from flask import Flask
    print("✅ Flask imported successfully")
except Exception as e:
    print(f"❌ Flask import error: {e}")

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    print("✅ APScheduler imported successfully")
except Exception as e:
    print(f"❌ APScheduler import error: {e}")

try:
    import yagmail
    print("✅ Yagmail imported successfully")
except Exception as e:
    print(f"❌ Yagmail import error: {e}")

try:
    from openai import OpenAI
    print("✅ OpenAI imported successfully")
except Exception as e:
    print(f"❌ OpenAI import error: {e}")

try:
    import numpy as np
    print("✅ NumPy imported successfully")
except Exception as e:
    print(f"❌ NumPy import error: {e}")

try:
    import pandas as pd
    print("✅ Pandas imported successfully")
except Exception as e:
    print(f"❌ Pandas import error: {e}")

try:
    from sklearn.cluster import KMeans
    print("✅ Scikit-learn imported successfully")
except Exception as e:
    print(f"❌ Scikit-learn import error: {e}")

try:
    from agentic_ai_agent import AgenticReminderAgent
    print("✅ AgenticReminderAgent imported successfully")
except Exception as e:
    print(f"❌ AgenticReminderAgent import error: {e}")

print("\n🎉 All imports completed!") 