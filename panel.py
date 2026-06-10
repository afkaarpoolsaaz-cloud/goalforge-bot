from flask import Flask, render_template, request, jsonify
from coach import forge_chat
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "forge-secret-key")


@app.route("/")
def home():
    return """
    <h1>🔥 Forge AI Control Panel</h1>
    <a href="/chat">Open Chat</a>
    """


@app.route("/chat")
def chat_page():
    return render_template("chat.html")


@app.route("/ping")
def ping():
    return {"status": "ok", "service": "GoalForge"}


@app.route("/chat", methods=["POST"])
def chat_api():
    try:
        data = request.get_json(force=True)
        user_text = data.get("message", "").strip()
        user_id = data.get("user_id", 0)

        if not user_text:
            return jsonify({"reply": "⚠️ Empty message."})

        reply = forge_chat(user_text, user_id)
        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "⚠️ Server Error"})


if __name__ == "__main__":
    print("🔥 Forge Panel Running")
    app.run(host="0.0.0.0", port=5000, debug=True)
