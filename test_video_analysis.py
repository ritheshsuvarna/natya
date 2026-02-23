#!/usr/bin/env python3
"""Test video analysis without needing MongoDB or full server startup"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set up minimal environment
os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
os.environ['DB_NAME'] = 'test_db'
os.environ['CORS_ORIGINS'] = '*'

import cv2
import numpy as np
from pathlib import Path

# Import the analyze_video_frames function from server
try:
    # Create a dummy video file for testing
    import tempfile
    
    def create_test_video(filename, duration=2, fps=30):
        """Create a simple test video"""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (640, 480))
        
        num_frames = duration * fps
        for i in range(int(num_frames)):
            # Create a simple frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Add some simple patterns
            cv2.circle(frame, (320, 240), 50, (0, 255, 0), -1)
            cv2.putText(frame, f"Frame {i}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(frame)
        
        out.release()
        print(f"Created test video: {filename}")
    
    # Create test video
    import tempfile
    temp_dir = tempfile.gettempdir()
    test_video_path = os.path.join(temp_dir, "test_bharatanatyam.mp4")
    create_test_video(test_video_path)
    
    # Now test the analyze_video_frames function
    print("\nTesting video analysis function...")
    print("=" * 60)
    
    # Import and test the function
    from backend.server import analyze_video_frames
    
    print(f"Analyzing video: {test_video_path}")
    result = analyze_video_frames(test_video_path, max_frames=5)
    
    print(f"\nAnalysis Results:")
    print(f"  Total Frames: {result['total_frames']}")
    print(f"  FPS: {result['fps']}")
    print(f"  Duration: {result['duration_seconds']:.2f}s")
    print(f"  Scenes Analyzed: {len(result['scenes'])}")
    
    if result['scenes']:
        print(f"\n First Scene:")
        scene = result['scenes'][0]
        print(f"   Frame: {scene['frame_number']}")
        print(f"   Timestamp: {scene['timestamp_seconds']}s")
        print(f"   Action: {scene['action']}")
        print(f"   Mudra: {scene['mudra']}")
        print(f"   Emotion: {scene['emotion']}")
        print(f"   Interpretation: {scene['interpretation']}")
    
    print("\n" + "=" * 60)
    print("✅ Video analysis is working!")
    
    # Clean up
    if os.path.exists(test_video_path):
        os.remove(test_video_path)
        
except Exception as e:
    print(f"❌ Error during video analysis: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
