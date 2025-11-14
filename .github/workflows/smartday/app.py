from flask import Flask, request, jsonify
import openai
import os
import json

app = Flask(__name__)

# Initialize OpenAI
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/')
def smartday_home():
    return """
    <html>
    <head>
        <title>SmartDay - AI Daily Planner</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
            textarea { width: 100%; padding: 10px; margin: 10px 0; }
            button { background: #0078d4; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .schedule { background: #f5f5f5; padding: 20px; margin-top: 20px; border-radius: 4px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>🎯 SmartDay AI Planner</h1>
        <p>Enter your tasks and get an optimized daily schedule!</p>
        
        <div>
            <h3>Your Tasks:</h3>
            <textarea id="tasks" rows="4" placeholder="e.g., Gym 1 hour, Work on project 3 hours, Team meeting at 2 PM, Grocery shopping 45 minutes"></textarea><br>
            <button onclick="createSchedule()">Create My Schedule</button>
        </div>
        
        <div id="schedule" class="schedule"></div>
        
        <script>
        async function createSchedule() {
            const tasks = document.getElementById('tasks').value;
            const button = event.target;
            button.textContent = 'Creating...';
            button.disabled = true;
            
            try {
                const response = await fetch('/create_schedule', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tasks: tasks})
                });
                const data = await response.json();
                if (data.schedule) {
                    document.getElementById('schedule').innerHTML = '<h3>📅 Your Optimized Schedule:</h3><pre>' + data.schedule + '</pre>';
                } else {
                    document.getElementById('schedule').innerHTML = '<p style="color: red;">Error: ' + data.error + '</p>';
                }
            } catch (error) {
                document.getElementById('schedule').innerHTML = '<p style="color: red;">Network error: ' + error + '</p>';
            }
            
            button.textContent = 'Create My Schedule';
            button.disabled = false;
        }
        </script>
    </body>
    </html>
    """

@app.route('/create_schedule', methods=['POST'])
def create_schedule():
    try:
        data = request.get_json()
        tasks = data.get('tasks', '')
        
        if not tasks:
            return jsonify({"error": "Please enter some tasks"}), 400
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """You are SmartDay, a daily planning assistant. Create optimized schedules that consider:
                    - Time blocking with specific times
                    - Energy levels throughout the day
                    - Realistic task durations
                    - Breaks and transition time
                    - Morning routine, meals, and bedtime
                    Format as a clear time-block schedule from morning to evening."""
                },
                {
                    "role": "user",
                    "content": f"Create an optimized daily schedule for these tasks: {tasks}. Include morning routine, meals, work blocks, breaks, and evening wind-down."
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        schedule = response.choices[0].message.content
        return jsonify({"schedule": schedule})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
