from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import video
import random as rd
from pathlib import Path
import shutil
import uuid
import os
import glob
import base64


app = FastAPI()

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.1.33"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for file storage if they don't exist

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output/videos")
STATIC_DIR = "static"
VIDEOS_DIR = "static/placeholder/videos"
TEMP_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class VideoProcessor:

    def __init__(self, video_length: int, video_width: int, video_height: int):
        self.video_length = video_length
        self.video_width = video_width
        self.video_height = video_height
        self.session_id = str(uuid.uuid4())
        self.session_dir = UPLOAD_DIR / self.session_id
        self.session_dir.mkdir(exist_ok=True)

    async def save_file(self, file: UploadFile, file_type: str) -> Path:
        """Save uploaded file to session directory"""
        if not file:
            return None
        
        file_path = self.session_dir / f"{file_type}{Path(file.filename).suffix}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path

    def generate_video(self, subtitle_path: Path = None, audio_path: Path = None) -> str:
        vprocessor = video.VideoProcessor()
        print(audio_path)
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        video_number = rd.randint(1, 4)

        print(f"{VIDEOS_DIR}/placeholder_{video_number}.mp4")

        output_path = vprocessor.process_video(f"placeholder_{video_number}.mp4", audio_data, video_number)
        print(f"processed video saved to {output_path}")

        """return f"/output/videos/{output_path}"""  
        print(f"{output_path}")

        try:
            with open(f"{output_path}", "rb") as video_file:
                video_content = video_file.read()
                video_base64 = base64.b64encode(video_content).decode("utf-8")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"error reading video file: {str(e)}",
            )
        
        return{
            "file_path" : f"{output_path}",
            "content" : video_base64,
        }

    def cleanup(self):
        """Clean up temporary files"""
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)

@app.post("/api/generate-video")
async def generate_video(
    videoLength: int = Form(...),
    videoWidth: int = Form(...),
    videoHeight: int = Form(...),
    subtitle: UploadFile = File(None),
    audio: UploadFile = File(None)
):
    try:
        # Input validation
        if videoLength <= 0 or videoWidth <= 0 or videoHeight <= 0:
            raise HTTPException(status_code=400, detail="Invalid dimensions or length")

        # Initialize video processor
        processor = VideoProcessor(videoLength, videoWidth, videoHeight)

        try:
            # Save uploaded files
            subtitle_path = await processor.save_file(subtitle, "subtitle") if subtitle else None
            audio_path = await processor.save_file(audio, "audio") if audio else None

            # Generate video
            video_data = processor.generate_video(subtitle_path, audio_path)

            return JSONResponse({
                "status": "success",
                "video_data": {
                    "path" :  video_data["file_path"],
                    "content" : video_data["content"],
                },
                "message": "Video generated successfully",
            })

        finally:
            # Clean up temporary files
            processor.cleanup()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to serve generated videos
@app.get("/api/videos/{video_name}")
async def get_video(video_name: str):
    video_path = OUTPUT_DIR / video_name
    print(video_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    try:
        with open(video_path, "rb") as video_file:
            video_content = video_file.read()
            video_base64 = base64.b64encode(video_content).decode("utf-8")

            return JSONResponse({
                "status" : "success",
                "video" : {
                    "path" : str(video_path),
                    "content" : video_base64,
                    "filename" : video_name
                }
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return video_path

# Optional: Endpoint to check server status
@app.get("/api/health")
async def health_check():
    """Check if the service is running and can access the video directory"""
    try:
        # Verify the videos directory exists and is accessible
        if not os.path.exists(VIDEOS_DIR):
            return {
                "status": "warning",
                "message": f"Videos directory not found at {VIDEOS_DIR}"
            }
        
        # Count available processed videos
        video_count = sum(1 for _ in glob.glob(f"{VIDEOS_DIR}/*[1-5].*"))
        
        return {
            "status": "healthy",
            "videosAvailable": video_count,
            "videosDirectory": str(VIDEOS_DIR)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Utility endpoint to list available videos
@app.get("/api/videos/list")
async def list_videos():
    """List all available processed videos"""
    try:
        for f in glob.glob(f"{VIDEOS_DIR}/*[1-5].*"):
            return {
                "videos": f,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7231)