mkdir -p /app/ffmpeg
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz
tar -xf /app/ffmpeg/ffmpeg-release-i686-static.tar.xz -C /app/ffmpeg
pip install -r requirements.txt
