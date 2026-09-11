const parameters = new URLSearchParams(location.search);
if (parameters.has('embed')) document.documentElement.classList.add('embedded');
const conceptIds = ['editorial','swiss','commons','fieldnotes','terminal','poster','gallery','blueprint','play','heritage'];
document.querySelector('[data-direction-select]')?.addEventListener('change', event => {
  if (conceptIds.includes(event.target.value)) location.href = `/${event.target.value}/`;
});

// Preview forms stay in the browser: no request, storage, or analytics event.
document.querySelectorAll('.preview-form,[data-preview-form]').forEach(form => {
  form.addEventListener('submit', event => {
    event.preventDefault();
    const status = form.querySelector('.preview-message');
    status.hidden = false;
    status.textContent = 'Preview complete. In the finished site, this would reach our team. Nothing was sent or stored.';
  });
  form.removeAttribute('inert');
});

const briefs = {
  websites: 'PROJECT: A better website\n\nAudience → Your next customer\nApproach → A clear story, fast pages,\n           a useful next step.\nTeam → Design + engineering + delivery',
  software: 'PROJECT: A useful product\n\nAudience → The people doing the work\nApproach → Prototype, test, refine,\n           build the real thing.\nTeam → Design + engineering + delivery',
  civic: 'PROJECT: A civic platform\n\nAudience → Your community\nApproach → Clear information, donations,\n           and ways to get involved.\nTeam → Design + engineering + delivery'
};
document.querySelectorAll('[data-brief]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-brief]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  document.querySelector('[data-brief-output]').textContent = briefs[button.dataset.brief];
}));
const audiences = {
  business: 'Make your digital presence feel as good as the work you do. We bring thoughtful design, senior engineering, and a clear path to launch.',
  founder: 'Turn the idea you keep thinking about into something people can use. We bring product design, senior engineering, and a practical path to launch.',
  civic: 'Bring a public purpose to life. We make clear, useful websites and platforms for campaigns, civic teams, and the people they serve.'
};
document.querySelectorAll('[data-audience]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-audience]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  document.querySelector('[data-audience-copy]').textContent = audiences[button.dataset.audience];
}));
const galleryProjects = [
  ['Seamaphore','01 / Brand & website','seamaphore.webp'],
  ['Brown for Austin','02 / Civic & campaigns','brown-for-austin.webp'],
  ['Austin Tax Rate Election','03 / Civic & public data','austin-tax-election.webp']
];
document.querySelectorAll('[data-gallery]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-gallery]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  const [name, category, image] = galleryProjects[Number(button.dataset.gallery)];
  document.querySelector('[data-gallery-title]').textContent = name;
  document.querySelector('[data-gallery-category]').textContent = category;
  const picture = document.querySelector('[data-gallery-image]');
  picture.src = `/assets/work/${image}`;
  picture.alt = `${name} website`;
}));

// Shortlisting is intentionally local to this browser and contains only direction IDs.
if (document.querySelector('.directions-grid')) {
  let saved = [];
  try { saved = JSON.parse(localStorage.getItem('eastbay-design-shortlist') || '[]'); } catch {}
  const shortlist = new Set(Array.isArray(saved) ? saved.filter(id => conceptIds.includes(id)) : []);
  let picks = [];
  let onlyShortlist = false;
  const update = () => {
    document.querySelectorAll('[data-shortlist]').forEach(button => {
      const selected = shortlist.has(button.dataset.shortlist);
      button.setAttribute('aria-pressed', String(selected));
      button.textContent = selected ? '★' : '☆';
      button.closest('.direction-card').hidden = onlyShortlist && !selected;
    });
    document.querySelector('[data-shortlist-count]').textContent = String(shortlist.size);
    document.querySelector('.shortlist-empty').hidden = !onlyShortlist || shortlist.size > 0;
    document.querySelectorAll('[data-compare-pick]').forEach(button => {
      const selected = picks.includes(button.dataset.comparePick);
      button.setAttribute('aria-pressed', String(selected));
      button.textContent = selected ? '✓ Selected' : '+ Compare';
    });
    document.querySelector('[data-compare-count]').textContent = `${picks.length} / 2`;
    document.querySelector('.compare-launch').disabled = picks.length !== 2;
  };
  document.querySelectorAll('[data-shortlist]').forEach(button => button.addEventListener('click', () => {
    const id = button.dataset.shortlist;
    shortlist.has(id) ? shortlist.delete(id) : shortlist.add(id);
    try { localStorage.setItem('eastbay-design-shortlist', JSON.stringify([...shortlist])); } catch {}
    update();
  }));
  document.querySelector('.shortlist-filter').addEventListener('click', event => {
    onlyShortlist = !onlyShortlist;
    event.currentTarget.setAttribute('aria-pressed', String(onlyShortlist));
    update();
  });
  document.querySelectorAll('[data-compare-pick]').forEach(button => button.addEventListener('click', () => {
    const id = button.dataset.comparePick;
    if (picks.includes(id)) picks = picks.filter(item => item !== id);
    else picks = [...picks.slice(-1), id];
    update();
  }));
  document.querySelector('.compare-launch').addEventListener('click', () => {
    if (picks.length === 2) location.href = `/compare.html?left=${picks[0]}&right=${picks[1]}`;
  });
  update();
}

if (document.querySelector('.compare-grid')) {
  let size = 'desktop';
  const layoutFrames = () => {
    document.querySelectorAll('.frame-stage').forEach(stage => {
      const frame = stage.querySelector('iframe');
      const width = size === 'phone' ? 390 : 1440;
      const scale = Math.min(1, stage.clientWidth / width);
      frame.style.width = `${width}px`;
      frame.style.height = `${Math.ceil(stage.clientHeight / scale)}px`;
      frame.style.transform = `scale(${scale})`;
      frame.style.left = `${Math.max(0, (stage.clientWidth - width * scale) / 2)}px`;
    });
  };
  const selectors = [...document.querySelectorAll('[data-compare-side]')];
  const updateSide = (select, navigate = true) => {
    const side = select.dataset.compareSide;
    const value = conceptIds.includes(select.value) ? select.value : side === 'left' ? 'editorial' : 'swiss';
    const frame = document.querySelector(`[data-frame="${side}"]`);
    frame.src = `/${value}/?embed=1`;
    frame.title = `${side === 'left' ? 'Left' : 'Right'} preview: ${select.selectedOptions[0].textContent}`;
    document.querySelector(`[data-open-side="${side}"]`).href = `/${value}/`;
    if (navigate) {
      const url = new URL(location.href);
      selectors.forEach(item => url.searchParams.set(item.dataset.compareSide, item.value));
      history.replaceState(null, '', url);
    }
    layoutFrames();
  };
  selectors.forEach(select => {
    const requested = parameters.get(select.dataset.compareSide);
    select.value = conceptIds.includes(requested) ? requested : select.dataset.compareSide === 'left' ? 'editorial' : 'swiss';
    updateSide(select, false);
    select.addEventListener('change', () => updateSide(select));
  });
  document.querySelectorAll('[data-frame-size]').forEach(button => button.addEventListener('click', () => {
    size = button.dataset.frameSize;
    document.body.dataset.size = size;
    document.querySelectorAll('[data-frame-size]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    layoutFrames();
  }));
  const observer = new ResizeObserver(layoutFrames);
  document.querySelectorAll('.frame-stage').forEach(stage => observer.observe(stage));
}
