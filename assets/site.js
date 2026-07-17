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
  const el = document.getElementById('visitCounter');
  if (!el) return;
  fetch('https://api.counterapi.dev/v1/ecoclubup-dataimpact-in/visits/up')
    .then(r => r.json())
    .then(d => { el.textContent = `${d.count.toLocaleString('en-IN')} visits`; })
    .catch(() => { el.remove(); });
})();
