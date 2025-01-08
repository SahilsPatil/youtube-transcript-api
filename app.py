from flask import Flask, request, jsonify
import pytube
import requests
from time import sleep

app = Flask(__name__)

ASSEMBLYAI_API_KEY = '6a608718f1c64d4daeda0cfb74510e11'
AUDIO_PATH = 'audio.mp4'

def download_audio(video_url):
    try:
        yt = pytube.YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(filename=AUDIO_PATH)
        return AUDIO_PATH
    except Exception as e:
        return str(e)

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
    if "error" in audio_path:
        return jsonify({"error": audio_path}), 500

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
