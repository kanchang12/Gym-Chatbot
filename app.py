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

    if "SCHEDULE_REQUEST" in bot_response:
        # Send the Google Calendar iframe for scheduling without needing to collect any user input
        calendar_iframe = '''
        <iframe src="https://calendar.google.com/calendar/embed?src=kanchan.g12%40gmail.com&ctz=Europe%2FLondon" 
        style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>
        '''
        return calendar_iframe  # Return the iframe directly

    return bot_response



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
