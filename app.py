from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import sqlite3
from dotenv import load_dotenv
import os


# Load Environment Variables
load_dotenv()

API_KEY = os.getenv("API_KEY")


app = Flask(__name__)


# ================= GEMINI CONFIG =================

genai.configure(
    api_key=API_KEY
)


model = genai.GenerativeModel(
    "gemini-2.5-flash"
)



# ================= DATABASE =================


def get_db():

    return sqlite3.connect(
        "chat.db"
    )



def init_db():

    with get_db() as conn:

        conn.execute("""

        CREATE TABLE IF NOT EXISTS chats(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_message TEXT,

            bot_reply TEXT

        )

        """)

        conn.commit()



init_db()



# ================= HOME =================


@app.route("/")
def home():

    return render_template(
        "index.html"
    )



# ================= CHAT =================


@app.route(
    "/chat",
    methods=["POST"]
)

def chat():

    try:

        data = request.get_json()


        user_message = data.get(
            "message",
            ""
        )


        if user_message == "":

            return jsonify({

                "reply":
                "Please enter a message."

            })



        prompt = f"""

You are a helpful AI assistant.

Rules:

1. Detect user language automatically.

2. If user writes English,
reply only in English.

3. If user writes Gujarati,
reply only in Gujarati.

4. Do not mix languages.

User message:

{user_message}

"""


        response = model.generate_content(
            prompt
        )


        ai_reply = response.text



        # Save Chat

        with get_db() as conn:

            conn.execute(

            """

            INSERT INTO chats

            (user_message, bot_reply)

            VALUES (?,?)

            """,

            (

            user_message,

            ai_reply

            )

            )

            conn.commit()



        return jsonify({

            "reply":
            ai_reply

        })



    except Exception as e:


        return jsonify({

            "reply":
            "Error: " + str(e)

        })




# ================= HISTORY =================


@app.route("/history")
def history():


    with get_db() as conn:


        chats = conn.execute(

        """

        SELECT id, user_message

        FROM chats

        ORDER BY id DESC

        LIMIT 20

        """

        ).fetchall()



    return jsonify(
        chats
    )




# ================= OPEN OLD CHAT =================


@app.route(
    "/chat/<int:id>"
)

def open_chat(id):


    with get_db() as conn:


        chat = conn.execute(

        """

        SELECT user_message, bot_reply

        FROM chats

        WHERE id=?

        """,

        (id,)

        ).fetchone()



    return jsonify(
        chat
    )




# ================= CLEAR HISTORY =================


@app.route(
    "/clear",
    methods=["POST"]
)

def clear_history():


    with get_db() as conn:


        conn.execute(

            "DELETE FROM chats"

        )


        conn.commit()



    return jsonify({

        "status":
        "success"

    })




# ================= RUN =================


if __name__ == "__main__":


    app.run(

        debug=True

    )