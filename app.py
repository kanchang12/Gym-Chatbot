from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import requests
import re
from datetime import datetime

app = Flask(__name__)

# Configuration
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Zoho Forms Configuration
ZOHO_FORMS_TOKEN = os.environ.get("ZOHO_FORMS_TOKEN")
ZOHO_FORMS_BASE_URL = "https://forms.zoho.com/api/v1"
zapier_webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")

def get_bot_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4",  
        messages=[{
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
        {
            "role": "user", 
            "content": user_input
        }],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    bot_response = response.choices[0].message.content

    # If user wants to schedule an appointment
    if re.search(r"(book|schedule).*(appointment|meeting)", bot_response, re.IGNORECASE):
        calendar_button = '''
        <div>
            <p>Click the button below to schedule your appointment:</p>
            <a href="https://calendar.zoho.in/eventreqForm/zz080212302dae9116d6ef3330452c31d40e6372bdad962211f9031055bd904ab414609977519d0f1221547968c673c8219a39b780?theme=0&l=en&tz=Europe%2FLondon" target="_blank">
                <button style="padding: 10px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Schedule Appointment
                </button>
            </a>
        </div>
        '''
        return bot_response + calendar_button
    
    # If user wants to file a complaint
    complaint_match = re.search(r"(complaint|issue|problem|feedback)", bot_response, re.IGNORECASE)
    if complaint_match:
        complaint_form = '''
        <div>
            <form id="complaintFormZoho" class="complaint-form">
                <input type="text" placeholder="First Name" required id="firstName">
                <input type="text" placeholder="Last Name" required id="lastName">
                <input type="email" placeholder="Email" required id="email">
                <textarea placeholder="Your Message" required id="message"></textarea>
                <button type="submit" onclick="submitComplaintForm(event)">Submit</button>
            </form>
        </div>
        '''
        return bot_response + complaint_form
    
    return bot_response

@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        form_data = request.json
        
        # Prepare data for Zoho Forms API
        headers = {
            'Authorization': f'Zoho-oauthtoken {ZOHO_FORMS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Map your form data to Zoho Forms fields
        zoho_data = {
            'data': {
                'Name_First': form_data.get('firstName', ''),
                'Name_Last': form_data.get('lastName', ''),
                'Email': form_data.get('email', ''),
                'Message': form_data.get('message', ''),
                'Submission_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        # Send to Zoho Forms API
        response = requests.post(
            f"{ZOHO_FORMS_BASE_URL}/form/YOUR_FORM_ID/submissions",
            headers=headers,
            json=zoho_data
        )
        
        if response.status_code == 200:
            return jsonify({"success": True, "message": "Form submitted successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to submit form"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    bot_response = get_bot_response(user_message)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
