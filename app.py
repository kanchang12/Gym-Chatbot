from flask import Flask, render_template, request, jsonify, redirect
from openai import OpenAI
import os
import requests

app = Flask(__name__)

# Replace with your actual OpenAI API key
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

zapier_webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")

# Zoho CRM OAuth details
ZOHO_CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET")
ZOHO_REDIRECT_URI = os.environ.get("ZOHO_REDIRECT_URI")

# Function to get the bot response from OpenAI
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
    return bot_response

# Function to send data to Zoho CRM (e.g., for complaints or order inquiries)
def send_to_zoho_crm(name, email, phone, complaint):
    try:
        zoho_crm_url = "https://www.zohoapis.com/crm/v2/Leads"
        access_token = os.environ.get("ZOHO_ACCESS_TOKEN")  # Ensure the access token is available
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "data": [{
                "Company": "PowerFit Equipment Co.",
                "Last_Name": name,
                "Email": email,
                "Phone": phone,
                "Lead_Source": "Chatbot",
                "Description": complaint
            }]
        }
        response = requests.post(zoho_crm_url, headers=headers, json=payload)
        return response.status_code == 201
    except Exception as e:
        print(f"Zoho CRM Error: {e}")
        return False

# Route to handle user messages
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    bot_response = get_bot_response(user_message)

    # If the user is talking about booking
    if "book" in user_message.lower() or "schedule" in user_message.lower() or "appointment" in user_message.lower():
        return jsonify({
            'response': """
                To book an appointment, please use the calendar below:
                <iframe src="https://calendar.google.com/calendar/embed?src=kanchan.g12%40gmail.com&ctz=Europe%2FLondon" style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>
            """
        })

    # If the user talks about complaints or order-related issues
    if "complaint" in user_message.lower() or "order" in user_message.lower():
        # Check if the user provided their details for Zoho CRM
        if "Name" in user_message and "Email" in user_message and "Phone" in user_message:
            details = user_message.split(",")  # Example: "John Doe, john@example.com, 1234567890"
            if len(details) == 3:
                success = send_to_zoho_crm(details[0].strip(), details[1].strip(), details[2].strip(), user_message)
                if success:
                    return jsonify({'response': "Thank you! Your complaint has been sent to our customer service team. We'll contact you shortly!"})
                else:
                    return jsonify({'response': "Sorry, there was an issue sending your complaint. Please try again."})
        else:
            return jsonify({'response': "Please provide your name, email, and phone number for us to proceed with your complaint."})

    return jsonify({'response': bot_response})

# Route to redirect user to Zoho OAuth authorization page
@app.route('/zoho_oauth_redirect')
def zoho_oauth_redirect():
    zoho_oauth_url = f"https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.leads.CREATE&client_id={ZOHO_CLIENT_ID}&response_type=code&access_type=offline&redirect_uri={ZOHO_REDIRECT_URI}"
    return redirect(zoho_oauth_url)

# Route to handle Zoho OAuth callback
@app.route('/auth/zoho/callback')
def zoho_callback():
    code = request.args.get('code')  # Get the authorization code
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    token_data = {
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": ZOHO_REDIRECT_URI,
        "code": code
    }

    # Make a request to get the access token
    response = requests.post(token_url, data=token_data)

    if response.status_code == 200:
        access_token = response.json()['access_token']
        refresh_token = response.json()['refresh_token']

        # Save access_token and refresh_token securely
        # Example: save to a database or secure storage
        os.environ['ZOHO_ACCESS_TOKEN'] = access_token
        os.environ['ZOHO_REFRESH_TOKEN'] = refresh_token

        return jsonify({"message": "OAuth Successful! You can now send data to Zoho CRM."})
    else:
        return jsonify({"error": "OAuth failed. Please try again."}), 400

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
