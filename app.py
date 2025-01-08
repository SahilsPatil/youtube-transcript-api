from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

# Initialize the Flask app
app = Flask(__name__)

# Define the route to fetch transcripts
@app.route('/get-transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')  # Extract video ID from query params

    # Validate input
    if not video_id:
        return jsonify({"error": "Please provide a YouTube video ID"}), 400

    try:
        # Fetch the transcript using the YouTube Transcript API
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify(transcript)  # Return transcript as JSON
    except Exception as e:
        # Handle exceptions (e.g., video without captions)
        return jsonify({"error": str(e)}), 500

# Run the app locally for testing
if __name__ == '__main__':
    app.run(debug=True)
