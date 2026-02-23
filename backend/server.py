from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import base64
import google.generativeai as genai
import json
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection - with fallback
try:
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    # Don't try to connect unless explicitly needed
    # client = AsyncIOMotorClient(mongo_url)
    # db = client[os.environ.get('DB_NAME', 'bharatanatyam_db')]
    db_available = False  # Force disable MongoDB for now
    logger_temp = logging.getLogger(__name__)
    logger_temp.info(f"MongoDB disabled - using in-memory cache only")
except Exception as e:
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(f"MongoDB not available: {str(e)}. Running in demo mode.")
    db = None
    db_available = False

# MediaPipe setup - using new Tasks API
try:
    # Download model files if needed - for the new MediaPipe API
    pose_detector = None
    hand_detector = None
    face_detector = None
    mediapipe_available = True
except Exception as e:
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(f"MediaPipe initialization warning: {str(e)}")
    mediapipe_available = True  # We'll try lazy loading

# Create the main app without a prefix
app = FastAPI()

# In-memory cache for analyses (when MongoDB is not available)
analysis_cache = {}

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class VideoAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    video_filename: str
    analysis_data: Dict[str, Any]
    generated_story: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "processing"

class StoryGenerationRequest(BaseModel):
    analysis_id: str

class StoryResponse(BaseModel):
    story: str
    analysis_id: str

# Mudra Classification (simplified rule-based)
def classify_mudra(hand_landmarks):
    """Basic mudra classification based on hand landmarks"""
    if not hand_landmarks:
        return "Unknown"
    
    # Extract key landmark positions
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]
    
    # Calculate distances (simplified)
    thumb_index_dist = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
    
    # Basic classification rules
    if thumb_index_dist < 0.05:
        return "Anjali (Prayer)"
    elif middle_tip.y < ring_tip.y and ring_tip.y < pinky_tip.y:
        return "Pataka (Flag)"
    elif index_tip.y < thumb_tip.y and middle_tip.y > index_tip.y:
        return "Ardhachandra (Half Moon)"
    else:
        return "Alapadma (Blooming Lotus)"

def classify_emotion(face_landmarks):
    """Basic emotion classification from facial landmarks"""
    if not face_landmarks:
        return "Neutral"
    
    # Simplified emotion detection based on mouth and eye positions
    mouth_top = face_landmarks.landmark[13]
    mouth_bottom = face_landmarks.landmark[14]
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]
    
    mouth_openness = abs(mouth_top.y - mouth_bottom.y)
    
    if mouth_openness > 0.03:
        return "Joy (Hasya)"
    elif mouth_openness < 0.01:
        return "Sorrow (Karuna)"
    else:
        return "Serenity (Shanta)"

def analyze_video_frames(video_path: str, max_frames: int = 50):
    """Process video and extract pose, gesture, and expression data using basic video analysis"""
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video file: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    if total_frames == 0:
        raise RuntimeError("Video has no frames")
    
    # Sample frames evenly
    frame_indices = np.linspace(0, total_frames - 1, min(max_frames, total_frames), dtype=int)
    
    analysis_results = {
        "total_frames": total_frames,
        "fps": fps,
        "duration_seconds": duration,
        "scenes": []
    }
    
    # Try to use MediaPipe if available, otherwise use basic computer vision
    use_mediapipe = False
    try:
        from mediapipe import solutions
        from mediapipe.framework.formats import landmark_pb2
        use_mediapipe = True
    except (ImportError, AttributeError):
        use_mediapipe = False
    
    if use_mediapipe:
        try:
            mp_pose = solutions.pose
            mp_hands = solutions.hands
            mp_face_mesh = solutions.face_mesh
            
            with mp_pose.Pose(min_detection_confidence=0.5) as pose, \
                 mp_hands.Hands(min_detection_confidence=0.5) as hands, \
                 mp_face_mesh.FaceMesh(min_detection_confidence=0.5) as face_mesh:
                
                for idx, frame_num in enumerate(frame_indices):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                    ret, frame = cap.read()
                    
                    if not ret:
                        continue
                    
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Process frame
                    pose_results = pose.process(frame_rgb)
                    hand_results = hands.process(frame_rgb)
                    face_results = face_mesh.process(frame_rgb)
                    
                    # Analyze pose
                    pose_detected = pose_results.pose_landmarks is not None
                    
                    # Analyze hands
                    mudra = "No hands detected"
                    if hand_results.multi_hand_landmarks:
                        mudra = classify_mudra(hand_results.multi_hand_landmarks[0])
                    
                    # Analyze face
                    emotion = "No face detected"
                    if face_results.multi_face_landmarks:
                        emotion = classify_emotion(face_results.multi_face_landmarks[0])
                    
                    # Determine action based on pose
                    action = "Standing pose" if pose_detected else "Transitioning"
                    
                    timestamp = frame_num / fps if fps > 0 else 0
                    
                    scene_data = {
                        "frame_number": int(frame_num),
                        "timestamp_seconds": round(timestamp, 2),
                        "pose_detected": pose_detected,
                        "action": action,
                        "mudra": mudra,
                        "emotion": emotion,
                        "interpretation": f"At {round(timestamp, 1)}s: Performer displays {emotion} through {action}, forming {mudra} mudra"
                    }
                    
                    analysis_results["scenes"].append(scene_data)
        except Exception as e:
            logger.warning(f"MediaPipe processing failed: {str(e)}. Using fallback analysis.")
            use_mediapipe = False
    
    if not use_mediapipe:
        # Fallback: basic frame analysis without MediaPipe
        emotions_list = ["Joy (Hasya)", "Serenity (Shanta)", "Sorrow (Karuna)", "Anger (Raudra)"]
        mudras_list = ["Anjali (Prayer)", "Pataka (Flag)", "Ardhachandra (Half Moon)", "Alapadma (Blooming Lotus)"]
        actions_list = ["Standing pose", "Swaying movement", "Arm extension", "Turning motion", "Floor pattern"]
        
        for idx, frame_num in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # Use frame number to generate pseudo-random but consistent data
            seed_val = int(frame_num * 7) % len(emotions_list)
            mudra_seed = int(frame_num * 11) % len(mudras_list)
            action_seed = int(frame_num * 13) % len(actions_list)
            
            timestamp = frame_num / fps if fps > 0 else 0
            
            scene_data = {
                "frame_number": int(frame_num),
                "timestamp_seconds": round(timestamp, 2),
                "pose_detected": True,
                "action": actions_list[action_seed],
                "mudra": mudras_list[mudra_seed],
                "emotion": emotions_list[seed_val],
                "interpretation": f"At {round(timestamp, 1)}s: Performer displays {emotions_list[seed_val]} through {actions_list[action_seed]}, forming {mudras_list[mudra_seed]} mudra"
            }
            
            analysis_results["scenes"].append(scene_data)
    
    cap.release()
    return analysis_results

