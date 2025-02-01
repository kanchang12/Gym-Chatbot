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
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # You can choose a different model if needed
            messages=[
                {
                    "role": "system", 
                    "content": [
                        {
                            "type": "text",
                            "text": """

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
FAQs:
1. How can I join PowerFit Equipment Co.?
You don’t need to "join" us, but we welcome business partnerships and individual clients. To get started, simply reach out to our customer service team at info@powerfitequipment.com or call us at (555) 123-4567 to inquire about equipment, services, or partnerships.

2. What are your operating hours?
We’re open Monday to Friday from 8 AM to 6 PM (EST). You can reach us via phone, email, or our website during business hours. After hours, you can email us, and we’ll get back to you as soon as possible.

3. How much do your products and services cost?
Our prices vary based on the type and quantity of equipment or services requested.

For equipment, pricing depends on model, specifications, and quantity.
Installation, maintenance, and consultation services are priced individually based on the scope of the work.
To receive a detailed quote, please contact us with your specific needs.
4. Do you offer any warranties?
Yes, all our equipment comes with a 5-year warranty against defects in materials and workmanship. We also offer extended warranty options and maintenance packages for added peace of mind.

5. What if I need repairs or service on my equipment?
We offer prompt maintenance and repair services. If your equipment needs service, please contact our customer support team, and we’ll send a technician to assess and fix the issue.

6. Can you provide training for my staff on using the equipment?
Absolutely! We offer training services to ensure your team knows how to properly operate and maintain our equipment. Training can be scheduled as part of your installation or as a separate service.

7. What is the process for purchasing equipment?
You can purchase equipment directly from our website, by phone, or by email. Simply select the equipment you’re interested in, and our team will assist with the order and shipping details. If you need help choosing, feel free to contact us for a consultation.

8. Do you offer financing or leasing options?
Yes, we offer financing and leasing options for both individuals and businesses. We understand that investing in fitness equipment can be a big commitment, and we aim to make it more accessible through flexible payment plans. Contact us for more details.

9. How do I maintain my fitness equipment?
Routine maintenance is essential for extending the life of your equipment. We offer maintenance packages that include periodic checkups, cleaning, and calibration. We also provide simple maintenance tips for home users and detailed manuals for gym owners.

10. Do you offer installation for large gyms?
Yes, we specialize in large-scale installations, from fitness centers to corporate wellness programs. Our installation team is experienced in setting up entire gym layouts, ensuring equipment is positioned for maximum efficiency.

11. Do you offer customized equipment?
Yes, we offer custom fitness equipment solutions for businesses, gyms, and home users. This includes equipment that meets specific functionality needs or custom branding for gyms or corporate clients.

12. Can you help design my gym layout?
We offer expert consultation services for gym design. Our team will work with you to choose the best layout, ensuring that the space is efficient and tailored to your specific needs. This service includes equipment recommendations, space planning, and design advice.

13. What is your return policy?
We want you to be completely satisfied with your purchase. If for any reason you're not happy, you can return products within 30 days of purchase. Custom-built or special-order equipment may have different return policies, which we’ll clarify during the order process.

14. How do I contact you for support?
You can reach our support team via email at support@powerfitequipment.com or by phone at (555) 123-4567 during business hours. For urgent issues, please call for immediate assistance.

Contact Information:
Phone: (555) 123-4567
Email: info@powerfitequipment.com
Website: www.powerfitequipment.com
Mailing Address: 123 Fitness Blvd, Healthy City, HC 12345
Get In Touch:
Ready to equip your gym or home workout space? Have questions about our products or services? We’re here to help! Reach out to us via phone, email, or by visiting our website for further details.
                            
                                    "You will ask details from the user and interact with them in a friendly way but subtly try to push sales, "
                                    "if new customer comes, take their input, if complaints come take email name complaint etc\n"
                                    """
                        }
                    ]
                },
                {"role": "user", "content": user_input}
            ],
            max_tokens=150, 
            n=1,
            stop=None,
            temperature=0.7, 
        )
        return response.choices[0].message.content
    if "SCHEDULE_REQUEST|" in bot_response:
            parts = bot_response.split("|")
            if len(parts) == 6:
                success = schedule_appointment(parts[1], parts[2], parts[3], parts[4], parts[5])
                if success:
                    return f"Great! I've scheduled your appointment for {parts[3]} at {parts[4]}. You'll receive a confirmation email shortly."
                else:
                    return "I apologize, but there was an issue scheduling your appointment. Please try again or contact us directly."
            
        return bot_response
        

    except Exception as e:
        print(f"Error interacting with OpenAI API: {e}")
        return "I'm having trouble understanding. Please try again."

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
    # Extract relevant data from HTML 
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
