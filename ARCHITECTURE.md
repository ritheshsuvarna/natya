# Bharatanatyam AI Story Generator - System Architecture

## Overview
An end-to-end AI system that automatically understands and translates Bharatanatyam dance performances into meaningful natural-language stories in real time.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                         │
│  React + Tailwind CSS + Framer Motion + shadcn/ui              │
│  - Landing Page                                                 │
│  - Dashboard (Upload & Analysis Interface)                      │
│  - Story Display Panel                                          │
│  - Timeline Visualization                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                       Backend Layer (FastAPI)                   │
│                                                                 │
│  API Endpoints:                                                 │
│  ├─ POST /api/upload-video                                     │
│  ├─ POST /api/generate-story                                   │
│  ├─ GET  /api/analysis/{video_id}                              │
│  └─ GET  /api/analyses                                          │
│                                                                 │
│  Processing Pipeline:                                           │
│  ├─ Video Upload Handler                                       │
│  ├─ Frame Extraction (OpenCV)                                  │
│  ├─ Multi-Modal Analysis (MediaPipe)                           │
│  ├─ Semantic Understanding                                      │
│  └─ Story Generation (OpenAI GPT-5.2)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   Computer Vision Module                        │
│                                                                 │
│  MediaPipe Solutions:                                           │
│  ├─ Pose Detection (Full body skeletal keypoints)              │
│  ├─ Hand Landmarks (Mudra classification)                       │
│  └─ Face Mesh (Emotion detection)                              │
│                                                                 │
│  Processing:                                                    │
│  ├─ Frame sampling (max 50 frames)                             │
│  ├─ Real-time landmark extraction                              │
│  ├─ Temporal sequence analysis                                 │
│  └─ Action segmentation                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                 Semantic Understanding Layer                    │
│                                                                 │
│  Classification Logic:                                          │
│  ├─ Mudra Classification (Rule-based)                          │
│  │  └─ Maps hand landmarks to Bharatanatyam mudras             │
│  ├─ Emotion Recognition (Facial landmarks)                     │
│  │  └─ Joy, Sorrow, Serenity (Rasas)                           │
│  └─ Action Detection (Pose analysis)                            │
│     └─ Standing poses, transitions                             │
│                                                                 │
│  Output: Structured JSON with scenes                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│               NLP Story Generation Module                       │
│                                                                 │
│  Emergent LLM Integration:                                      │
│  ├─ Provider: OpenAI                                            │
│  ├─ Model: GPT-5.2                                              │
│  └─ API Key: Emergent LLM Key (Universal)                      │
│                                                                 │
│  Process:                                                       │
│  ├─ Scene-by-scene analysis formatting                         │
│  ├─ Cultural context injection                                 │
│  ├─ Prompt engineering for coherent narrative                  │
│  └─ Natural language story generation                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      Database Layer (MongoDB)                   │
│                                                                 │
│  Collections:                                                   │
│  └─ video_analyses                                              │
│     ├─ id (UUID)                                                │
│     ├─ video_filename                                           │
│     ├─ analysis_data (JSON)                                     │
│     ├─ generated_story (text)                                   │
│     ├─ status (processing/analyzed/completed)                   │
│     └─ timestamp                                                │
└─────────────────────────────────────────────────────────────────┘

## Data Flow

1. **Video Upload**
   - User uploads Bharatanatyam video via React frontend
   - File validation (video/* mime type)
   - Temporary storage in /tmp

2. **Video Analysis**
   - Frame extraction using OpenCV
   - Uniform sampling (max 50 frames across video duration)
   - Parallel processing:
     * MediaPipe Pose → Full body keypoints
     * MediaPipe Hands → Hand landmarks → Mudra classification
     * MediaPipe Face Mesh → Facial landmarks → Emotion detection

3. **Semantic Interpretation**
   - Rule-based mudra classification:
     * Anjali (Prayer)
     * Pataka (Flag)
     * Ardhachandra (Half Moon)
     * Alapadma (Blooming Lotus)
   - Emotion mapping to Rasas:
     * Hasya (Joy)
     * Karuna (Sorrow)
     * Shanta (Serenity)
   - Action identification from pose

4. **Structured Output**
   ```json
   {
     "total_frames": 1500,
     "fps": 30,
     "duration_seconds": 50.0,
     "scenes": [
       {
         "frame_number": 0,
         "timestamp_seconds": 0.0,
         "pose_detected": true,
         "action": "Standing pose",
         "mudra": "Anjali (Prayer)",
         "emotion": "Serenity (Shanta)",
         "interpretation": "At 0.0s: Performer displays..."
       }
     ]
   }
   ```

5. **Story Generation**
   - Structured data → Natural language prompt
   - GPT-5.2 generates culturally sensitive narrative
   - 3-4 paragraph cohesive story
   - Explains movements, emotions, mudras for beginners

6. **Output Delivery**
   - Real-time display in Story Script panel
   - Timeline visualization with scene cards
   - Downloadable text file

## Technology Stack

### Backend
- **Framework**: FastAPI 0.110.1
- **Computer Vision**: 
  - OpenCV (opencv-python-headless 4.13.0)
  - MediaPipe 0.10.14
- **NLP**: 
  - emergentintegrations 0.1.0
  - OpenAI GPT-5.2 via Emergent LLM Key
- **Database**: MongoDB (Motor async driver)
- **Python**: 3.11

### Frontend
- **Framework**: React 19.0.0
- **UI Library**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS 3.4.17
- **Animations**: Framer Motion 12.27.5
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Notifications**: Sonner

### Infrastructure
- **Deployment**: Kubernetes cluster
- **Process Manager**: Supervisor
- **Hot Reload**: Enabled for both frontend and backend

## Key Features

1. **Multi-Modal Analysis**
   - Simultaneous pose, hand, and face detection
   - Temporal coherence across frames

2. **Cultural Sensitivity**
   - Bharatanatyam-specific mudra recognition
   - Rasa (emotion) mapping
   - Contextual storytelling

3. **Real-Time Processing**
   - Efficient frame sampling
   - Async processing
   - Progressive results display

4. **User Experience**
   - Beautiful, culturally appropriate UI
   - Upload progress tracking
   - Scene timeline visualization
   - Downloadable narratives

## Performance Characteristics

- **Video Processing**: ~2-5 seconds for 30-second video
- **Story Generation**: ~5-10 seconds (GPT-5.2 API call)
- **Frame Sampling**: Max 50 frames (adjustable)
- **Supported Formats**: All common video formats (mp4, mov, avi, etc.)

## Future Improvements

1. **Enhanced ML Models**
   - Train custom mudra classifier on Bharatanatyam dataset
   - Fine-tune emotion recognition for Indian classical expressions
   - Implement action recognition model (LSTM/Transformer)

2. **Advanced Features**
   - Real-time webcam analysis
   - Multi-dancer tracking
   - Audio-visual fusion (music/rhythm integration)
   - Costume and jewelry recognition

3. **Dataset Development**
   - Collect annotated Bharatanatyam videos
   - Build mudra taxonomy database
   - Create emotion-to-rasa mapping corpus

4. **Performance Optimization**
   - GPU acceleration for video processing
   - Batch processing for multiple videos
   - Caching for repeated analyses

## Scalability Considerations

- **Horizontal Scaling**: FastAPI supports multiple workers
- **Queue System**: Add Celery for async video processing
- **Storage**: Migrate to S3/GCS for video storage
- **CDN**: Serve static assets via CDN
- **Caching**: Redis for analysis results