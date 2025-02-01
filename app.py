from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import requests
import re

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

    # Prioritize specific actions (like scheduling)
    if re.search(r"(book|schedule).*(meeting|appointment)", user_input, re.IGNORECASE):
        calendar_iframe = '''
        https://calendar.google.com/calendar/u/0?cid=a2FuY2hhbi5nMTJAZ21haWwuY29t
        '''
        return calendar_iframe

    # Handle complaints, orders, and leads *separately* and *after* specific actions.
    complaint_match = re.search(r"(complaint|issue|problem|feedback)", user_input, re.IGNORECASE)
    order_match = re.search(r"(order|buy|purchase|interested)", user_input, re.IGNORECASE)

    if complaint_match or order_match:  # Check if either a complaint OR an order is mentioned
        ticket_data = {}

        if complaint_match:
            ticket_data["complaint_details"] = user_input # Capture the whole user input as complaint
            bot_response = "Thank you for your feedback. Your complaint has been submitted."  # Update bot response
        if order_match:
            ticket_data["order_details"] = user_input # Capture the whole user input as order
            bot_response = "Thank you for your interest. Your order request has been submitted."  # Update bot response

        # Extract name and email (Improved)
        name_match = re.search(r"my name is (.*)|I am (.*)", user_input, re.IGNORECASE) # More robust name extraction
        name = name_match.group(1) if name_match else "User Name" # Default if no name found
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", user_input) #Email regex
        email = email_match.group(0) if email_match else "user@example.com" # Default if no email found

        ticket_data["name"] = name
        ticket_data["email"] = email

        create_zoho_ticket(ticket_data)  # Create Zoho ticket *after* gathering all info
        return bot_response  # Return the appropriate response

    return bot_response  # Default bot response if no special keywords are found


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    bot_response = get_bot_response(user_message)
    return jsonify({'response': bot_response})

# Load Zoho CRM API details from environment variables
ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
ZOHO_REDIRECT_URI = os.getenv('ZOHO_REDIRECT_URI')
ZOHO_ACCESS_TOKEN = ''  # Store this after fetching it

# This would be the function to request Zoho CRM access token from authorization code
def get_access_token(authorization_code):
    url = 'https://accounts.zoho.com/oauth/v2/token'
    data = {
        'client_id': ZOHO_CLIENT_ID,
        'client_secret': ZOHO_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': ZOHO_REDIRECT_URI,
        'code': authorization_code
    }
    response = requests.post(url, data=data)
    access_token = response.json().get('access_token')
    return access_token

# Endpoint to authenticate Zoho CRM (called by your frontend after login)
@app.route('/auth/zoho/callback')
def zoho_callback():
    authorization_code = request.args.get('code')
    access_token = get_access_token(authorization_code)
    # Store access token for future API calls
    global ZOHO_ACCESS_TOKEN
    ZOHO_ACCESS_TOKEN = access_token
    return "Successfully authenticated Zoho CRM!"

# Function to create a ticket in Zoho CRM (after user provides complaint/order/lead info)
def create_zoho_ticket(ticket_data):
    url = "https://www.zohoapis.com/crm/v2/Leads"  # Using Leads API for complaints/orders/leads
    headers = {
        "Authorization": f"Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"data": [ticket_data]})
    return response.json()

# Endpoint for handling complaints/orders/leads
@app.route('/create_ticket', methods=['POST'])
def create_ticket():
    # Sample ticket data coming from the user
    ticket_data = request.json  # Expecting JSON data
    response = create_zoho_ticket(ticket_data)
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