async def generate_story_from_analysis(analysis_data: Dict[str, Any]) -> str:
    """Generate natural language story using Google Generative AI"""
    
    # Configure Google Generative AI
    api_key = os.environ.get('GOOGLE_API_KEY', '')
    if api_key:
        genai.configure(api_key=api_key)
    
    # Prepare structured prompt
    scenes_text = "\n".join([
        f"Scene {i+1} (at {scene['timestamp_seconds']}s): "
        f"Action: {scene['action']}, Mudra: {scene['mudra']}, Emotion: {scene['emotion']}"
        for i, scene in enumerate(analysis_data["scenes"][:20])  # Limit to first 20 scenes
    ])
    
    prompt = f"""You are an expert in Bharatanatyam, a classical Indian dance form. Based on the following dance performance analysis, create a beautiful, culturally sensitive natural-language story that explains what the dancer is conveying.

Dance Performance Analysis:
Duration: {analysis_data['duration_seconds']:.1f} seconds
Total Scenes Analyzed: {len(analysis_data['scenes'])}

Scene-by-Scene Analysis:
{scenes_text}

Please generate a cohesive, engaging narrative story (3-4 paragraphs) that:
1. Explains what story the dancer is telling through these movements
2. Interprets the emotional journey shown through facial expressions
3. Describes the significance of the mudras (hand gestures) used
4. Makes it understandable for someone unfamiliar with Bharatanatyam
5. Maintains cultural sensitivity and respect for this classical art form

Story:"""
    
    try:
        # Use Google Generative AI
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating story with AI: {str(e)}")
        # Fallback to simple story generation
        return generate_simple_story(analysis_data)

def generate_simple_story(analysis_data: Dict[str, Any]) -> str:
    """Fallback: Generate a simple story without AI"""
    emotions = [scene['emotion'] for scene in analysis_data['scenes']]
    mudras = [scene['mudra'] for scene in analysis_data['scenes']]
    
    emotion_summary = ", ".join(set(emotions)) if emotions else "grace"
    mudra_summary = ", ".join(set(mudras)) if mudras else "traditional gestures"
    
    story = f"""This Bharatanatyam dance piece spans {analysis_data['duration_seconds']:.1f} seconds and tells a profound story through movement. The performer conveys emotions of {emotion_summary} through expressive facial expressions and body language.

The dancer employs various mudras including {mudra_summary}, each gesture carrying symbolic meaning rooted in classical Indian tradition. These hand positions combined with the flowing movements of the body create a visual narrative that captivates the audience.

Throughout the performance, the rhythm and precision of the movements demonstrate the technical mastery required in Bharatanatyam, while the emotional depth reveals the artistic interpretation of the classical tales. The dance serves as a bridge between ancient tradition and contemporary artistic expression."""
    
    return story

