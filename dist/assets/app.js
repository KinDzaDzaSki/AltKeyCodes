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
  function tile(s){return '<button class="sym" data-copy="'+escapeHtml(s.glyph)+'" data-href="'+symbolUrl(s)+'" aria-label="Copy '+escapeHtml(s.name)+'"><span class="g" aria-hidden="true">'+escapeHtml(s.glyph)+'</span><span class="n">'+escapeHtml(s.name)+'</span><span class="c">'+escapeHtml(primaryCode(s))+'</span></button>';}
  function showStatus(msg){const st=document.getElementById('copy-status');if(!st)return;st.textContent=msg;st.classList.add('show');setTimeout(()=>st.classList.remove('show'),1600);}
  function fallbackCopy(t){const a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.left='-9999px';document.body.appendChild(a);a.select();try{document.execCommand('copy');return true;}catch(e){return false;}finally{a.remove();}}
  async function copy(t,name){try{if(navigator.clipboard&&navigator.clipboard.writeText){await navigator.clipboard.writeText(t);}else if(!fallbackCopy(t))throw new Error('copy failed');}catch(e){showStatus('Copy failed');return;}const label=name||'Value';showStatus(label+' copied');saveRecent(t);renderRecent();}
  function saveRecent(glyph){let r=JSON.parse(localStorage.getItem(RECENT)||'[]');r=r.filter(x=>x!==glyph);r.unshift(glyph);r=r.slice(0,12);localStorage.setItem(RECENT,JSON.stringify(r));}
  function renderRecent(){if(!recentGrid)return;const r=JSON.parse(localStorage.getItem(RECENT)||'[]');if(!r.length){recentEl&&(recentEl.hidden=true);return;}recentEl&&(recentEl.hidden=false);recentGrid.innerHTML=r.map(g=>{const s=symbols.find(x=>x.glyph===g);return s?tile(s):'<button class="sym" data-copy="'+escapeHtml(g)+'" aria-label="Copy character"><span class="g" aria-hidden="true">'+escapeHtml(g)+'</span></button>';}).join('');}

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
  document.addEventListener('keydown',e=>{if(!resultsEl||!['ArrowDown','ArrowUp','Enter','Escape'].includes(e.key))return;const btns=Array.from(resultsEl.querySelectorAll('.sym'));if(e.key==='Escape'){if(input){input.value='';input.blur();doSearch();}return;}if(!btns.length)return;if(e.key==='Enter'&&focused>=0&&focused<btns.length){e.preventDefault();copy(btns[focused].dataset.copy,btns[focused].querySelector('.n')?.textContent);return;}if(e.key==='ArrowDown'){e.preventDefault();focused=Math.min(focused+1,btns.length-1);btns[focused]?.focus();}else if(e.key==='ArrowUp'){e.preventDefault();focused=Math.max(focused-1,-1);if(focused>=0)btns[focused]?.focus();else input?.focus();}});
  document.addEventListener('click',e=>{const b=e.target.closest('.sym,[data-copy]');if(!b)return;const text=b.dataset.copy||b.textContent;const name=b.querySelector('.n')?.textContent||b.closest('.sym')?.querySelector('.n')?.textContent;if(text)copy(text,name);const href=b.dataset.href;if(href&&!b.classList.contains('sym'))location.href=href;else if(href&&e.shiftKey===false&&e.ctrlKey===false&&e.metaKey===false){window.location.href=href;}});

  fetch('/assets/symbols.json').then(r=>r.json()).then(data=>{symbols=data;doSearch();renderRecent();}).catch(()=>{if(resultsEl&&resultsEl.children.length===0)resultsEl.innerHTML='<p class="noscript-notice">Could not load search index.</p>';});
})();
