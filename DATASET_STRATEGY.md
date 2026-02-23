# Dataset Collection & Annotation Strategy
## For Bharatanatyam AI Story Generator

---

## Overview

This document outlines a comprehensive strategy for collecting, annotating, and utilizing datasets to improve the Bharatanatyam dance interpretation system. The current MVP uses pre-trained MediaPipe models with rule-based classification. To achieve production-grade accuracy, custom-trained models require domain-specific datasets.

---

## 1. Dataset Requirements

### 1.1 Video Data Requirements

**Minimum Dataset Size:**
- **Training**: 500-1000 annotated Bharatanatyam performance videos
- **Validation**: 100-200 videos
- **Testing**: 100-200 videos

**Video Specifications:**
- **Duration**: 30 seconds to 5 minutes per video
- **Resolution**: Minimum 720p (1280x720), preferably 1080p
- **Frame Rate**: 25-30 FPS
- **Format**: MP4, MOV, AVI
- **Lighting**: Varied (stage lighting, natural light, studio)
- **Camera Angles**: Front-facing, side-facing, 45-degree angles
- **Background**: Both plain and theatrical backgrounds

**Diversity Requirements:**
- Multiple dancers (different ages, body types, skill levels)
- Various Bharatanatyam styles (Kalakshetra, Pandanallur, Vazhuvoor)
- Different performance contexts (solo, duet, group)
- Various costumes and jewelry
- Different tempos and musical accompaniments

---

## 2. Annotation Requirements

### 2.1 Frame-Level Annotations

**Skeletal Pose Annotations:**
- Full body keypoints (33 landmarks per MediaPipe Pose standard)
- Joint angles for classical poses (aramandi, muzhumandi, etc.)
- Annotate every 5th frame for training efficiency

**Hand Gesture (Mudra) Annotations:**
- **28 Single-Hand Mudras (Asamyuta Hastas):**
  - Pataka, Tripataka, Ardhapataka, Kartarimukha
  - Mayura, Ardhachandra, Arala, Shukatunda
  - Mushti, Shikhara, Kapittha, Katakamukha
  - Suchi, Chandrakala, Padmakosha, Sarpashirsha
  - Mrigashirsha, Simhamukha, Kangula, Alapadma
  - Chatura, Bhramara, Hamsasya, Hamsapaksha
  - Samdamsha, Mukula, Tamrachuda, Trisula
  
- **24 Double-Hand Mudras (Samyuta Hastas):**
  - Anjali, Kapota, Karkata, Swastika
  - Dola, Pushpaputa, Utsanga, Shivalinga
  - Katakavardana, Kartariswastika, Shakata, Shankha
  - Chakra, Samputa, Pasha, Kilaka
  - Matsya, Kurma, Varaha, Garuda
  - Nagabandha, Khatwa, Bherunda, Avahittha

**Facial Expression Annotations:**
- **9 Rasas (Emotions):**
  1. Shringara (Love/Beauty)
  2. Hasya (Laughter/Joy)
  3. Karuna (Compassion/Sorrow)
  4. Raudra (Fury/Anger)
  5. Veera (Heroism/Courage)
  6. Bhayanaka (Terror/Fear)
  7. Bibhatsa (Disgust)
  8. Adbhuta (Wonder/Amazement)
  9. Shanta (Peace/Tranquility)

- **Facial Landmarks**: 468 points per MediaPipe Face Mesh
- **Key Features**: Eye gaze, eyebrow position, mouth shape

### 2.2 Sequence-Level Annotations

**Adavu Classification:**
- Identify and label specific adavu sequences
- Common adavus: Tatta, Natta, Visharu, Kudittam, etc.
- Temporal start and end frames

**Narrative Context:**
- Story being portrayed (e.g., "Depicting Krishna's childhood")
- Character being portrayed (e.g., "Radha", "Krishna", "Shiva")
- Scene description (e.g., "Prayer to deity", "Battle scene")

**Action Segments:**
- Segment videos into meaningful action units
- Label transitions between poses
- Mark rhythmic cycles (tala)

