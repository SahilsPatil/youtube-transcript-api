import yt_dlp
import assemblyai as aai
from flask import Flask, jsonify, request
from threading import Thread
import time

app = Flask(__name__)

# Set your AssemblyAI API key
aai.settings.api_key = "6a608718f1c64d4daeda0cfb74510e11"

# Store the transcription results in a dictionary (use a more permanent solution for production)
transcriptions = {}

def download_audio(video_url, filename):
    print(f"Starting download for video: {video_url}")
    ydl_opts = {
        'format': 'm4a/bestaudio/best',  # The best audio version in m4a format
        'outtmpl': filename,  # The output name should be the id followed by the extension
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        },
        'proxy': 'dwuojzgn:wx0b3xey9xxm@64.137.42.112:5157',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading audio for {video_url}...")
            error_code = ydl.download([video_url])
            if error_code == 0:
                print(f"Audio download completed successfully: {filename}")
                return filename  # Return the file name if successful
            else:
                print(f"Error occurred during download: {error_code}")
    except Exception as e:
        print(f"Download error: {e}")
    return None

def transcribe_audio(filename, transcription_id):
    print(f"Starting transcription for audio file: {filename}")
    try:
        # Transcribe the audio using AssemblyAI SDK
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(filename)
        print("Transcription request sent to AssemblyAI.")
        # Wait for the transcription to complete
        while transcript.status != "completed":
            print(f"Waiting for transcription to complete. Current status: {transcript.status}")
            time.sleep(5)
            transcript = transcriber.get_transcript(transcript.id)  # Poll for the result
        print(f"Transcription completed successfully: {transcript.text}")
        transcriptions[transcription_id] = transcript.text  # Store the transcript
        return transcript.text
    except Exception as e:
        print(f"Transcription failed: {str(e)}")
        return None

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    # Set the filename for the audio file
    audio_file = f"{video_url.split('=')[-1]}.m4a"
    print(f"Received video URL: {video_url}, audio file name will be {audio_file}")

    transcription_id = f"{video_url.split('=')[-1]}"  # Create a unique transcription ID

    # Start background thread for download and transcription
    def process_transcription():
        print("Starting background process for download and transcription...")
        # Download audio
        downloaded_audio = download_audio(video_url, audio_file)
        if downloaded_audio:
            # Perform transcription
            transcript = transcribe_audio(downloaded_audio, transcription_id)
            if transcript:
                print(f"Transcript: {transcript}")
            else:
                print("Transcription failed.")
        else:
            print("Audio download failed.")

    # Start the background thread
    thread = Thread(target=process_transcription)
    thread.start()

    # Return immediately with a status message and transcription ID
    return jsonify({"message": "Transcription is being processed. Check back later for the result.", "transcription_id": transcription_id}), 202

@app.route('/get_transcript/<transcription_id>', methods=['GET'])
def get_transcript(transcription_id):
    if transcription_id not in transcriptions:
        return jsonify({"error": "Transcription not found or still in progress"}), 404
    transcript = transcriptions[transcription_id]
    return jsonify({"transcript": transcript})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)





# import yt_dlp
# import assemblyai as aai
# from flask import Flask, jsonify, request
# from threading import Thread
# from queue import Queue
# import time

# app = Flask(__name__)

# # Set your AssemblyAI API key
# aai.settings.api_key = "6a608718f1c64d4daeda0cfb74510e11"

# # Store the transcription results in a dictionary (use a more permanent solution for production)
# transcriptions = {}

# def download_audio(video_url, filename, result_queue):
#     print(f"Starting download for video: {video_url}")
#     ydl_opts = {
#         'format': 'm4a/bestaudio/best',  # The best audio version in m4a format
#         'outtmpl': filename,  # The output name should be the id followed by the extension
#         'http_headers': {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
#         },
#         'proxy': 'dwuojzgn:wx0b3xey9xxm@64.137.42.112:5157',
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             print(f"Downloading audio for {video_url}...")
#             error_code = ydl.download([video_url])
#             if error_code == 0:
#                 print(f"Audio download completed successfully: {filename}")
#                 result_queue.put((True, filename))  # Send success result to the queue
#             else:
#                 print(f"Error occurred during download: {error_code}")
#                 result_queue.put((False, "Error occurred during download."))  # Send error message to the queue
#     except Exception as e:
#         print(f"Download error: {e}")
#         result_queue.put((False, f"Download error: {str(e)}"))  # Send error message to the queue

# def transcribe_audio(filename, transcription_id):
#     print(f"Starting transcription for audio file: {filename}")
#     try:
#         # Transcribe the audio using AssemblyAI SDK
#         transcriber = aai.Transcriber()
#         transcript = transcriber.transcribe(filename)
#         print("Transcription request sent to AssemblyAI.")
#         # Wait for the transcription to complete
#         while transcript.status != "completed":
#             print(f"Waiting for transcription to complete. Current status: {transcript.status}")
#             time.sleep(5)
#             transcript = transcriber.get_transcript(transcript.id)  # Poll for the result
#         print(f"Transcription completed successfully: {transcript.text}")
#         transcriptions[transcription_id] = transcript.text  # Store the transcript
#         return transcript.text
#     except Exception as e:
#         print(f"Transcription failed: {str(e)}")
#         return None

# @app.route('/transcribe', methods=['POST'])
# def transcribe():
#     data = request.get_json()
#     video_url = data.get('video_url')

#     if not video_url:
#         return jsonify({"error": "No video URL provided"}), 400

#     # Set the filename for the audio file
#     audio_file = f"{video_url.split('=')[-1]}.m4a"
#     print(f"Received video URL: {video_url}, audio file name will be {audio_file}")

#     transcription_id = f"{video_url.split('=')[-1]}"  # Create a unique transcription ID

#     # Create a Queue to handle results from the background thread
#     result_queue = Queue()

#     # Start background thread for download and transcription
#     def process_transcription():
#         print("Starting background process for download and transcription...")

#         # Download audio
#         downloaded_audio = download_audio(video_url, audio_file, result_queue)
#         success, result = result_queue.get()  # Get result from the queue

#         if success:
#             # Perform transcription
#             transcript = transcribe_audio(result, transcription_id)
#             if transcript:
#                 print(f"Transcript: {transcript}")
#             else:
#                 print("Transcription failed.")
#         else:
#             print(f"Audio download failed: {result}")
#             # Handle the error response by sending it back to the main thread
#             result_queue.put((False, result))  # Send error to the main thread

#     # Start the background thread
#     thread = Thread(target=process_transcription)
#     thread.start()

#     # Get the result from the queue to handle it in the main thread
#     success, error_message = result_queue.get()
#     if not success:
#         return jsonify({"error": error_message}), 500

#     # Return immediately with a status message and transcription ID
#     return jsonify({"message": "Transcription is being processed. Check back later for the result.", "transcription_id": transcription_id}), 202

# @app.route('/get_transcript/<transcription_id>', methods=['GET'])
# def get_transcript(transcription_id):
#     if transcription_id not in transcriptions:
#         return jsonify({"error": "Transcription not found or still in progress"}), 404
#     transcript = transcriptions[transcription_id]
#     return jsonify({"transcript": transcript})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8080)
