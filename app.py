import os
import yt_dlp
import requests
from flask import Flask, jsonify, request
from time import sleep

app = Flask(__name__)

# Set your AssemblyAI API key here
ASSEMBLYAI_API_KEY = '6a608718f1c64d4daeda0cfb74510e11'

def download_audio(video_url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',  # The best audio version in m4a format
        'outtmpl': '%(id)s.%(ext)s',  # The output name should be the id followed by the extension
        'proxy': 'dwuojzgn:wx0b3xey9xxm@173.0.9.70:5653',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        },
        
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([video_url])
        if error_code != 0:
            return None
    return f"{video_url.split('=')[-1]}.m4a"  # Returns the file name of the downloaded audio

def upload_audio(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                'https://api.assemblyai.com/v2/upload',
                headers={'authorization': ASSEMBLYAI_API_KEY},
                files={'file': f}
            )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def request_transcription(audio_url):
    try:
        response = requests.post(
            'https://api.assemblyai.com/v2/transcript',
            headers={'authorization': ASSEMBLYAI_API_KEY},
            json={'audio_url': audio_url}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_transcription_status(transcript_id):
    try:
        response = requests.get(
            f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
            headers={'authorization': ASSEMBLYAI_API_KEY}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()

    video_url = data.get('video_url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    # Download audio from the video
    audio_path = download_audio(video_url)
    if not audio_path:
        return jsonify({"error": "Failed to download audio"}), 500

    # Upload the audio file to AssemblyAI
    upload_response = upload_audio(audio_path)
    if "error" in upload_response:
        return jsonify({"error": upload_response["error"]}), 500

    # Request transcription from AssemblyAI
    transcript_response = request_transcription(upload_response['upload_url'])
    if "error" in transcript_response:
        return jsonify({"error": transcript_response["error"]}), 500

    transcript_id = transcript_response['id']

    # Poll for transcription status
    while True:
        status_response = get_transcription_status(transcript_id)
        if "error" in status_response:
            return jsonify({"error": status_response["error"]}), 500
        if status_response['status'] == 'completed':
            return jsonify({"transcript": status_response['text']})
        elif status_response['status'] == 'failed':
            return jsonify({"error": "Transcription failed"}), 500
        sleep(10)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