---

## 3. Data Collection Strategy

### 3.1 Data Sources

**Primary Sources:**
1. **Dance Academies & Schools**
   - Partner with Bharatanatyam institutions
   - Record student performances at various skill levels
   - Obtain consent forms and permissions

2. **Professional Performances**
   - License recordings from cultural festivals
   - Collaborate with professional dancers
   - Use publicly available YouTube videos (with attribution)

3. **Commissioned Recordings**
   - Hire professional dancers to perform specific sequences
   - Control lighting, angles, and background
   - Capture high-quality training data

**Secondary Sources:**
4. **Historical Archives**
   - Digitize archival footage (with proper permissions)
   - Historical performances by legendary artists

5. **Public Datasets**
   - Search for existing Bharatanatyam datasets in research repositories
   - Collaborate with universities and research institutions

### 3.2 Data Collection Workflow

```
1. Identify Source → 2. Obtain Permissions → 3. Record/Download
     ↓
4. Quality Check → 5. Metadata Tagging → 6. Store in Repository
     ↓
7. Assign to Annotators → 8. Annotation Phase → 9. Quality Assurance
     ↓
10. Version Control → 11. Dataset Release → 12. Model Training
```

### 3.3 Annotation Tools

**Recommended Tools:**
1. **CVAT (Computer Vision Annotation Tool)**
   - Open-source, web-based
   - Supports video annotation
   - Keypoint annotation support

2. **Label Studio**
   - Flexible annotation interface
   - Custom annotation schemas
   - ML-assisted labeling

3. **VGG Image Annotator (VIA)**
   - Lightweight, browser-based
   - Good for frame-by-frame annotation

4. **Custom Annotation Pipeline**
   - Build custom tool using MediaPipe for pre-annotation
   - Human annotators refine and classify
   - Reduces annotation time by 60-70%

---

## 4. Annotation Guidelines

### 4.1 Mudra Annotation Protocol

1. **Frame Selection**: Annotate when mudra is fully formed and held
2. **Bounding Boxes**: Draw around each hand
3. **Mudra Label**: Assign specific mudra name (from the 52 mudras)
4. **Confidence Score**: Low/Medium/High based on clarity
5. **Occlusion**: Mark if hand is partially hidden
6. **Transition Frames**: Mark frames where mudra is transitioning

### 4.2 Emotion Annotation Protocol

1. **Rasa Identification**: Identify primary rasa being expressed
2. **Intensity**: Rate emotion intensity (1-5 scale)
3. **Temporal Span**: Mark start and end of emotional expression
4. **Multi-Emotion**: Mark if multiple emotions are layered
5. **Context**: Note narrative context (e.g., "Krishna is playful")

### 4.3 Action Annotation Protocol

1. **Adavu Type**: Identify specific adavu being performed
2. **Tempo**: Mark as slow/medium/fast
3. **Repetition**: Count number of repetitions
4. **Symmetry**: Note if movements are symmetric or asymmetric

---

## 5. Data Quality Assurance

### 5.1 Quality Metrics

- **Inter-Annotator Agreement**: Minimum 85% agreement
- **Annotation Completeness**: 100% of required fields filled
- **Consistency**: Same mudra/emotion labeled consistently across videos
- **Expert Review**: 10% of annotations reviewed by Bharatanatyam experts

### 5.2 Quality Control Process

1. **Training Phase**: Annotators trained by Bharatanatyam experts
2. **Pilot Annotation**: 10 videos annotated as pilot
3. **Agreement Check**: Measure inter-annotator agreement
4. **Feedback Loop**: Refine guidelines based on disagreements
5. **Production Annotation**: Full dataset annotation
6. **Random Audits**: 10% random sample reviewed by experts
7. **Corrections**: Identified errors corrected

---

## 6. Data Storage & Management

### 6.1 Storage Structure

