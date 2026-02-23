import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sparkles, Video, Brain, BookOpen } from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Hero glow effect */}
      <div 
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] opacity-30"
        style={{
          background: 'radial-gradient(circle at center, rgba(217, 56, 30, 0.15) 0%, rgba(5, 5, 5, 0) 70%)'
        }}
      />

      {/* Navigation */}
      <nav className="relative z-10 p-6 md:p-8 flex justify-between items-center">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3"
        >
          <Sparkles className="w-8 h-8 text-primary" />
          <span className="font-heading text-2xl font-bold">Natya AI</span>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <Button
            data-testid="nav-get-started-btn"
            onClick={() => navigate('/dashboard')}
            className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-sm px-6 py-5 font-medium transition-all duration-300"
          >
            Get Started
          </Button>
        </motion.div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-6 md:px-12 lg:px-24 py-12 md:py-24">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 min-h-[90vh] items-center">
          {/* Left Content */}
          <motion.div
            className="lg:col-span-7 space-y-8"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="space-y-6">
              <h1 className="font-heading text-5xl md:text-7xl font-bold tracking-tight leading-none">
                Dance Stories,
                <br />
                <span className="text-primary">Unveiled by AI</span>
              </h1>
              
              <p className="font-body text-base md:text-lg leading-relaxed text-muted-foreground max-w-2xl">
                Experience the magic of Bharatanatyam through AI. Our system observes classical Indian dance performances and translates intricate movements, mudras, and expressions into beautiful natural-language narratives.
              </p>
            </div>

            <div className="flex gap-4 flex-wrap">
              <Button
                data-testid="hero-start-analyzing-btn"
                onClick={() => navigate('/dashboard')}
                className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-sm px-8 py-6 text-lg font-medium transition-all duration-300 pulse-glow"
              >
                Start Analyzing
              </Button>
              
              <Button
                data-testid="hero-learn-more-btn"
                variant="outline"
                className="bg-transparent border border-secondary text-secondary hover:bg-secondary/10 rounded-sm px-6 py-6 text-lg font-medium transition-all duration-300"
              >
                Learn More
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 pt-8">
              <div className="space-y-1">
                <div className="font-heading text-3xl font-bold text-accent">AI</div>
                <div className="font-mono text-xs tracking-wider uppercase text-muted-foreground/60">Powered</div>
              </div>
              <div className="space-y-1">
                <div className="font-heading text-3xl font-bold text-secondary">Real-time</div>
                <div className="font-mono text-xs tracking-wider uppercase text-muted-foreground/60">Analysis</div>
              </div>
              <div className="space-y-1">
                <div className="font-heading text-3xl font-bold text-primary">Cultural</div>
                <div className="font-mono text-xs tracking-wider uppercase text-muted-foreground/60">Authentic</div>
              </div>
            </div>
          </motion.div>

          {/* Right Image */}
          <motion.div
            className="lg:col-span-5 relative"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="relative rounded-xl overflow-hidden border border-border/50">
              <img
                src="https://images.unsplash.com/photo-1764014792666-0f9e3c8442a9?crop=entropy&cs=srgb&fm=jpg&q=85"
                alt="Bharatanatyam dancer"
                className="w-full h-auto object-cover"
              />
              <div className="absolute inset-0 bg-black/30"></div>
            </div>
          </motion.div>
        </div>

        {/* Features Section */}
        <motion.div
          className="py-24 space-y-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <h2 className="font-heading text-3xl md:text-5xl font-semibold tracking-tight text-center">
            How It Works
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-card/50 backdrop-blur-md border border-border/50 rounded-xl p-6 hover:border-primary/50 transition-colors duration-300">
              <Video className="w-12 h-12 text-primary mb-4" />
              <h3 className="font-heading text-2xl font-medium text-foreground/90 mb-3">
                Upload Video
              </h3>
              <p className="font-body text-base leading-relaxed text-muted-foreground">
                Upload your Bharatanatyam performance video. Our system supports various video formats.
              </p>
            </div>

            <div className="bg-card/50 backdrop-blur-md border border-border/50 rounded-xl p-6 hover:border-accent/50 transition-colors duration-300">
              <Brain className="w-12 h-12 text-accent mb-4" />
              <h3 className="font-heading text-2xl font-medium text-foreground/90 mb-3">
                AI Analysis
              </h3>
              <p className="font-body text-base leading-relaxed text-muted-foreground">
                Advanced computer vision detects poses, mudras, and expressions frame by frame.
              </p>
            </div>

            <div className="bg-card/50 backdrop-blur-md border border-border/50 rounded-xl p-6 hover:border-secondary/50 transition-colors duration-300">
              <BookOpen className="w-12 h-12 text-secondary mb-4" />
              <h3 className="font-heading text-2xl font-medium text-foreground/90 mb-3">
                Story Generation
              </h3>
              <p className="font-body text-base leading-relaxed text-muted-foreground">
                Natural language AI translates movements into beautiful, culturally sensitive narratives.
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8">
        <div className="container mx-auto px-6 md:px-12 text-center">
          <p className="font-body text-sm text-muted-foreground">
            Powered by MediaPipe, Google Generative AI, and OpenCV
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;