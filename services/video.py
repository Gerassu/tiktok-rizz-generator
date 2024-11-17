import ffmpeg
from pathlib import Path
import tempfile
import random as rd

#manage video processing using py

class VideoProcessor:
    #def init
    def __init__(self, 
                 placeholder_dir: str = "static/placeholder/videos", 
                 output_dir: str = "output/videos"):
        
        self.placeholder_dir = Path(placeholder_dir)
        self.output_dir = Path(output_dir)
   
    def getDuration(self, video_path: str) -> float:
        print(video_path)
        probe = ffmpeg.probe(video_path)
        #video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")

        return float(probe["format"]["duration"])

    def process_video(self, video_name: str, audio_data: bytes, get_random: int) -> str:

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:

                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            randomstring = rd.randint(99999,1000000)
            video_path = self.placeholder_dir / video_name
            output_path = self.output_dir / f"processed_{get_random}_{randomstring}.mp4"


            audio_probe = ffmpeg.probe(temp_audio_path)
            audio_duration = float(audio_probe["format"]["duration"])

            in_audio= ffmpeg.input(temp_audio_path)
            in_video = ffmpeg.input(str(video_path), ss=rd.randint(0,int(self.getDuration(video_path) - audio_duration)))
            filtered = ffmpeg.filter(in_video, "trim", duration=audio_duration)
            #crop = ffmpeg.crop(filtered, 380,0,400,650)

            stream = ffmpeg.concat(filtered, in_audio, v=1, a=1)
            stream = ffmpeg.output(stream, f"{output_path}")
            stream = stream.global_args('-loglevel', 'warning')
            ffmpeg.run(stream, overwrite_output=True)

            return str(output_path)

        finally:
            Path(temp_audio_path).unlink(missing_ok=True)

    def list_placeholder_videos(self) -> list[str]:
        return [f.name for f in self.placeholder_dir.glob("*.mp4")]

    def get_placeholder_count(self) -> int:
        return len([f.name for f in self.placeholder_dir.glob("*.mp4")])

    def validate_video(self, video_path: str) -> dict:

        try:

            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")

            return {
                "duration" : float(probe["format"]["duration"]),
                "width" : int(video_info["width"]),
                "height" : int(video_info["height"]),
                "codec" : video_info["codec_name"],
                "valid" : True
            }
        
        except ffmpeg.Error:
            return {"valid" : False}