import anthropic
import os
import json

def get_schedule():
    """Get weekly schedule from user"""
    print("\n" + "="*60)
    print("WEEKLY SCHEDULE")
    print("="*60)
    print("For each day, enter your activities with time blocks.")
    print("Format: 'HH:MM-HH:MM Activity name' (e.g., '09:00-10:30 Team meeting')")
    print("Press Enter on empty line when done with that day.")
    print("Activities can overlap - this helps identify time conflicts!\n")
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    schedule = {}
    
    for day in days:
        print(f"\n--- {day} ---")
        activities = []
        while True:
            activity = input(f"  {day} activity (or press Enter to finish): ").strip()
            if not activity:
                break
            activities.append(activity)
        schedule[day] = activities
    
    return schedule

def get_goals():
    """Get goals from user"""
    print("\n" + "="*60)
    print("YOUR GOALS")
    print("="*60)
    print("Enter your goals. Type 'done' when finished.\n")
    
    goals = []
    while True:
        goal = input("Goal: ").strip()
        if goal.lower() == 'done':
            break
        if goal:
            timeframe = input("  Timeframe (short/medium/long): ").strip().lower()
            if timeframe not in ['short', 'medium', 'long']:
                timeframe = 'short'
            goals.append({'text': goal, 'timeframe': timeframe})
    
    return goals

def generate_tips(schedule, goals):
    """Generate AI tips based on schedule and goals"""
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nERROR: ANTHROPIC_API_KEY environment variable not set!")
        print("Set it with: export ANTHROPIC_API_KEY='your-api-key-here'")
        return None
    
    # Build prompt
    schedule_text = ""
    for day, activities in schedule.items():
        if activities:
            schedule_text += f"\n{day}:\n"
            for activity in activities:
                schedule_text += f"  - {activity}\n"
        else:
            schedule_text += f"\n{day}: No activities listed\n"
    
    goals_text = ""
    for goal in goals:
        goals_text += f"  - {goal['text']} ({goal['timeframe']}-term)\n"
    
    if not goals_text:
        goals_text = "  No specific goals listed\n"
    
    prompt = f"""You are a life coach and productivity expert. A person has shared their weekly schedule and goals. Please analyze them and provide 5-7 specific, actionable tips to help them achieve their goals while maintaining balance.

Pay special attention to:
- Time conflicts and overlapping activities
- Work-life balance
- Time for goal-related activities
- Gaps in the schedule that could be utilized
- Overcommitment or underutilization

Weekly Schedule:
{schedule_text}

Goals:
{goals_text}

Please provide tips in the following format - each tip should be a JSON object with "category" (one of: time-management, habits, priorities, balance, strategy) and "tip" (the actual advice). Return ONLY a JSON array of these objects, no other text.

Example format:
[
  {{"category": "time-management", "tip": "Block out 30 minutes every morning for your most important task"}},
  {{"category": "balance", "tip": "I notice overlapping activities on Tuesday - consider prioritizing one"}}
]"""
    
    print("\nAnalyzing your schedule and goals...")
    print("This may take a moment...\n")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        tips = json.loads(cleaned_text)
        
        return tips
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return None

def display_tips(tips):
    """Display the generated tips"""
    if not tips:
        return
    
    print("\n" + "="*60)
    print("YOUR PERSONALIZED TIPS")
    print("="*60)
    
    category_emojis = {
        'time-management': '⏰',
        'habits': '✅',
        'priorities': '⭐',
        'balance': '⚖️',
        'strategy': '🎯'
    }
    
    for i, tip in enumerate(tips, 1):
        category = tip['category']
        emoji = category_emojis.get(category, '💡')
        category_name = category.replace('-', ' ').upper()
        
        print(f"\n{i}. {emoji} {category_name}")
        print(f"   {tip['tip']}")
    
    print("\n" + "="*60)

def display_schedule_summary(schedule):
    """Show a summary of the schedule"""
    print("\n" + "="*60)
    print("YOUR SCHEDULE SUMMARY")
    print("="*60)
    
    for day, activities in schedule.items():
        print(f"\n{day}:")
        if activities:
            for activity in activities:
                print(f"  • {activity}")
        else:
            print("  • No activities")

def display_goals_summary(goals):
    """Show a summary of goals"""
    print("\n" + "="*60)
    print("YOUR GOALS SUMMARY")
    print("="*60)
    
    if goals:
        for goal in goals:
            print(f"  • {goal['text']} ({goal['timeframe']}-term)")
    else:
        print("  • No goals set")

def main():
    print("\n" + "="*60)
    print("AI LIFE PLANNER")
    print("="*60)
    print("Plan your week and get personalized AI coaching!\n")
    
    # Get user input
    schedule = get_schedule()
    goals = get_goals()
    
    # Show summary
    display_schedule_summary(schedule)
    display_goals_summary(goals)
    
    # Confirm before generating
    print("\n" + "="*60)
    confirm = input("\nGenerate AI tips? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        tips = generate_tips(schedule, goals)
        if tips:
            display_tips(tips)
    else:
        print("\nNo problem! Run the program again when you're ready.")
    
    print("\n✨ Thank you for using AI Life Planner!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")