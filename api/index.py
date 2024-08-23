from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the environment variable
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/generate_title', methods=['POST', 'GET'])
def generate_title():
    # Get the video title from the request JSON body
    content_type = request.content_type

    # Get the video title based on content type
    if content_type == 'application/json':
        # Handle raw JSON input
        data = request.json
        video_title = data.get('video_title', '')
    elif content_type == 'application/x-www-form-urlencoded':
        # Handle x-www-form-urlencoded input
        video_title = request.form.get('video_title', '')
    else:
        return jsonify({'error': 'Unsupported content type'}), 415

    # Ensure a title is provided
    if not video_title:
        return jsonify({'error': 'Video title is required'}), 400

    # Create Groq client
    client = Groq(api_key=GROQ_API_KEY)

    # Generate the completion
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "You are a YouTube video title generator. Generate a video title for this video: "
                        f"{video_title}. Generate only a title, do not generate a description or tags or anything else. "
                        "If something inappropriate is entered, respond accordingly."
                    )
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Collect response from the streaming completion
        title = ''.join(chunk.choices[0].delta.content or "" for chunk in completion)

        return jsonify({'title': title})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
