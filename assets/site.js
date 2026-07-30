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

// This file is included near the top of each page, before the nav and footer
// elements exist, so all DOM lookups must wait for DOMContentLoaded.
function onDomReady(fn) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fn);
  } else {
    fn();
  }
}

onDomReady(function () {
  // Wrapped defensively so a DOM/API quirk here can never block the rest of
  // this script file (e.g. the visit counter below) from running.
  try {
    document.querySelectorAll('.nav-dropdown > .dropdown-toggle').forEach(toggle => {
      toggle.addEventListener('click', e => {
        if (window.matchMedia && window.matchMedia('(hover: hover)').matches) return;
        e.preventDefault();
        toggle.closest('.nav-dropdown').classList.toggle('open');
      });
    });
    document.addEventListener('click', e => {
      document.querySelectorAll('.nav-dropdown.open').forEach(d => {
        if (!d.contains(e.target)) d.classList.remove('open');
      });
    });
  } catch (err) { /* non-critical UI enhancement */ }
});

onDomReady(function () {
  const el = document.getElementById('visitCounter');
  if (!el) return;
  // Belt-and-suspenders against every failure mode we've seen:
  //  - old/locked-down browsers without fetch()/Promise -> skip immediately
  //  - fetch() throwing synchronously (some enterprise/proxy setups) -> try/catch
  //  - a stub fetch() whose Promise never settles -> race against a hard timer
  //  - any network/JSON error -> normal .catch()
  // Whatever happens, this always ends with either a number or the element gone
  // within ~5 seconds - never stuck on "Loading visits..." forever.
  if (typeof fetch !== 'function' || typeof Promise !== 'function') {
    el.remove();
    return;
  }
  try {
    const hardTimeout = new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000));
    Promise.race([
      fetch('https://api.counterapi.dev/v1/ecoclubup-dataimpact-in/visits/up').then(r => r.json()),
      hardTimeout,
    ])
      .then(d => { el.textContent = `${d.count.toLocaleString('en-IN')} visits`; })
      .catch(() => { el.remove(); });
  } catch (err) {
    el.remove();
  }
});
