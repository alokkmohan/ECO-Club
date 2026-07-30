const fmt = n => n.toLocaleString('en-IN');

function getParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

function setParam(name, value) {
  const url = new URL(window.location.href);
  if (value) url.searchParams.set(name, value);
  else url.searchParams.delete(name);
  window.history.replaceState({}, '', url);
}

async function loadJSON(path) {
  const bust = path.includes('?') ? '&' : '?';
  const res = await fetch(`${path}${bust}v=${Date.now()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json();
}

function populateDistricts(selectEl, districts, selected) {
  selectEl.innerHTML = '<option value="">All Districts</option>' +
    districts.map(d => `<option value="${d}">${titleCase(d)}</option>`).join('');
  if (selected) selectEl.value = selected;
}

function titleCase(s) {
  return String(s).toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
}

(function () {
  document.querySelectorAll('.nav-dropdown > .dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', e => {
      if (window.matchMedia('(hover: hover)').matches) return;
      e.preventDefault();
      toggle.closest('.nav-dropdown').classList.toggle('open');
    });
  });
  document.addEventListener('click', e => {
    document.querySelectorAll('.nav-dropdown.open').forEach(d => {
      if (!d.contains(e.target)) d.classList.remove('open');
    });
  });
})();

(function () {
  const el = document.getElementById('visitCounter');
  if (!el) return;
  // Some ad-blocker / privacy-extension builds replace window.fetch with a stub
  // that returns a Promise which never settles (ignoring AbortSignal entirely),
  // which would otherwise leave this stuck on "Loading visits..." forever.
  // Racing against an independent timer guarantees we always move past it.
  const hardTimeout = new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000));
  Promise.race([
    fetch('https://api.counterapi.dev/v1/ecoclubup-dataimpact-in/visits/up').then(r => r.json()),
    hardTimeout,
  ])
    .then(d => { el.textContent = `${d.count.toLocaleString('en-IN')} visits`; })
    .catch(() => { el.remove(); });
})();
