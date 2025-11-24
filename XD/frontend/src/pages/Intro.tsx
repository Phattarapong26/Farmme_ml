import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const texts = [
  'ยินดีต้อนรับ',
  'Welcome',
  'สู่โลกแห่งการเกษตร',
  'To the World of Agriculture',
  'เราพร้อมช่วยคุณ',
  'We are Ready to Help',
  'วิเคราะห์ ทำนาย',
  'Analyze & Predict',
  '',
];

export default function IntroPage() {
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    // Check if user has seen intro before
    const hasSeenIntro = localStorage.getItem('hasSeenIntro');
    if (hasSeenIntro === 'true') {
      window.location.href = '/';
      return;
    }

    // Cycle through texts
    const textInterval = setInterval(() => {
      setCurrentIndex((prev) => {
        if (prev < texts.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 600); // Change every 600ms

    // Show subtitle and logo after texts
    const contentTimer = setTimeout(() => {
      setShowContent(true);
    }, texts.length * 600);

    // Navigate after everything shown with full page refresh
    const navTimer = setTimeout(() => {
      localStorage.setItem('hasSeenIntro', 'true');
      window.location.href = '/';
    }, texts.length * 600 + 2000); // texts + 2 seconds for content

    return () => {
      clearInterval(textInterval);
      clearTimeout(contentTimer);
      clearTimeout(navTimer);
    };
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen overflow-hidden">
      {/* Main Text - Center of screen */}
      <div className="absolute inset-0 flex items-center justify-center px-4">
        <AnimatePresence mode="wait">
          <motion.h1
            key={currentIndex}
            initial={{ opacity: 0, y: 30, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -30, scale: 0.9 }}
            transition={{ 
              duration: 0.5,
              ease: [0.4, 0, 0.2, 1]
            }}
            className="text-5xl md:text-7xl lg:text-8xl font-bold text-emerald-600 text-center"
          >
            {texts[currentIndex]}
          </motion.h1>
        </AnimatePresence>
      </div>

      {/* Logo - Fade in after texts, centered on screen */}
      <AnimatePresence>
        {showContent && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
            className="flex items-center justify-center"
          >
            <img src="/logo.png" alt="FarmMe Logo" className="max-w-full h-auto" style={{ maxHeight: '40vh' }} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
