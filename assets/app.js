(function(){
  'use strict';
  const KEY='altkeycodes-theme';
  const RECENT='altkeycodes-recent';
  const root=document.documentElement;
  const toggle=document.getElementById('theme-toggle');
  function setTheme(t){root.setAttribute('data-theme',t);localStorage.setItem(KEY,t);}
  function initTheme(){const saved=localStorage.getItem(KEY);const sys=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';setTheme(saved||sys);}
  if(toggle){toggle.addEventListener('click',()=>{setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark');});}
  initTheme();

  const input=document.getElementById('q');
  const resultsEl=document.getElementById('results');
  const groupFilter=document.getElementById('group-filter');
  const hasAlt=document.getElementById('has-alt');
  const hasOption=document.getElementById('has-option');
  const countEl=document.getElementById('result-count');
  const recentEl=document.getElementById('recent-copied');
  const recentGrid=document.getElementById('recent-grid');
  let symbols=[],debounce;

  function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function slugify(n){return n.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');}
  function symbolUrl(s){return '/symbol/'+s.id+'-'+slugify(s.name)+'/';}
  function primaryCode(s){if(s.alt_legacy&&s.alt_legacy.length)return 'Alt+'+s.alt_legacy[0];if(s.alt_decimal)return 'Alt+'+s.alt_decimal;if(s.mac_option)return s.mac_option;return s.unicode;}
  function tile(s){return '<div class="sym"><button type="button" class="sym-copy" data-copy="'+escapeHtml(s.glyph)+'" data-label="'+escapeHtml(s.name)+'" aria-label="Copy '+escapeHtml(s.name)+'"><span class="g" aria-hidden="true">'+escapeHtml(s.glyph)+'</span></button><a class="sym-name" href="'+symbolUrl(s)+'">'+escapeHtml(s.name)+'</a><span class="c">'+escapeHtml(primaryCode(s))+'</span></div>';}
  function showStatus(msg){const st=document.getElementById('copy-status');if(!st)return;st.textContent=msg;st.classList.add('show');setTimeout(()=>st.classList.remove('show'),1600);}
  function fallbackCopy(t){const a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.left='-9999px';document.body.appendChild(a);a.select();try{document.execCommand('copy');return true;}catch(e){return false;}finally{a.remove();}}
  async function copy(t,name){try{if(navigator.clipboard&&navigator.clipboard.writeText){await navigator.clipboard.writeText(t);}else if(!fallbackCopy(t))throw new Error('copy failed');}catch(e){showStatus('Copy failed');return;}const label=name||'Value';showStatus(label+' copied');saveRecent(t);renderRecent();}
  function saveRecent(glyph){let r=JSON.parse(localStorage.getItem(RECENT)||'[]');r=r.filter(x=>x!==glyph);r.unshift(glyph);r=r.slice(0,12);localStorage.setItem(RECENT,JSON.stringify(r));}
  function renderRecent(){if(!recentGrid)return;const r=JSON.parse(localStorage.getItem(RECENT)||'[]');if(!r.length){recentEl&&(recentEl.hidden=true);return;}recentEl&&(recentEl.hidden=false);recentGrid.innerHTML=r.map(g=>{const s=symbols.find(x=>x.glyph===g);return s?tile(s):'<button type="button" class="sym-copy" data-copy="'+escapeHtml(g)+'" data-label="character" aria-label="Copy character"><span class="g" aria-hidden="true">'+escapeHtml(g)+'</span></button>';}).join('');}

  function score(s,q){const lq=q.toLowerCase();if(s.glyph===q)return 1000;if(s.aliases&&s.aliases.some(a=>a.toLowerCase()===lq))return 900;if(s.name.toLowerCase()===lq)return 850;const aliasPrefix=s.aliases&&s.aliases.some(a=>a.toLowerCase().startsWith(lq));const namePrefix=s.name.toLowerCase().startsWith(lq);if(aliasPrefix)return 800;if(namePrefix)return 750;const aliasSub=s.aliases&&s.aliases.some(a=>a.toLowerCase().includes(lq));const nameSub=s.name.toLowerCase().includes(lq);if(aliasSub)return 600;if(nameSub)return 550;if(String(s.codepoint)===q||s.unicode.toLowerCase()===lq.replace(/u\+/,'')||s.id.toLowerCase()===lq.replace(/u\+/,'u'))return 500;if(s.alt_legacy&&s.alt_legacy.includes(q))return 500;if(s.alt_decimal===q)return 500;return 0;}
  function filterList(q){const g=groupFilter?groupFilter.value:'';const a=hasAlt?hasAlt.checked:false;const o=hasOption?hasOption.checked:false;return symbols.filter(s=>{if(g&&!s.groups.includes(g))return false;if(a&&!(s.alt_legacy&&s.alt_legacy.length))return false;if(o&&!s.mac_option)return false;return score(s,q)>0;}).sort((x,y)=>{const sx=score(x,q),sy=score(y,q);if(sx!==sy)return sy-sx;if(y.weight!==x.weight)return y.weight-x.weight;return x.codepoint-y.codepoint;});}
  function renderResults(list){const total=list.length;const show=list.slice(0,200);if(countEl)countEl.textContent=total+' result'+(total!==1?'s':'');if(resultsEl)resultsEl.innerHTML=show.map(tile).join('')+(total>200?'<p class="result-count" style="grid-column:1/-1;margin-top:8px;">Showing 200 of '+total+'</p>':'');}
  function doSearch(){const q=input?input.value.trim():'';if(!q){renderResults(symbols.slice(0,240));if(countEl)countEl.textContent=symbols.length+' symbols';return;}renderResults(filterList(q));}

  if(input){input.addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(doSearch,90);});}
  if(groupFilter)groupFilter.addEventListener('change',doSearch);
  if(hasAlt)hasAlt.addEventListener('change',doSearch);
  if(hasOption)hasOption.addEventListener('change',doSearch);
  document.addEventListener('keydown',e=>{const tag=e.target.tagName;if((e.key==='/'||((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'))&&tag!=='INPUT'&&tag!=='TEXTAREA'&&tag!=='SELECT'){e.preventDefault();input&&input.focus();}});
  let focused=-1;
  document.addEventListener('keydown',e=>{if(!resultsEl||!['ArrowDown','ArrowUp','Enter','Escape'].includes(e.key))return;const btns=Array.from(resultsEl.querySelectorAll('.sym-copy'));if(e.key==='Escape'){if(input){input.value='';input.blur();doSearch();}return;}if(!btns.length)return;if(e.key==='Enter'&&focused>=0&&focused<btns.length){e.preventDefault();const t=btns[focused].querySelector('[data-copy]');if(t)copy(t.dataset.copy,t.dataset.label);return;}if(e.key==='ArrowDown'){e.preventDefault();focused=Math.min(focused+1,btns.length-1);btns[focused]?.focus();}else if(e.key==='ArrowUp'){e.preventDefault();focused=Math.max(focused-1,-1);if(focused>=0)btns[focused]?.focus();else input?.focus();}});
  // Copy only. Navigation belongs to the .sym-name link, so a click never
  // destroys the result list the user is working through.
  document.addEventListener('click',e=>{
    const b=e.target.closest('[data-copy]');
    if(!b)return;
    const text=b.dataset.copy;
    if(!text)return;
    const label=b.dataset.label||b.closest('.sym')?.querySelector('.sym-name')?.textContent||'Value';
    copy(text,label);
  });

  fetch('/assets/symbols.json').then(r=>r.json()).then(data=>{symbols=data;doSearch();renderRecent();}).catch(()=>{if(resultsEl&&resultsEl.children.length===0)resultsEl.innerHTML='<p class="noscript-notice">Could not load search index.</p>';});

  // Hamburger menu (mobile). Progressive enhancement: with JS off the nav stays
  // visible and wraps, because the dropdown rules are scoped to .js.
  const navHeader=document.querySelector('.site-header');
  const navToggle=document.getElementById('nav-toggle');
  if(navHeader){
    if(navToggle){
      const setNav=o=>{if(o)navHeader.setAttribute('data-nav-open','');else navHeader.removeAttribute('data-nav-open');navToggle.setAttribute('aria-expanded',String(!!o));navToggle.setAttribute('aria-label',o?'Close menu':'Open menu');};
      navToggle.addEventListener('click',()=>setNav(!navHeader.hasAttribute('data-nav-open')));
      document.addEventListener('keydown',e=>{if(e.key==='Escape'&&navHeader.hasAttribute('data-nav-open')){setNav(false);navToggle.focus();}});
      document.addEventListener('click',e=>{if(navHeader.hasAttribute('data-nav-open')&&!navHeader.contains(e.target))setNav(false);});
      Array.prototype.forEach.call(navHeader.querySelectorAll('.site-nav a'),a=>a.addEventListener('click',()=>setNav(false)));
      addEventListener('resize',()=>{if(innerWidth>=840)setNav(false);});
    }
    // Drive the sticky search panel offset from the measured header height, so a
    // taller header (zoom, font swap, wrap) can never clip the search input.
    let lastHeaderH=0;
    const syncHeader=()=>{
      const h=navHeader.offsetHeight;
      if(h&&h!==lastHeaderH){lastHeaderH=h;root.style.setProperty('--header-h',h+'px');}
    };
    syncHeader();
    addEventListener('resize',syncHeader);
    addEventListener('orientationchange',syncHeader);
    addEventListener('load',syncHeader);
    requestAnimationFrame(syncHeader);
    // The header's height changes after the font swap and after the first layout,
    // so a one-shot read leaves --header-h a pixel or two short and the sticky
    // search panel clips. ResizeObserver keeps it exact for the whole session.
    if(window.ResizeObserver){new ResizeObserver(syncHeader).observe(navHeader);}
    if(document.fonts&&document.fonts.ready)document.fonts.ready.then(syncHeader);
  }
})();
