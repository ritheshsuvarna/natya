# Implementation Guide
## Bharatanatyam AI Story Generator - Step-by-Step

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)
8. [Future Enhancements](#future-enhancements)

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Python**: 3.11+
- **Node.js**: 18+
- **MongoDB**: 4.4+
- **RAM**: Minimum 4GB (8GB recommended for video processing)
- **Storage**: 10GB+ free space

### Required Accounts
- Emergent LLM Key (provided) for OpenAI GPT-5.2 access
- MongoDB instance (local or cloud)

---

## Installation & Setup

### 1. Backend Setup

#### Install Python Dependencies

```bash
cd /app/backend

# Install core dependencies
pip install fastapi==0.110.1 uvicorn==0.25.0
pip install motor==3.3.1  # MongoDB async driver
pip install python-dotenv==1.2.1
pip install python-multipart  # For file uploads

# Install computer vision libraries
pip install opencv-python-headless==4.13.0
pip install mediapipe==0.10.14
pip install pillow

# Install Emergent integrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Save requirements
pip freeze > requirements.txt
```

#### Configure Environment Variables

Create `/app/backend/.env`:

```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="bharatanatyam_db"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=sk-emergent-dDd08F339A1F29f770
```

**Important**: Never hardcode URLs, ports, or credentials in code. Always use environment variables.

---

### 2. Frontend Setup

#### Install Node Dependencies

```bash
cd /app/frontend

# Install core dependencies (already in package.json)
yarn install

# Install additional required packages
yarn add framer-motion
yarn add axios
yarn add sonner  # Toast notifications
yarn add lucide-react  # Icons
```

#### Configure Environment Variables

Create `/app/frontend/.env`:

```bash
REACT_APP_BACKEND_URL=https://dance2story.preview.emergentagent.com
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

**Critical**: 
- Frontend MUST use `REACT_APP_BACKEND_URL` for all API calls
- Backend endpoints MUST have `/api` prefix for Kubernetes ingress routing
- Never hardcode URLs or ports

---

## Backend Implementation

### Architecture Overview

```
Backend (FastAPI)
├── server.py (Main application)
├── Computer Vision Module
│   ├── MediaPipe Pose
│   ├── MediaPipe Hands
│   └── MediaPipe Face Mesh
├── Classification Logic
│   ├── classify_mudra()
│   ├── classify_emotion()
│   └── analyze_video_frames()
├── Story Generation
│   └── generate_story_from_analysis()
└── API Endpoints
    ├── POST /api/upload-video
    ├── POST /api/generate-story
    ├── GET /api/analysis/{video_id}
    └── GET /api/analyses
```

### Key Components

#### 1. Video Processing Pipeline

**File: `/app/backend/server.py`**

```python
import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh

def analyze_video_frames(video_path: str, max_frames: int = 50):
    """
    Process video and extract pose, gesture, and expression data
    
    Args:
        video_path: Path to video file
        max_frames: Maximum frames to analyze (for performance)
    
    Returns:
        Dict with analysis results
    """
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Sample frames evenly across video
    frame_indices = np.linspace(0, total_frames - 1, 
                                min(max_frames, total_frames), 
                                dtype=int)
    
    analysis_results = {
        "total_frames": total_frames,
        "fps": fps,
        "duration_seconds": total_frames / fps if fps > 0 else 0,
        "scenes": []
    }
    
    # Process each frame with MediaPipe
    with mp_pose.Pose() as pose, \
         mp_hands.Hands() as hands, \
         mp_face_mesh.FaceMesh() as face_mesh:
        
        for frame_num in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Convert BGR to RGB (MediaPipe requirement)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run detections
            pose_results = pose.process(frame_rgb)
            hand_results = hands.process(frame_rgb)
            face_results = face_mesh.process(frame_rgb)
            
            # Extract and classify
            scene = extract_scene_data(
                frame_num, fps, 
                pose_results, hand_results, face_results
            )
            analysis_results["scenes"].append(scene)
    
    cap.release()
    return analysis_results
```

#### 2. Mudra Classification

```python
def classify_mudra(hand_landmarks):
    """
    Rule-based mudra classification
    
    In production: Replace with trained ML model
    """
    if not hand_landmarks:
        return "Unknown"
    
    # Extract landmark positions
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    
    # Calculate distances and angles
    thumb_index_dist = np.sqrt(
        (thumb_tip.x - index_tip.x)**2 + 
        (thumb_tip.y - index_tip.y)**2
    )
    
    # Classification rules
    if thumb_index_dist < 0.05:
        return "Anjali (Prayer)"
    elif middle_tip.y < ring_tip.y:
        return "Pataka (Flag)"
    # ... more rules
    else:
        return "Alapadma (Blooming Lotus)"
```

#### 3. Story Generation with GPT-5.2

```python
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os

async def generate_story_from_analysis(analysis_data: Dict[str, Any]) -> str:
    """
    Generate natural language story using OpenAI GPT-5.2
    """
    # Format analysis data for prompt
    scenes_text = "\n".join([
        f"Scene {i+1} (at {scene['timestamp_seconds']}s): "
        f"Action: {scene['action']}, Mudra: {scene['mudra']}, "
        f"Emotion: {scene['emotion']}"
        for i, scene in enumerate(analysis_data["scenes"][:20])
    ])
    
    prompt = f"""You are an expert in Bharatanatyam. 
    Based on this dance analysis, create a beautiful story:
    
    {scenes_text}
    
    Generate a 3-4 paragraph narrative that:
    1. Explains the story being told
    2. Interprets the emotional journey
    3. Describes mudra significance
    4. Makes it understandable for beginners
    5. Maintains cultural sensitivity
    """
    
    # Use Emergent LLM key
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    chat = LlmChat(
        api_key=api_key,
        session_id=str(uuid.uuid4()),
        system_message="You are an expert storyteller for Indian classical dance."
    )
    chat.with_model("openai", "gpt-5.2")
    
    user_message = UserMessage(text=prompt)
    response = await chat.send_message(user_message)
    
    return response
```

#### 4. API Endpoints

```python
@api_router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload and analyze video
    """
    # Validate file type
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Must be video")
    
    # Save temporarily
    video_id = str(uuid.uuid4())
    video_path = f"/tmp/{video_id}_{file.filename}"
    
    with open(video_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Analyze
    analysis_data = analyze_video_frames(video_path)
    
    # Store in MongoDB
    video_analysis = VideoAnalysis(
        id=video_id,
        video_filename=file.filename,
        analysis_data=analysis_data,
        status="analyzed"
    )
    
    doc = video_analysis.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.video_analyses.insert_one(doc)
    
    # Clean up
    os.remove(video_path)
    
    return {"video_id": video_id, "analysis": analysis_data}

@api_router.post("/generate-story")
async def generate_story(request: StoryGenerationRequest):
    """
    Generate story from analysis
    """
    analysis_doc = await db.video_analyses.find_one(
        {"id": request.analysis_id}, {"_id": 0}
    )
    
    if not analysis_doc:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Generate story
    story = await generate_story_from_analysis(
        analysis_doc['analysis_data']
    )
    
    # Update database
    await db.video_analyses.update_one(
        {"id": request.analysis_id},
        {"$set": {"generated_story": story}}
    )
    
    return {"story": story, "analysis_id": request.analysis_id}
```

---

## Frontend Implementation

### Architecture Overview

```
Frontend (React)
├── App.js (Router)
├── pages/
│   ├── LandingPage.js
│   └── Dashboard.js
├── components/ui/ (shadcn/ui)
├── App.css (Global styles)
└── index.css (Tailwind base)
```

### Key Components

#### 1. Dashboard with Video Upload

**File: `/app/frontend/src/pages/Dashboard.js`**

```javascript
import { useState, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [story, setStory] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  const handleUploadAndAnalyze = async () => {
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    setUploading(true);
    
    try {
      const response = await axios.post(
        `${API}/upload-video`, 
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (e) => {
            const progress = Math.round((e.loaded * 100) / e.total);
            setUploadProgress(progress);
          }
        }
      );
      
      setAnalysis(response.data);
      await handleGenerateStory(response.data.video_id);
    } catch (error) {
      toast.error("Analysis failed");
    } finally {
      setUploading(false);
    }
  };
  
  // ... rest of component
};
```

#### 2. Design System Integration

**File: `/app/frontend/tailwind.config.js`**

```javascript
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Playfair Display', 'serif'],
        body: ['Manrope', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        background: '#050505',
        foreground: '#FAFAFA',
        primary: '#D9381E',  // Temple Red
        secondary: '#C5A059', // Antique Gold
        accent: '#06B6D4',    // Electric Cyan
        // ... more colors
      },
    },
  },
};
```

---

## Testing

### Backend Testing

```bash
# Test API health
curl https://dance2story.preview.emergentagent.com/api/

# Test video upload (use actual video file)
curl -X POST https://dance2story.preview.emergentagent.com/api/upload-video \
  -F "file=@/path/to/dance_video.mp4" \
  -H "Content-Type: multipart/form-data"
```

### Frontend Testing

1. Open browser: `https://dance2story.preview.emergentagent.com`
2. Click "Get Started" or "Start Analyzing"
3. Upload a Bharatanatyam video (MP4, MOV)
4. Wait for analysis (2-5 seconds)
5. Story should auto-generate (5-10 seconds)
6. Verify timeline shows scenes
7. Test download button

---

## Deployment

### Supervisor Configuration

The app runs in Kubernetes with Supervisor managing processes:

```bash
# Check status
sudo supervisorctl status

# Restart backend (after .env changes or new dependencies)
sudo supervisorctl restart backend

# Restart frontend (after package.json changes)
sudo supervisorctl restart frontend

# View logs
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log
```

**Important**: 
- DO NOT restart after regular code changes (hot reload handles it)
- ONLY restart after .env or dependency changes

---

## Troubleshooting

### Common Issues

#### 1. Backend not starting

```bash
# Check logs
tail -n 50 /var/log/supervisor/backend.err.log

# Common causes:
# - Missing dependency
# - Syntax error in server.py
# - MongoDB connection failed
# - Port already in use

# Solution:
pip install <missing-package>
sudo supervisorctl restart backend
```

#### 2. Video upload fails

- **Issue**: 413 Request Entity Too Large
- **Solution**: Compress video or increase nginx max body size

- **Issue**: Unsupported video format
- **Solution**: Convert to MP4 using ffmpeg

#### 3. Story generation fails

- **Issue**: Emergent LLM Key expired or out of credits
- **Solution**: User needs to top up balance in Emergent profile

- **Issue**: OpenAI API timeout
- **Solution**: Retry with exponential backoff

#### 4. MediaPipe errors

- **Issue**: "No module named 'mediapipe'"
- **Solution**: `pip install mediapipe` and restart backend

- **Issue**: Video frames not detected
- **Solution**: Check video quality, lighting, and dancer visibility

---

## Future Enhancements

### Phase 1 (Current MVP)
- ✅ Video upload and analysis
- ✅ Pose, hand, face detection
- ✅ Rule-based mudra classification
- ✅ GPT-5.2 story generation
- ✅ Beautiful UI with cultural design

### Phase 2 (Next 3 months)
- [ ] Train custom mudra classifier (CNN + LSTM)
- [ ] Improve emotion recognition accuracy
- [ ] Add audio processing (rhythm/music analysis)
- [ ] Real-time webcam analysis
- [ ] Multi-language support

### Phase 3 (6-12 months)
- [ ] Full dataset collection (1000+ videos)
- [ ] End-to-end action recognition model
- [ ] Character and narrative recognition
- [ ] Mobile app (React Native)
- [ ] API for third-party integrations

---

## Performance Optimization Tips

1. **Frame Sampling**: Reduce `max_frames` for faster processing
2. **GPU Acceleration**: Use CUDA-enabled OpenCV for 3x speedup
3. **Caching**: Cache analysis results in Redis
4. **Async Processing**: Use Celery for background video processing
5. **CDN**: Serve frontend assets via CDN

---

## Support & Resources

- **MediaPipe Documentation**: https://google.github.io/mediapipe/
- **OpenAI API**: https://platform.openai.com/docs/
- **Emergent Integrations**: https://emergent.sh/docs/
- **Bharatanatyam Reference**: https://en.wikipedia.org/wiki/Bharatanatyam

---

## Conclusion

This implementation guide provides a complete walkthrough of building the Bharatanatyam AI Story Generator. The system is now live and functional, with clear paths for future improvements through dataset development and model training.

Key takeaways:
- Start with pre-trained models (MediaPipe)
- Use rule-based logic for MVP
- Gradually improve with custom datasets
- Maintain cultural authenticity throughout
- Iterate based on user feedback