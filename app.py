from flask import Flask, render_template, request, jsonify
#import spacy

app = Flask(__name__)
#nlp = spacy.load('en_core_web_sm')

# Basic conversation state memory
user_state = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip().lower()
    user_id = "default_user"

    # Initialize state
    if user_id not in user_state:
        user_state[user_id] = {"step": 0, "data": {}}

    step = user_state[user_id]["step"]
    data = user_state[user_id]["data"]

    # Step-based conversation flow
    if step == 0:
        reply = "Hello, could I help you book a room?"
        user_state[user_id]["step"] = 1

    elif step == 1:
        if "yes" in user_input:
            reply = "Great! What is your name?"
            user_state[user_id]["step"] = 2
            render_template("book")
        else:
            reply = "Alright, let me know if you change your mind!"
            user_state[user_id]["step"] = 0

    elif step == 2:
        data["name"] = user_input.title()
        reply = f"Nice to meet you, {data['name']}! What are your check-in and check-out dates?"
        user_state[user_id]["step"] = 3

    elif step == 3:
        data["dates"] = user_input
        reply = "How many guests will stay in the room?"
        user_state[user_id]["step"] = 4

    elif step == 4:
        data["guests"] = user_input
        reply = ("For a couple, we recommend a double room. For 3 adults, a triple room. "
                 "For families, a family room or larger suite. Which option do you prefer?")
        user_state[user_id]["step"] = 5

    elif step == 5:
        data["room_type"] = user_input
        reply = "Would you like breakfast included?"
        user_state[user_id]["step"] = 6

    elif step == 6:
        data["breakfast"] = user_input
        reply = "Would you prefer to pay now or at check-in time?"
        user_state[user_id]["step"] = 7

    elif step == 7:
        data["payment"] = user_input
        reply = ("Would you prefer a non-refundable room? "
                 "Options: 'Yes' or 'I prefer to cancel a few days in advance (+€20)'")
        user_state[user_id]["step"] = 8

    elif step == 8:
        data["refund_policy"] = user_input
        summary = (f"Here is your booking summary:\n"
                   f"👤 Name: {data['name']}\n"
                   f"📅 Dates: {data['dates']}\n"
                   f"👥 Guests: {data['guests']}\n"
                   f"🛏 Room: {data['room_type']}\n"
                   f"🥐 Breakfast: {data['breakfast']}\n"
                   f"💳 Payment: {data['payment']}\n"
                   f"🔁 Refund Policy: {data['refund_policy']}")
        reply = summary + "\nPlease confirm your booking ('I confirm' / 'Change' / 'Start over')."
        user_state[user_id]["step"] = 9

    elif step == 9:
        if "confirm" in user_input:
            reply = "✅ Thank you! Your booking is confirmed. Can I assist you with anything else?"
            user_state[user_id]["step"] = 0
        elif "change" in user_input:
            reply = "Sure, what would you like to change?"
        elif "start over" in user_input:
            user_state[user_id] = {"step": 0, "data": {}}
            reply = "Let’s start again. Hello, could I help you book a room?"
        else:
            reply = "Please type 'I confirm', 'Change', or 'Start over'."

    else:
        reply = "I’m sorry, I didn’t understand that."

    return jsonify({"response": reply})


if __name__ == "__main__":
    app.run(port=8080)