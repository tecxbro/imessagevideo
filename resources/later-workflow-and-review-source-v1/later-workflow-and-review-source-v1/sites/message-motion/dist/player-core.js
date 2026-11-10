(function (root) {
  'use strict';
  function clampTime(time, duration) {
    const value = Number(time);
    return Math.max(0, Math.min(Number.isFinite(value) ? value : 0, Number.isFinite(duration) ? duration : Infinity));
  }
  function sourceTime(time, segments = []) {
    const t = clampTime(time);
    if (!segments.length) return t;
    for (const segment of segments) {
      const start = segment.candidate_start ?? segment.output_start ?? 0;
      if (t >= start && t < start + segment.duration) return (segment.reference_start ?? segment.source_start ?? 0) + t - start;
    }
    const last = segments[segments.length - 1];
    const end = (last.candidate_start ?? last.output_start ?? 0) + last.duration;
    if (t >= end) return (last.reference_start ?? last.source_start ?? 0) + last.duration;
    return t;
  }
  function formatTime(time) {
    const seconds = Math.floor(Math.max(0, Number(time) || 0));
    return Math.floor(seconds / 60) + ':' + String(seconds % 60).padStart(2, '0');
  }
  function validateFilm(film) {
    if (!film || !film.id || !film.title || !film.source || !(film.duration > 0)) throw new Error('Incomplete film metadata');
    const methods = ['remotion', 'gsap', 'html', 'motion-canvas', 'pillow'];
    for (const method of methods) if (!film.methods?.[method]) throw new Error('Missing ' + method + ' for ' + film.id);
    return film;
  }
  function playbackMessage(error) {
    if (error?.name === 'NotAllowedError') return 'Your browser is waiting for a tap. Press play on the video to begin.';
    if (error?.code === 2) return 'The video connection was interrupted. Press play to retry, or open the MP4 directly.';
    if (error?.code === 3) return 'This browser could not decode the video. Try opening the MP4 directly.';
    return 'The video could not be loaded. Try opening the MP4 directly.';
  }
  root.MotionReview = Object.freeze({clampTime, sourceTime, formatTime, validateFilm, playbackMessage});
})(typeof window === 'undefined' ? globalThis : window);
