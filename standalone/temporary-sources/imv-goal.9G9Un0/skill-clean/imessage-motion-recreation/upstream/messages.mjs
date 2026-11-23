import { readFileSync, writeFileSync } from 'node:fs';
import { esc, fontCss, svgMarkup } from '../scripts/engines/common.mjs';

const [sceneFile, output] = process.argv.slice(2);
const scene = JSON.parse(readFileSync(sceneFile, 'utf8'));
const { fpsNum, fpsDen, frameCount } = scene.timeline.picture;
const rate = fpsNum / fpsDen;
const duration = frameCount / rate;
const visibleLayers = (layers) => layers.map((layer) => ({
  ...layer,
  start: 0,
  end: duration,
  opacity: 1,
  keyframes: {},
  ...(layer.children && { children: visibleLayers(layer.children) }),
}));
const staticScene = { ...scene, layers: visibleLayers(scene.layers) };
const art = svgMarkup(staticScene, 0, undefined, false)
  .replaceAll(/<g data-layer="([^"]+)"/g, (_, id) => {
    const safe = id.replaceAll(/[^a-z0-9-]/gi, (char) => '_' + char.charCodeAt(0).toString(16) + '_');
    return '<g id="messages-' + safe + '" data-imv-layer="' + id + '"';
  });
const sceneData = JSON.stringify(scene).replaceAll('<', '\\u003c');

// The compiled DOM keeps one stable wrapper per layer. HyperFrames seeks the
// paused timeline, and our shared evaluator supplies the SVG state at that time.
writeFileSync(output, `<template>
<style>#root { position: absolute; inset: 0; } ${fontCss(scene)}</style>
<div id="root" data-composition-id="messages" data-width="${scene.width}" data-height="${scene.height}">
  <div id="messages-art" aria-label="${esc(scene.title)}">${art}</div>
</div>
<script>
(async () => {
  const { svgMarkup } = await import(new URL('assets/scene-runtime.mjs', document.baseURI));
  const scene = ${sceneData};
  const art = document.getElementById('messages-art');
  const parser = new DOMParser();
  const layers = Array.from(art.querySelectorAll('[data-imv-layer]'), (el) => ({
    el, id: el.dataset.imvLayer, leaf: !el.querySelector('[data-imv-layer]'),
  }));
  await document.fonts.ready;
  const clock = { time: 0 };
  const draw = () => {
    // Rendered timestamps land on the output frame grid. Deriving the time
    // from the frame also removes browser/GSAP sub-frame rounding at cuts.
    const frame = Math.min(${frameCount - 1}, Math.max(0, Math.floor(clock.time * ${rate} + 0.001)));
    const next = parser.parseFromString(svgMarkup(scene, frame / ${rate}, undefined, false), 'image/svg+xml');
    const states = new Map(Array.from(next.querySelectorAll('[data-layer]'), (node) => [node.getAttribute('data-layer'), node]));
    for (const { el, id, leaf } of layers) {
      const state = states.get(id);
      el.style.display = state ? '' : 'none';
      if (!state) continue;
      for (const key of ['opacity', 'transform']) el.setAttribute(key, state.getAttribute(key));
      el.style.filter = state.style?.filter || '';
      if (leaf && el.innerHTML !== state.innerHTML) el.innerHTML = state.innerHTML;
    }
  };
  const timeline = gsap.timeline({ paused: true });
  timeline.to(clock, { time: ${duration}, duration: ${duration}, ease: 'none', onUpdate: draw }, 0);
  draw();
  window.__timelines.messages = timeline;
})();
</script>
</template>\n`);
