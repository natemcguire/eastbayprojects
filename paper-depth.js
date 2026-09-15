/* Decorative graph-paper layers; touch scrolling always stays browser-native. */
(() => {
  const stages = [...document.querySelectorAll('#hero, .launch-hero, .work-intro, .page-hero, .pitch, #services, #why')];
  for (const stage of stages) {
    stage.classList.add('paper-stage');
    for (const side of ['corner', 'edge']) {
      const layer = document.createElement('div');
      layer.className = `paper-layer paper-${side}`;
      layer.setAttribute('aria-hidden', 'true');
      stage.prepend(layer);
    }
  }
  const motion = matchMedia('(prefers-reduced-motion: no-preference) and (pointer: fine) and (min-width: 901px)');
  let frame = 0;
  const draw = () => {
    frame = 0;
    for (const stage of stages) {
      const rect = stage.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > innerHeight) continue;
      const offset = Math.max(-24, Math.min(24, -rect.top * 0.055));
      stage.style.setProperty('--paper-shift', `${offset.toFixed(1)}px`);
    }
  };
  const schedule = () => { if (!frame) frame = requestAnimationFrame(draw); };
  const configure = () => {
    removeEventListener('scroll', schedule);
    removeEventListener('resize', schedule);
    cancelAnimationFrame(frame);
    frame = 0;
    for (const stage of stages) stage.style.removeProperty('--paper-shift');
    if (motion.matches) {
      addEventListener('scroll', schedule, { passive: true });
      addEventListener('resize', schedule, { passive: true });
      schedule();
    }
  };
  motion.addEventListener('change', configure);
  configure();
})();
