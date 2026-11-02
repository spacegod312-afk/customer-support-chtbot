from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Customer Support</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f4f8;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            margin: 20px auto;
            background: white;
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0 3px 12px #ccd3dc;
        }
        h1 { color: #174ea6; }
        #chat {
            height: 350px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        .message {
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            overflow-wrap: anywhere;
        }
        .user { background: #dbeafe; text-align: right; }
        .bot { background: #dcfce7; }
        form { display: flex; gap: 8px; }
        input {
            flex: 1;
            min-width: 0;
            padding: 12px;
            border: 1px solid #bbb;
            border-radius: 8px;
        }
        button {
            padding: 12px;
            background: #174ea6;
            color: white;
            border: 0;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Customer Support</h1>
        <p>Welcome! How can we help you today?</p>
        <div id="chat" aria-live="polite">
            <div class="message bot">
                <b>Assistant:</b> Hello! Ask me about delivery, damaged items, or power problems.
            </div>
        </div>
        <form id="form">
            <input id="question" placeholder="Type your question..." required>
            <button type="submit">Send</button>
        </form>
    </div>
    <script>
        const form = document.getElementById("form");
        const input = document.getElementById("question");
        const chat = document.getElementById("chat");

        function addMessage(who, message, type) {
            const div = document.createElement("div");
            div.className = "message " + type;
            const label = document.createElement("b");
            label.textContent = who + ": ";
            div.appendChild(label);
            div.appendChild(document.createTextNode(message));
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        form.addEventListener("submit", async function(event) {
            event.preventDefault();
            const question = input.value.trim();
            if (!question) return;
            addMessage("You", question, "user");
            input.value = "";
            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({question: question})
                });
                const data = await response.json();
                addMessage("Assistant", data.answer, "bot");
            } catch (error) {
                addMessage("Assistant", "Connection error. Please try again.", "bot");
            }
        });
    </script>
</body>
</html>
"""

def get_answer(question):
    question = question.lower()

    if "delivery" in question or "late" in question:
        return "Please check your order confirmation for delivery updates."
    elif any(word in question for word in ["damaged", "cracked", "broken"]):
        return "I'm sorry your item arrived damaged. What part is damaged? Please contact the seller about a replacement or refund."
    elif "turn on" in question or "power" in question:
        return "Check the charger and power outlet. If it still won't turn on, contact the seller."
    elif any(word in question for word in ["not arrived", "not yet arrived", "missing", "where is my order"]):
        return "I'm sorry your order hasn't arrived. Check your tracking information and contact the seller if it is overdue."
    elif "refund" in question or "replacement" in question:
        return "Please contact the seller, explain the problem, and ask about their refund or replacement policy."
    else:
        return "Thank you for your message. Could you please provide more details?"

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    if not question:
        return jsonify({"answer": "Please enter a question."}), 400
    return jsonify({"answer": get_answer(question)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
