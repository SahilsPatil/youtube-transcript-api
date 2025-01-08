import yt_dlp
import assemblyai as aai
from flask import Flask, jsonify, request

app = Flask(__name__)

# Set your AssemblyAI API key
aai.settings.api_key = "6a608718f1c64d4daeda0cfb74510e11"

def download_audio(video_url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',  # The best audio version in m4a format
        'outtmpl': '%(id)s.%(ext)s',  # The output name should be the id followed by the extension
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        },
        'proxy': 'dwuojzgn:wx0b3xey9xxm@64.137.42.112:5157',
        #'cookiefile':"cookies.txt",
       
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([video_url])
            if error_code == 0:
                return f"{video_url.split('=')[-1]}.m4a"  # Return file name
    except Exception as e:
        print(f"Download error: {e}")
    return None

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()

    video_url = data.get('video_url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    # Download audio from YouTube
    audio_file = download_audio(video_url)
    if not audio_file:
        return jsonify({"error": "Failed to download audio"}), 500

    try:
        # Transcribe the audio using AssemblyAI SDK
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file)
        return jsonify({"transcript": transcript.text})
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
