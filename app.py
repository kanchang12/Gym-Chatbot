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
        messages=[{
            "role": "system",
            "content": """
                Welcome to PowerFit Equipment Co.
                PowerFit Equipment Co. has been a leader in the fitness equipment industry since 1995. 
                Our mission is to provide innovative, high-quality fitness solutions for individuals and businesses, helping them achieve their health and wellness goals.
                Our Products:
                Commercial Treadmills
                Built for durability and designed to handle high-intensity use in gyms and fitness centers.
                Strength Equipment
                From free weights to resistance machines, our strength equipment is engineered for performance, comfort, and safety.
                Cardio Equipment
                Ellipticals, stationary bikes, rowing machines, and more.
                Our Services:
                Equipment Installation, Maintenance & Repair, Consultation, Custom Solutions.
            """
        },
        {"role": "user", "content": user_input}],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    bot_response = response.choices[0].message.content

    # Google Calendar Scheduling
    if "SCHEDULE_REQUEST|" in bot_response:
        parts = bot_response.split("|")
        if len(parts) == 6:
            success = schedule_appointment(parts[1], parts[2], parts[3], parts[4], parts[5])
            if success:
                return f"Great! I've scheduled your appointment for {parts[3]} at {parts[4]}. You'll receive a confirmation email shortly."
            else:
                return "I apologize, but there was an issue scheduling your appointment. Please try again or contact us directly."

    elif any(keyword in user_input.lower() for keyword in ["schedule", "appointment", "book time", "google calendar"]):
        return '''
            Sure! You can book an appointment using our Google Calendar: 
            <br><br>
            <iframe src="https://calendar.google.com/calendar/embed?src=kanchan.g12%40gmail.com&ctz=Europe%2FLondon" 
                    style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>
            <br><br>
            Please select a time slot and confirm your booking.
        '''
    
    # Zoho CRM Inquiry Handling (for product inquiries)
    elif any(keyword in user_input.lower() for keyword in ["buy", "purchase", "pricing", "cost", "quote", "order", "product details", "sales inquiry"]):
        bot_response += "\n\nTo assist you better, please provide your **Name, Email, and Phone Number**. We'll get back to you with details."

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

def send_to_zoho_crm(name, email, phone, inquiry):
    try:
        zoho_crm_url = "https://www.zohoapis.com/crm/v2/Leads"
        headers = {
            "Authorization": f"Zoho-oauthtoken {os.environ.get('ZOHO_ACCESS_TOKEN')}",
            "Content-Type": "application/json"
        }
        payload = {
            "data": [{
                "Company": "PowerFit Equipment Co.",
                "Last_Name": name,
                "Email": email,
                "Phone": phone,
                "Lead_Source": "Chatbot",
                "Description": inquiry
            }]
        }
        response = requests.post(zoho_crm_url, headers=headers, json=payload)
        return response.status_code == 201
    except Exception as e:
        print(f"Zoho CRM Error: {e}")
        return False

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    bot_response = get_bot_response(user_message)

    # If user provides their details for Zoho CRM
    if "Name" in user_message and "Email" in user_message and "Phone" in user_message:
        details = user_message.split(",")  # Example: "John Doe, john@example.com, 1234567890"
        if len(details) == 3:
            success = send_to_zoho_crm(details[0].strip(), details[1].strip(), details[2].strip(), user_message)
            if success:
                return jsonify({'response': "Thank you! Your details have been sent to our sales team. We'll contact you shortly!"})
            else:
                return jsonify({'response': "Sorry, there was an issue sending your details. Please try again."})

    return jsonify({'response': bot_response})
@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)
