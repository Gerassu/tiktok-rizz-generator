# Check end for possible improvements / things to add

# Manages video processing "" Generation "" using py, list of placeholder videos utilised under static/placeholder/videos

## -- IMPORTS --

# -- video manipulation

import ffmpeg

# -- os operations

from pathlib import Path
import tempfile

import random as rd

## ----


class VideoProcessor:

    def __init__(self, 
                 placeholder_dir: str = "static/placeholder/videos", 
                 output_dir: str = "output/videos"):
        

        self.placeholder_dir = Path(placeholder_dir)
        self.output_dir = Path(output_dir)
   

    # Get total video duration, used for ffmpeg operations

    def getDuration(self, video_path: str) -> float:

        #print(video_path)

        probe = ffmpeg.probe(video_path)

        #video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")

        return float(probe["format"]["duration"])

    # Processes new video using random placeholder video

    def process_video(self, video_name: str, audio_data: bytes, get_random: int, vduration: int, height: int, width: int) -> str:

        # Create temporary audio to use with ffmpeg

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:

                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name


            # Why use UIDS when you can just print a big random number

            randomstring = rd.randint(99999,1000000)


            video_path = self.placeholder_dir / video_name
            output_path = self.output_dir / f"processed_{get_random}_{randomstring}.mp4"

            # ffmpeg operations, consider adding cropping and custom duration given by user 

            audio_probe = ffmpeg.probe(temp_audio_path)
            audio_duration = float(audio_probe["format"]["duration"])

            in_audio= ffmpeg.input(temp_audio_path)

            if(vduration > 0): 

                in_video = ffmpeg.input(str(video_path), ss=rd.randint(0,int(self.getDuration(video_path) - vduration)))
                filtered = ffmpeg.filter(in_video, "trim", duration=vduration)

            else: 
                
                in_video = ffmpeg.input(str(video_path), ss=rd.randint(0,int(self.getDuration(video_path) - audio_duration)))
                filtered = ffmpeg.filter(in_video, "trim", duration=audio_duration)

            org_probe = ffmpeg.probe(video_path)
            org_width = org_probe['streams'][0]['width']
            org_height = org_probe['streams'][0]['height']

            x_offset = (org_width - width) // 2
            y_offset = (org_height - height) // 2

            if width > org_width or height > org_height:

                raise ValueError("Given Dimension cannot be larger than the original video dimensions")
            
            crop = ffmpeg.crop(filtered, x_offset, y_offset, width, height)

            stream = ffmpeg.concat(crop, in_audio, v=1, a=1)
            stream = ffmpeg.output(stream, f"{output_path}")
            stream = stream.global_args('-loglevel', 'warning')

            ffmpeg.run(stream, overwrite_output=True)

            return str(output_path)

        finally:

            Path(temp_audio_path).unlink(missing_ok=True)


    # Get placeholder videos

    def list_placeholder_videos(self) -> list[str]:

        return [f.name for f in self.placeholder_dir.glob("*.mp4")]


    # Get video count

    def get_placeholder_count(self) -> int:

        return len([f.name for f in self.placeholder_dir.glob("*.mp4")])


    # Not used, useful to check if video is valid / too lengthy

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
        
        
####################################################################################
#
# Add length, width, height control for video generation
#
# Cleanup output/videos when needed
#
# Consider Audio operations, maybe the placeholder videos audio should not be muted 
#             (decode --> weighted addition to signal --> encode) ???
# 
# Add Overlay using multiple videos, useful when managing Subtitles Utility
#
####################################################################################