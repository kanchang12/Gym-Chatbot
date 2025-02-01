from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import requests

app = Flask(__name__)

# Replace with your actual OpenAI API key
openai_api_key = os.environ.get("API-KEY")
client = OpenAI(api_key=openai_api_key)

zapier_webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")

def get_bot_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4",  # You can choose a different model if needed
        messages=[
            {
                "role": "system",
                "content": """
                    Welcome to PowerFit Equipment Co.
                    PowerFit Equipment Co. has been a leader in the fitness equipment industry since 1995. Our mission is to provide innovative, high-quality fitness solutions for individuals and businesses, helping them achieve their health and wellness goals.
                    Our Products:
                    Commercial Treadmills
                    Built for durability and designed to handle high-intensity use in gyms and fitness centers. Features include adjustable speed, incline, and advanced tracking technology.
                    Strength Equipment
                    From free weights to resistance machines, our strength equipment is engineered for performance, comfort, and safety, helping you build muscle and improve strength.
                    Cardio Equipment
                    Ellipticals, stationary bikes, rowing machines, and more, designed to enhance cardiovascular fitness and endurance. Our cardio machines offer various resistance levels and performance tracking.
                    Custom Solutions
                    Looking for something unique? We offer tailored fitness equipment to meet specific business or personal needs, including custom branding, design, and functionality.
                    Our Services:
                    Equipment Installation: Professional setup for all our equipment, ensuring it's ready to use.
                    Maintenance & Repair: Keep your equipment in top shape with our regular maintenance packages. If anything breaks down, we offer efficient repair services.
                    Consultation: Our expert team will guide you in selecting the right equipment and layout for your fitness facility, ensuring you make the most of your investment.
                    Custom Solutions: We can design custom equipment and fitness setups that meet specific requirements, whether for a gym, corporate wellness program, or home use.
                    "You will ask details from the user and interact with them in a friendly way but subtly try to push sales. If a new customer comes, take their input. If complaints come, take email, name, and complaint details."
                """
            },
            {"role": "user", "content": user_input}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    bot_response = response.choices[0].message.content

    if "SCHEDULE_REQUEST|" in bot_response:
        parts = bot_response.split("|")
        if len(parts) == 6:
            success = schedule_appointment(parts[1], parts[2], parts[3], parts[4], parts[5])
            if success:
                return f"Great! I've scheduled your appointment for {parts[3]} at {parts[4]}. You'll receive a confirmation email shortly."
            else:
                return "I apologize, but there was an issue scheduling your appointment. Please try again or contact us directly."

    return bot_response

def schedule_appointment(name, email, date, time, service_type):
    try:
        payload = {
            "name": name,
            "email": email,
            "date": date,
            "time": time,
            "service_type": service_type
        }
        response = requests.post(zapier_webhook_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Scheduling Error: {e}")
        return False

@app.route('/')
def index():
    context = """
    This chatbot is designed to assist users with inquiries related to PowerFit Equipment Co., a fitness equipment company. 
    PowerFit offers a range of products and services, including:
    - Products: Commercial Treadmills, Strength Equipment, Cardio Equipment
    - Services: Equipment Installation, Maintenance & Repair, Consultation, Custom Solutions
    """
    return render_template('index.html', context=context)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    bot_response = get_bot_response(user_message)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
