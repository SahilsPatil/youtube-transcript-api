import os
import yt_dlp
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set AssemblyAI API key
ASSEMBLYAI_API_KEY = '6a608718f1c64d4daeda0cfb74510e11'

# Helper function to download YouTube audio
def download_audio(video_url):
    output_path = 'audio.mp3'
    
    ydl_opts = {
        'format': 'bestaudio/best',  # Download the best audio format
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,  # Save to 'audio.mp3'
        'ffmpeg_location': '/app/ffmpeg/ffmpeg-*/ffmpeg',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    return output_path

# Helper function to upload audio to AssemblyAI
def upload_audio(file_path):
    headers = {
        'authorization': ASSEMBLYAI_API_KEY
    }
    
    # Prepare the file for upload
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.assemblyai.com/v2/upload',
            headers=headers,
            files={'file': f}
        )
    
    if response.status_code == 200:
        return response.json()['upload_url']
    else:
        raise Exception('Failed to upload audio to AssemblyAI')

# Endpoint to download audio and start transcription
@app.route('/transcribe', methods=['POST'])
def transcribe():
    video_url = request.json.get('videoUrl')
    
    if not video_url:
        return jsonify({"error": "Video URL is required"}), 400
    
    try:
        # Step 1: Download the audio
        audio_file = download_audio(video_url)
        
        # Step 2: Upload the audio to AssemblyAI
        audio_url = upload_audio(audio_file)
        
        # Step 3: Request transcription
        transcript_response = requests.post(
            'https://api.assemblyai.com/v2/transcript',
            headers={'authorization': '6a608718f1c64d4daeda0cfb74510e11'},
            json={'audio_url': audio_url}
        )
        
        if transcript_response.status_code == 200:
            transcript_id = transcript_response.json()['id']
            return jsonify({'transcriptId': transcript_id})
        else:
            raise Exception('Failed to request transcription')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to get the transcription status
@app.route('/transcript/<transcript_id>', methods=['GET'])
def get_transcript(transcript_id):
    try:
        # Request transcription status
        response = requests.get(
            f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
            headers={'authorization': ASSEMBLYAI_API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'completed':
                return jsonify({'transcript': data['text']})
            else:
                return jsonify({'status': data['status']})
        else:
            raise Exception('Failed to fetch transcript')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
