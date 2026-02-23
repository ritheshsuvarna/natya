# Bharatanatyam AI Story Generator

A web application that analyzes Bharatanatyam dance videos and generates narrative stories using computer vision and AI. Built this as a way to bring technology and classical Indian dance together.

## Why I Built This

I've always been fascinated by Bharatanatyam and thought it would be cool to use AI to help people understand the stories being told in the dance. Most people don't know what the mudras (hand gestures) mean or what narrative is unfolding. This tool bridges that gap by analyzing the dance in real-time and explaining what's happening.

## What It Does

1. **Video Upload**: Users upload a Bharatanatyam dance video
2. **Computer Vision Analysis**: Uses MediaPipe to detect:
   - Pose and body movements
   - Hand gestures (mudras)
   - Facial expressions and emotions
3. **Story Generation**: GPT-5.2 analyzes the detected movements and creates a narrative explanation
4. **Beautiful UI**: Displays results with timeline and detailed analysis

## Tech Stack

**Backend:**
- FastAPI (Python)
- MediaPipe (pose, hand, face detection)
- OpenAI GPT-5.2 via Emergent LLM
- MongoDB (data storage)
- Uvicorn (ASGI server)

**Frontend:**
- React.js
- Tailwind CSS
- Shadcn/ui components
- Axios for API calls
- Framer Motion for animations

**Deployment:**
- Kubernetes
- Supervisor (process management)
- Nginx (reverse proxy)

## Getting Started

### Prerequisites

Make sure you have:
- Python 3.11+ (I ran into issues with 3.10, so 3.11 is the minimum)
- Node.js 18+
- MongoDB running locally or in the cloud
- Emergent LLM key (get this from your Emergent account)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file:
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="bharatanatyam_db"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=your-key-here
```

Run the server:
```bash
python server.py
```

Server should be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
yarn install
```

Create `.env` file:
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
WDS_SOCKET_PORT=3000
ENABLE_HEALTH_CHECK=false
```

Start the dev server:
```bash
yarn start
```

Open `http://localhost:3000` in your browser

## How It Works

### Video Analysis Pipeline

The video processing happens in several stages:

1. **Frame Sampling**: Instead of processing every frame (which is slow), I sample frames evenly across the video. This keeps processing time under 5 seconds for most videos.

2. **MediaPipe Detection**: For each frame:
   - Extract pose landmarks (33 points across the body)
   - Detect hand landmarks (21 points per hand)
   - Detect facial features

3. **Classification**: Based on the landmarks, classify:
   - Which mudra is being performed
   - What emotion is expressed
   - What action/movement is happening

4. **Story Generation**: Feed all this data to GPT and let it create a narrative

### Mudra Classification

Right now I'm using rule-based classification based on hand landmark distances and angles. It works okay for MVP but could definitely be improved with a trained ML model. The rules I have:

- If thumb and index finger are close → Anjali (Prayer)
- If fingers are spread → Pataka (Flag)
- And so on...

This is probably the weakest part of the system. Training a custom CNN on actual mudra data would give much better results.

## Common Issues I Ran Into

### 1. Video Format Problems
**Problem:** Got 413 errors on large videos
**Solution:** Compress videos before upload. I recommend 720p, 10-15 seconds max

### 2. MediaPipe Detection Fails on Poor Quality
**Problem:** If lighting is bad or the dancer is too far away, MediaPipe can't detect anything
**Solution:** Users need decent lighting and the dancer should be in frame clearly

### 3. MongoDB Connection Timeouts
**Problem:** Sometimes the connection would drop
**Solution:** Added connection pooling and retry logic

### 4. CORS Issues During Development
**Problem:** Frontend couldn't reach backend during local dev
**Solution:** Set `CORS_ORIGINS="*"` in .env (obviously change this in production)

### 5. OpenAI Timeouts
**Problem:** Story generation would timeout on large analysis data
**Solution:** Limited the analysis to top 20 scenes