```
bharatanatyam_dataset/
├── videos/
│   ├── train/
│   ├── val/
│   └── test/
├── annotations/
│   ├── mudras/
│   │   ├── train.json
│   │   ├── val.json
│   │   └── test.json
│   ├── emotions/
│   │   ├── train.json
│   │   ├── val.json
│   │   └── test.json
│   └── sequences/
│       ├── train.json
│       ├── val.json
│       └── test.json
├── metadata/
│   ├── dancer_info.csv
│   ├── video_metadata.csv
│   └── annotation_guidelines.pdf
└── README.md
```

### 6.2 Annotation Format (JSON)

```json
{
  "video_id": "bharatanatyam_001",
  "filename": "performance_dancer1_2024.mp4",
  "duration_seconds": 120.5,
  "fps": 30,
  "resolution": [1920, 1080],
  "dancer": {
    "id": "dancer_001",
    "experience_years": 15,
    "style": "Kalakshetra"
  },
  "annotations": [
    {
      "frame_number": 150,
      "timestamp": 5.0,
      "mudra": {
        "right_hand": "Pataka",
        "left_hand": "Pataka",
        "combined": "Anjali",
        "confidence": "high"
      },
      "emotion": {
        "rasa": "Shanta",
        "intensity": 4
      },
      "action": {
        "adavu": "Tatta Adavu",
        "pose": "Aramandi",
        "description": "Prayer gesture in half-sitting posture"
      }
    }
  ]
}
```

---

## 7. Model Training Strategy

### 7.1 Training Pipeline

1. **Data Preprocessing**
   - Frame extraction
   - Normalization
   - Augmentation (rotation, scaling, brightness)

2. **Feature Extraction**
   - Use MediaPipe for baseline features
   - Extract hand landmarks, pose keypoints

3. **Model Architecture**
   - **Mudra Classifier**: CNN + LSTM
   - **Emotion Classifier**: Facial CNN
   - **Action Recognition**: 3D CNN or Transformer

4. **Training**
   - Transfer learning from pre-trained models
   - Fine-tune on Bharatanatyam dataset
   - Multi-task learning (joint mudra + emotion)

5. **Evaluation**
   - Accuracy, Precision, Recall, F1-Score
   - Confusion matrices for mudras and emotions
   - Temporal coherence metrics

---

## 8. Ethical Considerations

### 8.1 Data Privacy
- Obtain explicit consent from dancers
- Anonymize personal information
- Secure storage of video data

### 8.2 Cultural Sensitivity
- Work with Bharatanatyam experts for validation
- Respect the cultural and spiritual significance
- Ensure accurate representation of art form

### 8.3 Bias Mitigation
- Include diverse dancers (age, body type, region)
- Balance dataset across different styles
- Avoid stereotypical representations

---

## 9. Timeline & Budget Estimate

### 9.1 Timeline (12 months)

- **Months 1-2**: Partnership development, data collection planning
- **Months 3-5**: Video recording and collection (500 videos)
- **Months 6-9**: Annotation phase (3 annotators + 1 expert reviewer)
- **Months 10-11**: Quality assurance, dataset refinement
- **Month 12**: Dataset release, model training

### 9.2 Budget Estimate

- **Video Recording**: $10,000 (commissioned performances)
- **Licensing**: $5,000 (public performance rights)
- **Annotation**: $30,000 (3 annotators × 4 months × $2,500/month)
- **Expert Review**: $5,000 (Bharatanatyam expert consultation)
- **Tools & Infrastructure**: $3,000 (annotation tools, storage)
- **Total**: ~$53,000

---

## 10. Immediate Next Steps (for MVP)

While building the full dataset:

1. **Use Public Videos**: YouTube videos (with attribution)
2. **Crowdsource Annotations**: Partner with dance schools for community annotation
3. **Active Learning**: Use current model predictions to identify uncertain cases for annotation
4. **Iterative Improvement**: Continuously improve with small batches of new data

---

## Conclusion

This dataset strategy provides a roadmap for transitioning from the current rule-based MVP to a production-grade AI system. The key is to start small, iterate quickly, and gradually build a comprehensive dataset with high-quality annotations. Collaboration with the Bharatanatyam community is essential for both data collection and cultural authenticity.