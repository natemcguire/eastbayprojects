const header = document.querySelector('.ebp-header');
const menu = document.querySelector('.ebp-menu');
const mobile = document.querySelector('.ebp-mobile');
function closeMenu() {
  mobile.hidden = true;
  menu.setAttribute('aria-expanded', 'false');
  menu.setAttribute('aria-label', 'Open navigation');
}
menu.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  mobile.hidden = !open;
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});
mobile.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !mobile.hidden) { closeMenu(); menu.focus(); }
});
window.addEventListener('scroll', () => header.classList.toggle('scrolled', scrollY > 20), {passive: true});
document.querySelectorAll('.ebp-links a').forEach(link => {
  if (link.pathname === location.pathname && !link.hash) link.setAttribute('aria-current', 'page');
});
const words = ['CIVIC & CAMPAIGNS', 'ROOFING CONTRACTORS', 'PUBLIC ORGANIZATIONS', 'HVAC COMPANIES', 'LAW FIRMS', 'DEFENSE CONTRACTORS', 'COMMUNITY COALITIONS', 'MEDICAL PRACTICES'];
const typewriter = document.querySelector('#tw-word');
if (typewriter && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  let index = 0, character = words[0].length, deleting = true;
  function type() {
    if (deleting) {
      typewriter.textContent = words[index].slice(0, --character);
      if (character === 0) { deleting = false; index = (index + 1) % words.length; setTimeout(type, 350); return; }
    } else {
      typewriter.textContent = words[index].slice(0, ++character);
      if (character === words[index].length) { deleting = true; setTimeout(type, 2200); return; }
    }
    setTimeout(type, deleting ? 40 : 70);
  }
  setTimeout(type, 2200);
}
const project = new URLSearchParams(location.search).get('project');
document.querySelectorAll('[data-role-interest]').forEach(link => link.addEventListener('click', () => {
  document.querySelector('#career-role').value = link.dataset.roleInterest;
}));
if (project === 'civic') {
  const select = document.querySelector('#project-type');
  if (select) select.value = 'Civic or campaign digital';
}
// Test site only: no submission, draft creation, analytics, or inquiry storage.
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', event => {
    event.preventDefault();
    const status = form.querySelector('.preview-status');
    status.hidden = false;
    status.textContent = 'Preview complete. Nothing was sent or stored.';
  });
  form.removeAttribute('inert');
});