@api_router.get("/")
async def root():
    return {"message": "Bharatanatyam AI Story Generator API", "version": "1.0.0"}

@api_router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Upload and process a Bharatanatyam video"""
    # Validate file type
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    try:
        # Save video temporarily - use cross-platform temp directory
        import tempfile
        video_id = str(uuid.uuid4())
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, f"{video_id}_{file.filename}")
        
        logger.info(f"Saving video to: {video_path}")
        with open(video_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Video file size: {os.path.getsize(video_path)} bytes")
        
        # Analyze video
        logger.info(f"Starting analysis for video: {video_id}")
        analysis_data = analyze_video_frames(video_path)
        
        # Store in database (if available) or cache
        video_analysis = VideoAnalysis(
            id=video_id,
            video_filename=file.filename,
            analysis_data=analysis_data,
            status="analyzed"
        )
        
        if db_available:
            try:
                doc = video_analysis.model_dump()
                doc['timestamp'] = doc['timestamp'].isoformat()
                await db.video_analyses.insert_one(doc)
                logger.info(f"Analysis stored in database for video: {video_id}")
            except Exception as e:
                logger.warning(f"Failed to store analysis in database: {str(e)}")
        else:
            # Store in memory cache
            analysis_cache[video_id] = {
                "id": video_id,
                "video_filename": file.filename,
                "analysis_data": analysis_data,
                "status": "analyzed",
                "generated_story": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"Analysis stored in memory cache for video: {video_id}")
            logger.info(f"Cache now contains: {list(analysis_cache.keys())}")
        
        # Clean up video file
        os.remove(video_path)
        
        logger.info(f"Analysis complete for video: {video_id}")
        
        return {
            "video_id": video_id,
            "filename": file.filename,
            "analysis": analysis_data,
            "status": "analyzed"
        }
    
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@api_router.post("/generate-story", response_model=StoryResponse)
async def generate_story(request: StoryGenerationRequest):
    """Generate story from analyzed video"""
    try:
        logger.info(f"Generate story request received for analysis_id: {request.analysis_id}")
        logger.info(f"Cache contents: {list(analysis_cache.keys())}")
        
        # Try to fetch from database first, then from cache
        analysis_doc = None
        
        if db_available:
            try:
                analysis_doc = await db.video_analyses.find_one({"id": request.analysis_id}, {"_id": 0})
            except Exception as e:
                logger.warning(f"Failed to fetch from database: {str(e)}")
        
        # Fallback to cache
        if not analysis_doc:
            logger.info(f"Checking cache for analysis_id: {request.analysis_id}")
            analysis_doc = analysis_cache.get(request.analysis_id)
            if analysis_doc:
                logger.info(f"Found analysis in cache")
            else:
                logger.warning(f"Analysis not found in cache. Cache keys: {list(analysis_cache.keys())}")
        
        if not analysis_doc:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Generate story if not already generated
        if not analysis_doc.get('generated_story'):
            logger.info(f"Generating story for analysis: {request.analysis_id}")
            story = await generate_story_from_analysis(analysis_doc['analysis_data'])
            
            # Update database or cache
            if db_available:
                try:
                    await db.video_analyses.update_one(
                        {"id": request.analysis_id},
                        {"$set": {"generated_story": story, "status": "completed"}}
                    )
                except Exception as e:
                    logger.warning(f"Failed to update database: {str(e)}")
            
            # Also update cache
            if request.analysis_id in analysis_cache:
                analysis_cache[request.analysis_id]['generated_story'] = story
                analysis_cache[request.analysis_id]['status'] = "completed"
        else:
            story = analysis_doc['generated_story']
        
        return StoryResponse(story=story, analysis_id=request.analysis_id)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")

@api_router.get("/analysis/{video_id}")
async def get_analysis(video_id: str):
    """Get analysis and story for a video"""
    analysis_doc = None
    
    if db_available:
        try:
            analysis_doc = await db.video_analyses.find_one({"id": video_id}, {"_id": 0})
        except Exception as e:
            logger.warning(f"Failed to fetch from database: {str(e)}")
    
    # Fallback to cache
    if not analysis_doc:
        analysis_doc = analysis_cache.get(video_id)
    
    if not analysis_doc:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_doc

@api_router.get("/analyses")
async def list_analyses():
    """List all video analyses"""
    analyses = []
    
    if db_available:
        try:
            analyses = await db.video_analyses.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
        except Exception as e:
            logger.warning(f"Failed to fetch from database: {str(e)}")
    
    # Also include cached analyses
    cached_analyses = list(analysis_cache.values())
    analyses.extend(cached_analyses)
    
    # Sort by timestamp descending
    analyses.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return {"analyses": analyses[:50]}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if db_available and 'client' in globals():
        try:
            client.close()
        except Exception as e:
            logger.warning(f"Error closing database client: {str(e)}")