import os
import yt_dlp
import requests
from flask import Flask, request, jsonify
from time import sleep

# Initialize Flask app
app = Flask(__name__)

# AssemblyAI API Key
ASSEMBLYAI_API_KEY = '6a608718f1c64d4daeda0cfb74510e11'

# Path where audio will be saved temporarily
AUDIO_PATH = 'audio.mp3'

# Function to download the audio from YouTube
def download_audio(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': AUDIO_PATH,
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': '/tmp/ffmpeg/ffmpeg-*/ffmpeg',  # Assuming ffmpeg is placed here
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return AUDIO_PATH

# Function to upload audio to AssemblyAI
def upload_audio(file_path):
    # Open the file and send it to AssemblyAI for upload
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.assemblyai.com/v2/upload',
            headers={'authorization': ASSEMBLYAI_API_KEY},
            files={'file': f}
        )
    return response.json()

# Function to get transcription status
def get_transcription_status(transcript_id):
    response = requests.get(
        f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
        headers={'authorization': ASSEMBLYAI_API_KEY}
    )
    return response.json()

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()

    # Get YouTube video URL
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    # Download audio from the video
    audio_path = download_audio(video_url)
    
    # Upload audio to AssemblyAI
    upload_response = upload_audio(audio_path)
    
    if 'upload_url' not in upload_response:
        return jsonify({"error": "Failed to upload audio to AssemblyAI"}), 500

    # Request transcription
    transcript_response = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        headers={'authorization': ASSEMBLYAI_API_KEY},
        json={'audio_url': upload_response['upload_url']}
    )

    if 'id' not in transcript_response.json():
        return jsonify({"error": "Failed to request transcription"}), 500

    transcript_id = transcript_response.json()['id']

    # Poll for transcription status
    while True:
        status_response = get_transcription_status(transcript_id)
        if status_response['status'] == 'completed':
            return jsonify({
                "transcript": status_response['text']
            })
        elif status_response['status'] == 'failed':
            return jsonify({"error": "Transcription failed"}), 500
        sleep(10)  # Wait before checking again

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
