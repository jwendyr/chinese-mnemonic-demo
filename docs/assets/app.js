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

  const searchInput = document.getElementById('searchInput');
  const filterButtons = document.querySelectorAll('.filter-pills button');
  let activeType = 'all';
  function runFilter() {
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    document.querySelectorAll('[data-searchable]').forEach(card => {
      const hay = card.dataset.searchable.toLowerCase();
      const t = card.dataset.type || 'all';
      const okType = activeType === 'all' || t === activeType;
      const okQ = !q || hay.includes(q);
      card.style.display = (okType && okQ) ? '' : 'none';
    });
  }
  if (searchInput) searchInput.addEventListener('input', runFilter);
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      activeType = btn.dataset.filter;
      filterButtons.forEach(b => b.classList.toggle('active', b === btn));
      runFilter();
    });
  });

  const modal = document.getElementById('entryModal');
  if (modal) {
    document.querySelectorAll('.glyph-card').forEach(card => {
      card.addEventListener('click', () => {
        const d = JSON.parse(card.dataset.entry);
        const lang = localStorage.getItem('scriptpedia_lang') || 'id';
        document.getElementById('mGlyph').textContent = d.glyph;
        document.getElementById('mReading').textContent = d.reading;
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
        modal.showModal();
      });
    });
    document.getElementById('mClose').addEventListener('click', () => modal.close());
  }
})();
