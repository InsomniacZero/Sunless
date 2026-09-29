/**
 * Sunless Gateway - Skiper7 Nike-Inspired Preloader (Shadow Slave Edition)
 * Rapid montage animation through Shadow Slave artwork, bold typography & seamless exit.
 */

(function () {
  'use strict';

  const SHADOW_SLAVE_IMAGES = [
    '/static/preloader/3a6a0a99717d5533928eecd2046ec085.jpg',
    '/static/preloader/40efbc5694229238b0741afcce6c3ddf.jpg',
    '/static/preloader/795c223825dfa27440ac1da9ff8c1109.jpg',
    '/static/preloader/8300bdc6821115d2a56d8d507d2a1dde.jpg',
    '/static/preloader/9ac47ecd3a2f7e405b494a618a35298d.jpg',
    '/static/preloader/a1dfd20723b5e270ea911068051e6bf3.jpg',
    '/static/preloader/cbbb353701a4e0545a5903413d71c77e.jpg'
  ];

  const PRELOADER_DURATION_MS = 2500; // Matches skiper7 standard duration
  const FRAME_INTERVAL_MS = 200;      // Rapid cinematic staccato cut

  let currentImageIdx = 0;
  let intervalId = null;
  let animationFrameId = null;
  let startTime = null;
  let isExiting = false;

  // Preload images into memory
  function preloadAllImages() {
    SHADOW_SLAVE_IMAGES.forEach(src => {
      const img = new Image();
      img.src = src;
    });
  }

  function initPreloader() {
    const preloaderEl = document.getElementById('sunless-skiper-preloader');
    if (!preloaderEl) return;

    preloadAllImages();

    const slideElements = preloaderEl.querySelectorAll('.skiper7-slide');
    const progressFill = preloaderEl.querySelector('.skiper7-progress-fill');

    if (!slideElements.length) return;

    // Reset state
    isExiting = false;
    currentImageIdx = 0;
    preloaderEl.classList.remove('skiper7-exiting', 'skiper7-hidden');
    slideElements.forEach((el, i) => {
      if (i === 0) el.classList.add('active');
      else el.classList.remove('active');
    });

    if (progressFill) progressFill.style.width = '0%';

    startTime = performance.now();

    // Montage cycling
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(() => {
      if (isExiting) return;
      slideElements[currentImageIdx].classList.remove('active');
      currentImageIdx = (currentImageIdx + 1) % slideElements.length;
      slideElements[currentImageIdx].classList.add('active');
    }, FRAME_INTERVAL_MS);

    // Progress bar loop
    function updateProgress(now) {
      if (isExiting) return;
      const elapsed = now - startTime;
      const progress = Math.min(100, (elapsed / PRELOADER_DURATION_MS) * 100);
      if (progressFill) {
        progressFill.style.width = progress.toFixed(1) + '%';
      }

      if (elapsed >= PRELOADER_DURATION_MS) {
        exitPreloader();
      } else {
        animationFrameId = requestAnimationFrame(updateProgress);
      }
    }

    animationFrameId = requestAnimationFrame(updateProgress);

    // Click anywhere or press key to skip immediately
    const skipHandler = (e) => {
      if (e.type === 'keydown' && e.key !== 'Escape' && e.key !== ' ' && e.key !== 'Enter') return;
      exitPreloader();
    };

    preloaderEl.addEventListener('click', skipHandler, { once: true });
    window.addEventListener('keydown', skipHandler, { once: true });
  }

  function exitPreloader() {
    if (isExiting) return;
    isExiting = true;

    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }

    const preloaderEl = document.getElementById('sunless-skiper-preloader');
    if (!preloaderEl) return;

    // Trigger smooth translateY(-100%) exit transition
    preloaderEl.classList.add('skiper7-exiting');
    window.dispatchEvent(new CustomEvent('sunless-preloader-exit'));

    setTimeout(() => {
      preloaderEl.classList.add('skiper7-hidden');
      window.dispatchEvent(new CustomEvent('sunless-preloader-complete'));
    }, 1050);
  }

  // Global manual replay function
  window.playSunlessPreloader = function () {
    const preloaderEl = document.getElementById('sunless-skiper-preloader');
    if (preloaderEl) {
      initPreloader();
    }
  };
  window.playPreloader = window.playSunlessPreloader;

  // Global key combo: Shift + P to replay preloader at any time
  window.addEventListener('keydown', (e) => {
    if (e.shiftKey && (e.key === 'P' || e.key === 'p') && !(e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA'))) {
      window.playSunlessPreloader();
    }
  });

  // Auto-run on DOM ready or immediate if already loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPreloader);
  } else {
    initPreloader();
  }
})();
