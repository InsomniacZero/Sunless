import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * Sunless Gateway - Skiper7 Preloader (Shadow Slave Edition)
 * Based on @skiper-ui/skiper7 & afterdarktour.nike.com architecture
 * Adapted with Shadow Slave theme & Sunless Gateway branding.
 */

export interface Skiper7PreloaderProps {
  onComplete?: () => void;
  durationMs?: number;
  images?: string[];
  logoSrc?: string;
  topTitle?: string;
  topSubtitle?: string;
  brandTitle?: string;
  brandSubtitle?: string;
  taglineKicker?: string;
  taglineSub?: string;
  bottomTitle?: string;
  bottomSubtitle?: string;
}

const DEFAULT_SHADOW_SLAVE_IMAGES = [
  "/static/preloader/3a6a0a99717d5533928eecd2046ec085.jpg",
  "/static/preloader/40efbc5694229238b0741afcce6c3ddf.jpg",
  "/static/preloader/795c223825dfa27440ac1da9ff8c1109.jpg",
  "/static/preloader/8300bdc6821115d2a56d8d507d2a1dde.jpg",
  "/static/preloader/9ac47ecd3a2f7e405b494a618a35298d.jpg",
  "/static/preloader/a1dfd20723b5e270ea911068051e6bf3.jpg",
  "/static/preloader/cbbb353701a4e0545a5903413d71c77e.jpg",
];

export const Skiper7SunlessPreloader: React.FC<Skiper7PreloaderProps> = ({
  onComplete,
  durationMs = 2500,
  images = DEFAULT_SHADOW_SLAVE_IMAGES,
  logoSrc = "/logo.svg",
  topTitle = "SHADOW SLAVE",
  topSubtitle = "DOMAIN©2025",
  brandTitle = "Sunless",
  brandSubtitle = "Gateway",
  taglineKicker = "LOST FROM LIGHT",
  taglineSub = "[FATED] DOMAIN",
  bottomTitle = "STEP INTO",
  bottomSubtitle = "THE SHADOWS.",
}) => {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [progress, setProgress] = useState(0);

  // Fast montage cycling through Shadow Slave images
  useEffect(() => {
    const cycleInterval = setInterval(() => {
      setCurrentIdx((prev) => (prev + 1) % images.length);
    }, 200);

    return () => clearInterval(cycleInterval);
  }, [images.length]);

  // Smooth duration countdown & progress
  useEffect(() => {
    const start = performance.now();
    const frame = () => {
      const elapsed = performance.now() - start;
      const pct = Math.min(100, (elapsed / durationMs) * 100);
      setProgress(pct);

      if (elapsed < durationMs) {
        requestAnimationFrame(frame);
      } else {
        onComplete?.();
      }
    };

    const anim = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(anim);
  }, [durationMs, onComplete]);

  return (
    <motion.div
      initial={{ y: 0 }}
      exit={{ y: "-100%" }}
      transition={{ duration: 1.0, ease: [0.785, 0.135, 0.15, 0.86] }}
      onClick={() => onComplete?.()}
      className="fixed inset-0 z-[99999999] flex h-screen w-screen cursor-pointer flex-col items-center justify-between overflow-hidden bg-[#040404] select-none"
    >
      {/* Background Montage Images */}
      <div className="absolute inset-0 z-0 h-full w-full pointer-events-none">
        {images.map((img, i) => (
          <img
            key={img}
            src={img}
            alt={`Shadow Slave ${i + 1}`}
            className={`absolute inset-0 h-full w-full object-cover object-center filter brightness-[0.38] contrast-[1.35] saturate-[1.15] transition-opacity duration-150 ${
              i === currentIdx ? "opacity-100 scale-100 z-10" : "opacity-0 scale-105 z-0"
            }`}
          />
        ))}

        {/* Cinematic Vignette */}
        <div className="absolute inset-0 z-20 bg-[radial-gradient(ellipse_at_center,rgba(4,4,4,0.15)_0%,rgba(4,4,4,0.65)_60%,rgba(4,4,4,0.95)_100%)]" />
        {/* Subtle Scanlines */}
        <div className="absolute inset-0 z-30 opacity-40 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%)] bg-[length:100%_4px]" />
      </div>

      {/* Foreground Content - Just <logo> Sunless Gateway in middle of screen */}
      <div className="relative z-40 flex h-full w-full items-center justify-center p-6 text-center">
        <div className="flex items-center justify-center gap-4 md:gap-7">
          <div className="flex h-16 w-16 md:h-24 md:w-24 items-center justify-center drop-shadow-[0_0_24px_rgba(234,88,12,0.65)]">
            <img src={logoSrc} alt="Logo" className="h-full w-full object-contain" />
          </div>
          <div className="text-left font-black uppercase tracking-[-0.04em] text-white text-[clamp(2.4rem,6.5vw,5.2rem)] leading-none drop-shadow-[0_4px_28px_rgba(0,0,0,0.9)]">
            {brandTitle} <span className="text-[#f97316]">{brandSubtitle}</span>
          </div>
        </div>
      </div>

      {/* Footer Progress & Skip Cue */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center gap-2 pointer-events-none">
        <div className="h-[3px] w-[clamp(160px,24vw,260px)] overflow-hidden rounded-full bg-white/10 shadow-[0_0_10px_rgba(0,0,0,0.6)]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#ea580c] via-[#f97316] to-[#fb923c] shadow-[0_0_8px_#f97316] transition-[width] duration-75"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="font-mono text-[11px] uppercase tracking-wider text-white/40">
          Click anywhere or press ESC to enter
        </span>
      </div>
    </motion.div>
  );
};

export default Skiper7SunlessPreloader;
