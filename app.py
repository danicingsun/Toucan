from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import json, os

app = Flask(__name__, template_folder='templates', static_folder='static')

# Initialize ChatterBot
chatbot = ChatBot(
    "ToucanHotelBot",
    logic_adapters=[
        "chatterbot.logic.BestMatch"
    ],
    database_uri="sqlite:///toucan_bot_db.sqlite3"
)

trainer = ListTrainer(chatbot)

# Load training data
training_file = os.path.join(os.path.dirname(__file__), 'training_data.json')
if os.path.exists(training_file):
    with open(training_file, 'r') as f:
        data = json.load(f)
        # train with flattened conversation lists
        for convo in data.get("conversations", []):
            try:
                trainer.train(convo)
            except Exception:
                # ignore training errors in environments without chatterbot support
                pass

# Simple rule-based helper
def rule_based_response(message):
    m = message.lower()
    if any(x in m for x in ["book a room", "book", "reserve"]):
        return "Sure! May I have your full name, please?"
    if any(x in m for x in ["check-in", "checkin", "check in", "dates", "date"]):
        return "Please tell me your check-in and check-out dates (e.g., 2025-07-01 to 2025-07-05)."
    if any(x in m for x in ["guest", "guests", "how many"]):
        return "How many guests will be staying? (e.g., 2 adults, 1 child)"
    if "breakfast" in m:
        return "We offer continental and full breakfast options. Would you like breakfast included? (Yes / No)"
    if "pay" in m or "payment" in m:
        return "Would you prefer to pay now or at check-in? (Pay now / Pay at check-in)"
    if "non-refundable" in m or "cancel" in m:
        return "Non-refundable bookings are cheaper. Do you want 'Yes' (non-refundable) or 'Flexible' (cancel for €20)?"
    if any(x in m for x in ["confirm", "i confirm"]):
        return "Thank you! Your booking is confirmed. Can I help with anything else?"
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reply', methods=['POST'])
def reply():
    payload = request.get_json(force=True)
    message = payload.get('message', '')
    # Try rule-based first
    rb = rule_based_response(message)
    if rb:
        return jsonify({'reply': rb})
    # Fallback to ChatterBot
    try:
        bot_reply = str(chatbot.get_response(message))
        return jsonify({'reply': bot_reply})
    except Exception as e:
        # If ChatterBot not available or fails, safe fallback
        return jsonify({'reply': "Sorry, I couldn't process that. Can you rephrase?"})

if __name__ == '__main__':
    app.run()
