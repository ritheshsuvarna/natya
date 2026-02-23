import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Sparkles, Upload, ArrowLeft, Loader2, Play, Clock, Zap } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [generatingStory, setGeneratingStory] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [story, setStory] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('video/')) {
        toast.error("Please select a video file");
        return;
      }
      setSelectedFile(file);
      setAnalysis(null);
      setStory(null);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) {
      toast.error("Please select a video file first");
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setUploading(true);
    setAnalyzing(true);
    setUploadProgress(0);

    try {
      toast.info("Uploading and analyzing video...");
      
      const response = await axios.post(`${API}/upload-video`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });

      setAnalysis(response.data);
      toast.success("Video analyzed successfully!");
      
      // Automatically generate story
      await handleGenerateStory(response.data.video_id);
    } catch (error) {
      console.error('Error uploading video:', error);
      toast.error(error.response?.data?.detail || "Failed to analyze video");
    } finally {
      setUploading(false);
      setAnalyzing(false);
    }
  };

  const handleGenerateStory = async (videoId) => {
    setGeneratingStory(true);
    
    try {
      toast.info("Generating story with AI...");
      
      const response = await axios.post(`${API}/generate-story`, {
        analysis_id: videoId,
      });

      setStory(response.data.story);
      toast.success("Story generated successfully!");
    } catch (error) {
      console.error('Error generating story:', error);
      toast.error(error.response?.data?.detail || "Failed to generate story");
    } finally {
      setGeneratingStory(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 sticky top-0 bg-background/95 backdrop-blur-md z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Button
              data-testid="back-button"
              variant="ghost"
              onClick={() => navigate('/')}
              className="hover:bg-accent/10 hover:text-accent"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <Sparkles className="w-7 h-7 text-primary" />
              <span className="font-heading text-xl font-bold">Natya AI</span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs tracking-wider uppercase text-muted-foreground/60">Dashboard</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-6rem)]">
          {/* Upload Section */}
          <div className="col-span-1 lg:col-span-8 row-span-1 bg-card border border-border/50 rounded-xl overflow-hidden relative">
            <div className="p-8 h-full flex flex-col">
              {!selectedFile ? (
                <div className="flex-1 flex flex-col items-center justify-center space-y-6">
                  <Upload className="w-20 h-20 text-muted-foreground/40" />
                  <div className="text-center space-y-3">
                    <h2 className="font-heading text-3xl font-semibold">Upload Dance Video</h2>
                    <p className="font-body text-base text-muted-foreground max-w-md">
                      Select a Bharatanatyam performance video to analyze and generate a story
                    </p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*"
                    onChange={handleFileSelect}
                    className="hidden"
                    data-testid="video-file-input"
                  />
                  <Button
                    data-testid="select-video-btn"
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-sm px-8 py-6 text-lg font-medium transition-all duration-300 pulse-glow"
                  >
                    Select Video
                  </Button>
                </div>
              ) : (
                <div className="flex-1 flex flex-col space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <h3 className="font-heading text-2xl font-semibold">Selected Video</h3>
                      <p className="font-mono text-sm text-muted-foreground truncate max-w-md">
                        {selectedFile.name}
                      </p>
                    </div>
                    <Button
                      data-testid="change-video-btn"
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading || analyzing}
                      className="border-secondary text-secondary hover:bg-secondary/10"
                    >
                      Change Video
                    </Button>
                  </div>

                  {uploading && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Uploading...</span>
                        <span className="text-accent font-medium">{uploadProgress}%</span>
                      </div>
                      <Progress value={uploadProgress} className="h-2" />
                    </div>
                  )}

                  {!analysis && !analyzing ? (
                    <Button
                      data-testid="analyze-video-btn"
                      onClick={handleUploadAndAnalyze}
                      disabled={uploading}
                      className="bg-accent text-accent-foreground hover:bg-accent/90 rounded-sm px-8 py-6 text-lg font-medium w-full transition-all duration-300"
                    >
                      {uploading ? (
                        <>
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Play className="w-5 h-5 mr-2" />
                          Analyze Video
                        </>
                      )}
                    </Button>
                  ) : null}

                  {analyzing && (
                    <div className="flex items-center justify-center space-x-3 py-8">
                      <Loader2 className="w-8 h-8 text-accent animate-spin" />
                      <span className="font-body text-lg text-muted-foreground">AI is analyzing the dance...</span>
                    </div>
                  )}

                  {analysis && (
                    <div className="flex-1 overflow-y-auto space-y-4 bg-muted/20 rounded-lg p-6">
                      <h3 className="font-heading text-xl font-semibold mb-4">Analysis Results</h3>
                      
                      <div className="grid grid-cols-3 gap-4">
                        <div className="bg-card/50 rounded-lg p-4 border border-border/30">
                          <div className="flex items-center gap-2 mb-2">
                            <Clock className="w-4 h-4 text-primary" />
                            <span className="font-mono text-xs uppercase text-muted-foreground">Duration</span>
                          </div>
                          <p className="font-heading text-2xl font-semibold">
                            {analysis.analysis.duration_seconds.toFixed(1)}s
                          </p>
                        </div>
                        
                        <div className="bg-card/50 rounded-lg p-4 border border-border/30">
                          <div className="flex items-center gap-2 mb-2">
                            <Zap className="w-4 h-4 text-accent" />
                            <span className="font-mono text-xs uppercase text-muted-foreground">Scenes</span>
                          </div>
                          <p className="font-heading text-2xl font-semibold">
                            {analysis.analysis.scenes.length}
                          </p>
                        </div>
                        
                        <div className="bg-card/50 rounded-lg p-4 border border-border/30">
                          <div className="flex items-center gap-2 mb-2">
                            <Play className="w-4 h-4 text-secondary" />
                            <span className="font-mono text-xs uppercase text-muted-foreground">FPS</span>
                          </div>
                          <p className="font-heading text-2xl font-semibold">
                            {analysis.analysis.fps.toFixed(0)}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Story Panel */}
          <div className="col-span-1 lg:col-span-4 row-span-2 bg-card/50 backdrop-blur-md border border-border/50 rounded-xl p-6 overflow-y-auto">
            <div className="space-y-6">
              <div>
                <h2 className="font-heading text-2xl font-semibold mb-2">Story Script</h2>
                <p className="font-mono text-xs tracking-wider uppercase text-muted-foreground/60">
                  AI-Generated Narrative
                </p>
              </div>

              {generatingStory ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <Loader2 className="w-12 h-12 text-primary animate-spin" />
                  <p className="font-body text-base text-muted-foreground">Crafting your story...</p>
                </div>
              ) : story ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.8 }}
                  className="space-y-4"
                >
                  <div className="prose prose-invert max-w-none">
                    <div className="font-heading text-base leading-relaxed whitespace-pre-wrap text-foreground/90">
                      {story}
                    </div>
                  </div>
                  
                  <Button
                    data-testid="download-story-btn"
                    onClick={() => {
                      const blob = new Blob([story], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `bharatanatyam-story-${Date.now()}.txt`;
                      a.click();
                      toast.success("Story downloaded!");
                    }}
                    className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90 rounded-sm py-5"
                  >
                    Download Story
                  </Button>
                </motion.div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 space-y-4 text-center">
                  <BookOpen className="w-16 h-16 text-muted-foreground/30" />
                  <p className="font-body text-base text-muted-foreground max-w-sm">
                    Upload and analyze a video to generate a beautiful story about the dance performance
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Timeline Section */}
          <div className="col-span-1 lg:col-span-8 row-span-1 bg-card border border-border/50 rounded-xl p-4 overflow-x-auto">
            <h3 className="font-heading text-lg font-semibold mb-4">Scene Timeline</h3>
            
            {analysis ? (
              <div className="flex gap-3 pb-2">
                {analysis.analysis.scenes.slice(0, 10).map((scene, idx) => (
                  <div
                    key={idx}
                    className="flex-shrink-0 w-48 bg-muted/30 rounded-lg p-3 border border-border/30 hover:border-accent/50 transition-colors"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs text-accent">{scene.timestamp_seconds}s</span>
                        <span className="font-mono text-xs text-muted-foreground">#{idx + 1}</span>
                      </div>
                      <div className="space-y-1 text-xs">
                        <p className="text-foreground/80"><span className="font-semibold">Action:</span> {scene.action}</p>
                        <p className="text-foreground/80"><span className="font-semibold">Mudra:</span> {scene.mudra}</p>
                        <p className="text-foreground/80"><span className="font-semibold">Emotion:</span> {scene.emotion}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32">
                <p className="font-body text-sm text-muted-foreground">Timeline will appear after video analysis</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

import { BookOpen } from "lucide-react";
export default Dashboard;