## Project Structure

```
.
├── backend/
│   ├── server.py (main FastAPI app)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.js
│   │   │   └── LandingPage.js
│   │   ├── components/
│   │   │   └── ui/ (shadcn components)
│   │   └── App.js
│   ├── package.json
│   └── .env
└── README.md
```

## Performance Tips

If the app is running slow:

1. **Reduce video length**: Longer videos = longer processing time
2. **Lower resolution**: Process at 480p instead of 1080p
3. **Use GPU**: If available, enable CUDA in OpenCV
4. **Increase max_frames limit**: Default is 50 frames, you can lower this

## What I Learned

### Design Decisions

- **Why MediaPipe?** It's pre-trained, accurate, and free. Training custom models would take months.
- **Why Emergent LLM?** Better integration than raw OpenAI API, simpler auth
- **Why Mongo?** Document-based storage is perfect for JSON-like analysis data
- **Why React?** It's what I know, Tailwind makes styling fast

### What I'd Do Differently

- **Authentication**: Didn't add user accounts initially, should add OAuth for production
- **Video Storage**: Currently videos are deleted after analysis. Could store them for re-analysis
- **Caching**: Could cache similar analyses to avoid re-processing
- **Mobile**: No mobile app yet, React Native version would be cool

## Testing

I didn't write formal unit tests (my bad), but here's how to manually test:

```bash
# Test backend health
curl http://localhost:8000/api/

# Test video upload
curl -X POST http://localhost:8000/api/upload-video \
  -F "file=@sample_video.mp4"

# Check analysis
curl http://localhost:8000/api/analysis/{video_id}
```

For frontend testing, just use the UI. Upload a video, wait for analysis, see if the story makes sense.

## Future Work

Things I want to add but haven't gotten to yet:

- [ ] Real-time webcam analysis
- [ ] Training a custom mudra classifier (CNN + LSTM)
- [ ] Multi-language support (Hindi, Tamil, Telugu)
- [ ] Audio analysis (detect raga and rhythm)
- [ ] User accounts and video history
- [ ] Mobile app (React Native)
- [ ] Better emotion recognition
- [ ] Character/narrative recognition (which story is being told?)

## Deployment Notes

If you're deploying this:

1. **Use environment variables** for all config (I learned this the hard way)
2. **Don't commit .env files** to git
3. **Use HTTPS** in production (I use Let's Encrypt)
4. **Set proper CORS origins** - don't leave it as `*`
5. **Monitor GPU usage** if running on GPU instances
6. **Set up log rotation** - videos create large log entries

Currently running on Kubernetes with Supervisor managing the processes. Takes about 5-10 seconds per video for end-to-end processing.

## Troubleshooting

### Backend won't start
- Check MongoDB is running
- Check all requirements are installed: `pip install -r requirements.txt`
- Check your .env file has all required variables

### Frontend blank page
- Check browser console for errors
- Verify `REACT_APP_BACKEND_URL` is correct in .env
- Make sure backend is running

### Analysis fails
- Check video quality and lighting
- Try a shorter video first
- Check Emergent LLM key is valid

### Story generation is weird
- This is expected sometimes with AI. It's hallucinating based on the pose data
- Try a clearer, more well-lit video
- The accuracy improves with better pose detection

## Inspirations & Resources

- **MediaPipe**: https://google.github.io/mediapipe/ - amazing computer vision library
- **OpenAI API**: https://platform.openai.com/docs/
- **Bharatanatyam Info**: https://en.wikipedia.org/wiki/Bharatanatyam
- **FastAPI**: https://fastapi.tiangolo.com/ - love how fast it is
- **Tailwind CSS**: https://tailwindcss.com/ - best styling framework imo

## License

MIT - use it however you want

## Contact

Built with 🎭 and ☕ by Rithesh

If you found this useful or have feedback, let me know!

---

**Last updated:** February 2026
**Current status:** MVP working, actively improving

