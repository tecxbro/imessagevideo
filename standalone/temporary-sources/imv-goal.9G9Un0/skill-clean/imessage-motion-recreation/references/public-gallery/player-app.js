(() => {
  'use strict';
  const {clampTime, sourceTime, formatTime, validateFilm, playbackMessage} = window.MotionReview;
  const films = JSON.parse(document.getElementById('film-data').textContent).map(validateFilm);
  const labels = {remotion: 'Remotion', gsap: 'GSAP', html: 'HTML / SVG', 'motion-canvas': 'Motion Canvas', pillow: 'Pillow + FFmpeg'};
  const dialog = document.getElementById('player-dialog');
  const video = document.getElementById('recreation');
  const reference = document.getElementById('reference');
  const status = document.getElementById('player-status');
  const playButton = document.getElementById('play-toggle');
  const compareButton = document.getElementById('compare-toggle');
  const tabs = document.getElementById('method-tabs');
  const download = document.getElementById('download-video');
  let activeIndex = 0, activeMethod = 'gsap', comparing = false, generation = 0, returnFocus = null;
  let loadTimer = 0, metadataHandler = null;
  let videoAbort = null, videoObjectURL = null, referenceObjectURL = null;
  let pendingTime=0, pendingAutoplay=false;
  let videoLoading = false, referenceRequest = null, bridgeReady = false, bridge = null;
  const bridgeOrigin = 'https://message-motion-originals.orchidhq.chatgpt.site';
  const bridgeRequests = new Map();
  function revokeVideo() { videoAbort?.abort(); videoAbort = null; if (videoObjectURL) URL.revokeObjectURL(videoObjectURL); videoObjectURL=null; videoLoading=false; }
  function releaseReference() {
    if (referenceRequest) { bridge?.contentWindow?.postMessage({type:'cancel',id:referenceRequest},bridgeOrigin); bridgeRequests.delete(referenceRequest); referenceRequest=null; }
    reference.pause();reference.removeAttribute('src');reference.load();
    if (referenceObjectURL) URL.revokeObjectURL(referenceObjectURL);referenceObjectURL=null;
  }
  function ensureBridge() {
    if (bridge) return;
    bridge=document.createElement('iframe');bridge.hidden=true;bridge.title='Original video loader';bridge.src=bridgeOrigin+'/bridge.html';document.body.append(bridge);
  }
  function requestReference() {
    releaseReference(); if (!comparing || !dialog.open) return;
    ensureBridge();const film=currentFilm().id;const id='reference-'+film+'-'+Date.now()+'-'+generation;
    referenceRequest=id;bridgeRequests.set(id,{film});
    if (bridgeReady) bridge.contentWindow.postMessage({type:'load',film,id},bridgeOrigin);
  }
  window.addEventListener('message',event=>{
    if (event.origin!==bridgeOrigin || event.source!==bridge?.contentWindow || !event.data) return;
    const data=event.data;
    if (data.type==='ready') { bridgeReady=true;for (const [id,item] of bridgeRequests) bridge.contentWindow.postMessage({type:'load',id,film:item.film},bridgeOrigin);return; }
    const pending=bridgeRequests.get(data.id);
    if (!pending || data.id!==referenceRequest || pending.film!==currentFilm().id || !comparing || !dialog.open) return;
    bridgeRequests.delete(data.id);referenceRequest=null;
    if (data.type==='loaded' && data.bytes instanceof ArrayBuffer && data.bytes.byteLength<=20*1024*1024) {
      if(referenceObjectURL)URL.revokeObjectURL(referenceObjectURL);
      referenceObjectURL=URL.createObjectURL(new Blob([data.bytes],{type:'video/mp4'}));reference.src=referenceObjectURL;reference.load();
      if(!video.paused)playReference();
    } else if(data.type==='error') showStatus('The original could not be loaded. The recreation can still play.');
  });
  const currentFilm = () => films[activeIndex];
  const el = (tag, className, text) => { const node = document.createElement(tag); if (className) node.className = className; if (text) node.textContent = text; return node; };

  films.forEach((film, index) => {
    const card = el('article', 'film-card');
    card.style.setProperty('--film-color', film.color);
    const button = el('button', 'film-open');
    button.type = 'button';
    button.setAttribute('aria-label', 'Watch ' + film.title);
    const img = el('img'); img.src = film.poster; img.alt = film.title + ', a still from the reconstruction'; img.width = 960; img.height = Math.round(960 * film.height / film.width); img.loading = 'lazy'; img.decoding = 'async';
    const watch = el('span', 'watch-label'); watch.append(el('span', '', '▶'), el('span', '', 'watch film'));
    button.append(img, watch, el('span', 'card-time', formatTime(film.duration)));
    button.addEventListener('click', () => openFilm(index, button));
    const label = el('div', 'film-label'); label.append(el('h3', '', film.title), el('span', 'index', '(' + String(index + 1).padStart(2, '0') + ')'));
    card.append(button, label, el('p', 'card-description', film.description));
    document.getElementById('film-grid').append(card);
  });

  function clearStatus() { status.hidden = true; status.textContent = ''; status.classList.remove('error'); }
  function showStatus(message, error = false) {
    status.replaceChildren(document.createTextNode(message + ' '));
    const direct = el('a', 'text-link', 'open MP4 ↗'); direct.href = currentFilm().methods[activeMethod]; direct.target = '_blank'; direct.rel = 'noopener';
    status.append(direct); status.hidden = false; status.classList.toggle('error', error);
  }
  function updateTime() {
    document.getElementById('time-display').textContent = formatTime(video.currentTime) + ' / ' + formatTime(Number.isFinite(video.duration) ? video.duration : currentFilm().duration);
  }
  function updatePlayButton() {
    playButton.disabled=videoLoading;
    playButton.replaceChildren(document.createTextNode(videoLoading ? 'loading film ' : video.paused ? 'play film ' : 'pause film '));
    const icon = el('span', '', video.paused ? '▶' : 'Ⅱ'); icon.setAttribute('aria-hidden', 'true'); playButton.append(icon);
    playButton.setAttribute('aria-label', (video.paused ? 'Play ' : 'Pause ') + currentFilm().title);
  }
  function syncReference(force = false) {
    if (!comparing || !reference.getAttribute('src') || reference.readyState < 1) return;
    const target = sourceTime(video.currentTime || 0, currentFilm().segments);
    if (force || Math.abs(reference.currentTime - target) > .16) reference.currentTime = clampTime(target, reference.duration);
    reference.playbackRate = video.playbackRate;
  }
  function playReference() {
    if (!comparing || !dialog.open || !reference.getAttribute('src')) return;
    syncReference(true);
    const sequence = generation;
    const attempt = reference.play();
    if (attempt) attempt.catch(error => { if (sequence === generation && comparing && error.name !== 'AbortError') showStatus('The original is paused. Tap its play control to join the comparison.'); });
  }
  function tryPlay() {
    if (videoLoading) return;
    const sequence = generation;
    const attempt = video.play();
    if (attempt) attempt.catch(error => {
      if (sequence !== generation || !dialog.open || error.name === 'AbortError') return;
      showStatus(playbackMessage(error), error.name !== 'NotAllowedError'); updatePlayButton();
    });
  }
  function setMethod(method, {time = videoLoading ? pendingTime : (video.currentTime || 0), autoplay = videoLoading ? pendingAutoplay : !video.paused} = {}) {
    if (!currentFilm().methods[method]) return;
    pendingTime=time;pendingAutoplay=autoplay;
    const sequence = ++generation;
    activeMethod = method; clearStatus(); clearTimeout(loadTimer);
    video.pause(); reference.pause(); revokeVideo();
    if (metadataHandler) video.removeEventListener('loadedmetadata', metadataHandler);
    for (const button of tabs.children) button.setAttribute('aria-pressed', String(button.dataset.method === method));
    document.getElementById('method-name').textContent = labels[method];
    download.href = currentFilm().methods[method]; download.download = currentFilm().id + '-' + method + '.mp4';
    metadataHandler = () => {
      if (sequence !== generation) return;
      clearTimeout(loadTimer);
      video.currentTime = clampTime(time, video.duration > .05 ? video.duration - .05 : video.duration);
      syncReference(true); updateTime();
    };
    video.addEventListener('loadedmetadata', metadataHandler, {once: true});
    video.removeAttribute('src');video.load();videoLoading=true;updatePlayButton();
    showStatus('Loading the film…');
    videoAbort=new AbortController();
    fetch(currentFilm().methods[method],{signal:videoAbort.signal,credentials:'omit'})
      .then(response=>{if(!response.ok || !response.headers.get('content-type')?.startsWith('video/mp4')) throw new Error('Video unavailable');return response.blob();})
      .then(blob=>{
        if(sequence!==generation || !dialog.open)return;
        videoLoading=false;videoObjectURL=URL.createObjectURL(blob);video.src=videoObjectURL;video.load();clearStatus();updatePlayButton();
        if(autoplay)tryPlay();
      })
      .catch(error=>{if(sequence!==generation || !dialog.open || error.name==='AbortError')return;videoLoading=false;updatePlayButton();showStatus('The film could not finish loading. Try again, or open the MP4 directly.',true);});
    loadTimer = setTimeout(() => { if (sequence === generation && dialog.open && video.readyState < 2) showStatus('Still loading. Check your connection, or open the MP4 directly.'); }, 15000);
    updatePlayButton(); updateTime();
    const hash = '#' + currentFilm().id + '/' + method;
    history.replaceState(null, '', hash);
  }
  function configureReference() {
    document.getElementById('reference-panel').hidden = !comparing;
    document.getElementById('players').classList.toggle('comparing', comparing);
    compareButton.setAttribute('aria-pressed', String(comparing));
    compareButton.firstChild.textContent = comparing ? 'hide original ' : 'compare original ';
    if (comparing) {
      requestReference();
    } else { releaseReference(); }
  }
  function openFilm(index, trigger = null, {autoplay = true, method = activeMethod} = {}) {
    activeIndex = (index + films.length) % films.length;
    const film = currentFilm();
    if (trigger) returnFocus = trigger;
    document.getElementById('player-title').textContent = film.title;
    document.getElementById('player-number').textContent = 'film ' + String(activeIndex + 1).padStart(2, '0') + ' / 06';
    document.getElementById('source-link').href = film.sourceUrl;
    document.getElementById('player-description').textContent = film.description + (comparing ? ' Use the recreation controls to scrub both videos.' : ' Switch the animation method above to explore each version.');
    document.getElementById('cut-note').hidden = !film.segments.length;
    video.poster = film.poster; video.muted = false; reference.muted = true;
    tabs.replaceChildren();
    for (const key of Object.keys(labels)) {
      const button = el('button', '', labels[key]); button.type = 'button'; button.dataset.method = key; button.setAttribute('aria-pressed', String(key === method));
      button.addEventListener('click', () => setMethod(key)); tabs.append(button);
    }
    if (!dialog.open) { dialog.showModal(); document.body.classList.add('viewer-open'); }
    configureReference(); setMethod(method, {time: 0, autoplay});
  }
  function closeFilm() { dialog.close(); }
  dialog.addEventListener('close', () => {
    ++generation; clearTimeout(loadTimer); video.pause(); reference.pause();revokeVideo();releaseReference();
    video.removeAttribute('src'); reference.removeAttribute('src'); video.load(); reference.load();
    if (metadataHandler) video.removeEventListener('loadedmetadata', metadataHandler);
    document.body.classList.remove('viewer-open'); history.replaceState(null, '', '#films');
    if (returnFocus?.isConnected) returnFocus.focus({preventScroll: true});
  });
  document.getElementById('close-player').addEventListener('click', closeFilm);
  dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) closeFilm(); } });
  playButton.addEventListener('click', () => { if (!video.getAttribute('src') || video.error) { setMethod(activeMethod, {time: video.currentTime || 0, autoplay: true}); return; } if (video.paused) tryPlay(); else video.pause(); });
  document.getElementById('restart').addEventListener('click', () => { video.currentTime = 0; syncReference(true); tryPlay(); });
  document.getElementById('previous-film').addEventListener('click', () => openFilm(activeIndex - 1));
  document.getElementById('next-film').addEventListener('click', () => openFilm(activeIndex + 1));
  compareButton.addEventListener('click', () => {
    comparing = !comparing; configureReference();
    document.getElementById('player-description').textContent = currentFilm().description + (comparing ? ' Use the recreation controls to scrub both videos.' : ' Switch the animation method above to explore each version.');
  });
  video.addEventListener('play', () => { updatePlayButton(); playReference(); });
  video.addEventListener('playing', () => { clearStatus(); clearTimeout(loadTimer); updatePlayButton(); });
  video.addEventListener('pause', () => { reference.pause(); updatePlayButton(); });
  video.addEventListener('ended', () => { reference.pause(); updatePlayButton(); });
  video.addEventListener('seeking', () => syncReference(true));
  video.addEventListener('seeked', () => { syncReference(true); if (!video.paused) playReference(); });
  video.addEventListener('ratechange', () => { reference.playbackRate = video.playbackRate; });
  video.addEventListener('timeupdate', () => { updateTime(); if (!video.paused) syncReference(); });
  video.addEventListener('error', () => { if (!dialog.open || !video.getAttribute('src')) return; clearTimeout(loadTimer); showStatus(playbackMessage(video.error), true); updatePlayButton(); });
  reference.addEventListener('loadedmetadata', () => { syncReference(true); if (!video.paused) playReference(); });
  reference.addEventListener('error', () => { if (comparing && dialog.open && reference.getAttribute('src')) showStatus('The original could not be loaded. The recreation can still play.'); });
  const requested = location.hash.slice(1).split('/');
  const initialIndex = films.findIndex(film => film.id === requested[0]);
  if (initialIndex >= 0) openFilm(initialIndex, null, {autoplay: false, method: labels[requested[1]] ? requested[1] : 'gsap'});
})();
