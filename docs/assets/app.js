(function() {
  const saved = localStorage.getItem('scriptpedia_lang') || 'id';
  function applyLang(lang) {
    localStorage.setItem('scriptpedia_lang', lang);
    document.querySelectorAll('[data-id][data-en]').forEach(el => {
      el.textContent = lang === 'en' ? el.dataset.en : el.dataset.id;
    });
    document.querySelectorAll('.lang-toggle button').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
  }
  document.querySelectorAll('.lang-toggle button').forEach(btn => {
    btn.addEventListener('click', () => applyLang(btn.dataset.lang));
  });
  applyLang(saved);

  // Web Speech helper
  window.speakScript = function(text, lang) {
    if (!('speechSynthesis' in window) || !text) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang || 'en-US';
    u.rate = 0.85;
    window.speechSynthesis.speak(u);
  };

  // Search + filter
  const searchInput = document.getElementById('searchInput');
  const filterButtons = document.querySelectorAll('.filter-pills button');
  let activeType = 'all';
  function runFilter() {
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    document.querySelectorAll('[data-searchable]').forEach(card => {
      const hay = card.dataset.searchable.toLowerCase();
      const t = card.dataset.type || card.dataset.group || 'all';
      const okType = activeType === 'all' || t === activeType;
      const okQ = !q || hay.includes(q);
      card.style.display = (okType && okQ) ? '' : 'none';
    });
    // Hide empty group sections
    document.querySelectorAll('.group-block').forEach(sec => {
      const visible = sec.querySelectorAll('[data-searchable]:not([style*="display: none"])').length;
      sec.style.display = visible > 0 ? '' : 'none';
    });

    // Global homepage cross-script search
    const globalBox = document.getElementById('globalResults');
    if (globalBox && window.SCRIPTPEDIA_INDEX) {
      if (q.length < 1) { globalBox.innerHTML = ''; return; }
      const hits = window.SCRIPTPEDIA_INDEX.filter(it => it.s.includes(q)).slice(0, 12);
      if (!hits.length) { globalBox.innerHTML = ''; return; }
      globalBox.innerHTML = '<div class="glyph-grid">' + hits.map(h =>
        `<a class="glyph-card" href="scripts/${h.slug}.html?q=${encodeURIComponent(h.g)}">` +
        `<div class="glyph-big">${h.g}</div>` +
        `<div class="glyph-reading">${h.r} · ${h.slug}</div>` +
        `<div class="glyph-meaning">${(localStorage.getItem('scriptpedia_lang')==='en'?h.en:h.id)}</div></a>`
      ).join('') + '</div>';
    }
  }
  if (searchInput) {
    searchInput.addEventListener('input', runFilter);
    const params = new URLSearchParams(window.location.search);
    if (params.get('q')) { searchInput.value = params.get('q'); runFilter(); }
  }
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      activeType = btn.dataset.filter;
      filterButtons.forEach(b => b.classList.toggle('active', b === btn));
      runFilter();
    });
  });

  // Stroke-order SVG animator
  let animTimer = null;
  async function renderStrokes(d) {
    const stage = document.getElementById('mStrokeStage');
    const btn = document.getElementById('mReplayStroke');
    if (!stage) return;
    if (animTimer) { clearInterval(animTimer); animTimer = null; }
    stage.innerHTML = '';
    stage.style.display = 'none';
    if (btn) btn.style.display = 'none';

    if (d.stroke_json) {
      try {
        const res = await fetch(d.stroke_json);
        if (!res.ok) return;
        const data = await res.json();
        const radSet = new Set(data.radStrokes || []);
        stage.style.display = 'flex';
        if (btn) btn.style.display = 'inline-block';
        const svgNS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(svgNS, 'svg');
        svg.setAttribute('viewBox', '0 0 1024 1024');
        const g = document.createElementNS(svgNS, 'g');
        g.setAttribute('transform', 'scale(1, -1) translate(0, -900)');
        const paths = data.strokes.map((p, idx) => {
          const path = document.createElementNS(svgNS, 'path');
          path.setAttribute('d', p);
          path.setAttribute('fill', radSet.has(idx) ? '#C85A32' : '#1E2D4A');
          path.style.opacity = '0.15';
          path.style.transition = 'opacity 0.2s ease';
          g.appendChild(path);
          return path;
        });
        svg.appendChild(g);
        stage.appendChild(svg);
        const play = () => {
          if (animTimer) clearInterval(animTimer);
          paths.forEach(p => p.style.opacity = '0.12');
          let i = 0;
          animTimer = setInterval(() => {
            if (i >= paths.length) { clearInterval(animTimer); return; }
            paths[i].style.opacity = '1';
            i++;
          }, 380);
        };
        play();
        if (btn) btn.onclick = play;
      } catch (_) {}
    } else if (d.kana_svg) {
      try {
        const res = await fetch(d.kana_svg);
        if (!res.ok) return;
        const txt = await res.text();
        stage.style.display = 'flex';
        stage.innerHTML = txt;
        const svg = stage.querySelector('svg');
        if (svg) {
          svg.style.width = '88%'; svg.style.height = '88%';
          const paths = Array.from(svg.querySelectorAll('path'));
          paths.forEach(p => { p.style.stroke = '#1E2D4A'; p.style.strokeWidth = '5'; });
          if (btn) {
            btn.style.display = 'inline-block';
            const play = () => {
              if (animTimer) clearInterval(animTimer);
              paths.forEach(p => { p.style.stroke = '#DDD3C0'; });
              let i = 0;
              animTimer = setInterval(() => {
                if (i >= paths.length) { clearInterval(animTimer); return; }
                paths[i].style.stroke = '#C85A32';
                i++;
              }, 420);
            };
            play();
            btn.onclick = play;
          }
        }
      } catch (_) {}
    }
  }

  const modal = document.getElementById('entryModal');
  if (modal) {
    let currentEntry = null;
    document.querySelectorAll('.glyph-card').forEach(card => {
      card.addEventListener('click', () => {
        const d = JSON.parse(card.dataset.entry);
        currentEntry = d;
        const lang = localStorage.getItem('scriptpedia_lang') || 'id';
        document.getElementById('mGlyph').textContent = d.glyph;
        document.getElementById('mReading').textContent = d.reading + (d.zhuyin ? ' · ' + d.zhuyin : '');
        document.getElementById('mMeaning').textContent = lang === 'en' ? d.meaning_en : d.meaning_id;
        document.getElementById('mTts').textContent = lang === 'en' ? d.tts_en : d.tts_id;
        document.getElementById('mPrompt').textContent = d.image_prompt || '-';
        const media = document.getElementById('mMedia');
        media.innerHTML = '';
        const vid = lang === 'en' ? (d.video_en || d.video_id) : (d.video_id || d.video_en);
        if (vid) {
          media.innerHTML = `<video controls playsinline preload="metadata" src="${vid}"></video>`;
        } else if (d.template_rel) {
          media.innerHTML = `<img alt="${d.glyph}" src="${d.template_rel}" loading="lazy">`;
        }
        renderStrokes(d);
        modal.showModal();
      });
    });
    document.getElementById('mSpeak').addEventListener('click', () => {
      if (currentEntry) window.speakScript(currentEntry.speak_text, currentEntry.speech_lang);
    });
    document.getElementById('mCopyPrompt').addEventListener('click', () => {
      if (currentEntry && navigator.clipboard) navigator.clipboard.writeText(currentEntry.image_prompt || '');
    });
    document.getElementById('mClose').addEventListener('click', () => modal.close());
  }
})();
