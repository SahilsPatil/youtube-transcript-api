import os
import pytube
import requests
from flask import Flask, request, jsonify
from time import sleep

app = Flask(__name__)

# AssemblyAI API Key
ASSEMBLYAI_API_KEY = "6a608718f1c64d4daeda0cfb74510e11"

# Path to save the downloaded audio temporarily
AUDIO_PATH = 'audio.mp4'

# Download audio from YouTube using Pytube
def download_audio(video_url):
    yt = pytube.YouTube(video_url)
    
    # Get the highest quality audio stream available
    audio_stream = yt.streams.filter(only_audio=True).first()
    
    # Download the audio stream
    audio_stream.download(filename=AUDIO_PATH)
    return AUDIO_PATH

# Function to upload audio to AssemblyAI
def upload_audio(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.assemblyai.com/v2/upload',
            headers={'authorization': ASSEMBLYAI_API_KEY},
            files={'file': f}
        )
    return response.json()

# Request transcription from AssemblyAI
def request_transcription(audio_url):
    response = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        headers={'authorization': ASSEMBLYAI_API_KEY},
        json={'audio_url': audio_url}
    )
    return response.json()

# Get the status of transcription
def get_transcription_status(transcript_id):
    response = requests.get(
        f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
        headers={'authorization': ASSEMBLYAI_API_KEY}
    )
    return response.json()

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()

    video_url = data.get('video_url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    # Download audio from the video
    audio_path = download_audio(video_url)
    
    # Upload the audio file to AssemblyAI
    upload_response = upload_audio(audio_path)

    if 'upload_url' not in upload_response:
        return jsonify({"error": "Failed to upload audio to AssemblyAI"}), 500

    # Request transcription from AssemblyAI
    transcript_response = request_transcription(upload_response['upload_url'])

    if 'id' not in transcript_response:
        return jsonify({"error": "Failed to request transcription"}), 500

    transcript_id = transcript_response['id']

    # Poll for transcription status
    while True:
        status_response = get_transcription_status(transcript_id)
        if status_response['status'] == 'completed':
            return jsonify({"transcript": status_response['text']})
        elif status_response['status'] == 'failed':
            return jsonify({"error": "Transcription failed"}), 500
        sleep(10)  # Wait for a while before polling again

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
6a608718f1c64d4daeda0cfb74510e11
