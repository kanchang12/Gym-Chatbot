from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)


# Replace with your actual OpenAI API key
openai_api_key = os.environ.get("API-KEY")
client = OpenAI(api_key=openai_api_key)

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
                            "text": "You are a sales assistant at a gym. The details are given below\n"
                                    "Company Name: PowerFit Equipment Co.\n\n"
                                    "Core Information:\n\n"
                                    "Founded: 1995\n"
                                    "Mission: To provide high-quality, innovative fitness equipment that helps people achieve their health and wellness goals.\n"
                                    "Values: Quality, Innovation, Integrity, and Customer Focus\n"
                                    "Products:\n\n"
                                    "Commercial Treadmills\n"
                                    "Strength Equipment\n"
                                    "Cardio Equipment\n"
                                    "Services:\n\n"
                                    "Equipment Installation\n"
                                    "Maintenance & Repair\n"
                                    "Consultation\n"
                                    "Custom Solutions\n"
                                    "Contact:\n\n"
                                    "Phone: (555) 123-4567\n"
                                    "Email: info@powerfitequipment.com\n"
                                    "Address: 123 Fitness Street, Gym City, GC 12345\n\n\n"
                                    "You will ask details from the user and interact with them in a friendly way but subtly try to push sales, "
                                    "if new customer comes, take their input, if complaints come take email name complaint etc\n"
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
    except Exception as e:
        print(f"Error interacting with OpenAI API: {e}")
        return "I'm having trouble understanding. Please try again."

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
