// Auto-dismiss and close behavior for flash messages
(function(){
  const TIMEOUT = 3500;
  document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.flash-container .msg-box').forEach(function(box){
      let dismissed = false;
      let timer = null;
      const startTimer = function(){ timer = setTimeout(()=> closeBox(), TIMEOUT); };
      const clearTimer = function(){ if(timer){ clearTimeout(timer); timer = null; } };
      const closeBox = function(){ if(dismissed) return; dismissed = true; box.style.opacity = '0'; box.style.maxHeight = '0'; setTimeout(()=> box.remove(), 300); };
      // start
      startTimer();
      box.addEventListener('mouseenter', function(){ clearTimer(); });
      box.addEventListener('mouseleave', function(){ startTimer(); });
      const btn = box.querySelector('.msg-close');
      if(btn){ btn.addEventListener('click', function(e){ e.preventDefault(); closeBox(); }); }
    });
  });
})();
// Render toast overlays from window.__FLASH_MESSAGES if provided
(function(){
  function makeToastItem(doc, category, message){
    const item = doc.createElement('div');
    item.className = 'toast-item toast-' + (category || 'info');
    const content = doc.createElement('div');
    content.className = 'toast-content';
    content.textContent = message;
    const btn = doc.createElement('button');
    btn.className = 'toast-close';
    btn.setAttribute('aria-label', 'Dismiss');
    btn.textContent = '×';
    btn.addEventListener('click', function(e){ e.preventDefault(); remove(); });
    item.appendChild(content);
    item.appendChild(btn);
    function remove(){ if(item._removed) return; item._removed = true; item.classList.add('toast-hidden'); setTimeout(()=> item.remove(), 300); }
    // auto dismiss
    let timer = setTimeout(remove, 3500);
    item.addEventListener('mouseenter', ()=> clearTimeout(timer));
    item.addEventListener('mouseleave', ()=> timer = setTimeout(remove, 2000));
    return item;
  }

  document.addEventListener('DOMContentLoaded', function(){
    const msgs = window.__FLASH_MESSAGES;
    if(!msgs || !msgs.length) return;
    let container = document.querySelector('.toast-container');
    if(!container){ container = document.createElement('div'); container.className = 'toast-container'; document.body.appendChild(container); }
    msgs.forEach(function(m, idx){
      // m is [category, message]
      let category = 'info', message = '';
      if(Array.isArray(m)) { category = m[0] || 'info'; message = m[1] || ''; }
      else if(m && typeof m === 'object'){ category = m[0] || m.category || 'info'; message = m[1] || m.message || '' }
      const item = makeToastItem(document, category, message);
      // start hidden to allow CSS transition
      item.classList.add('toast-enter', 'toast-hidden');
      container.appendChild(item);
      // stagger entrance slightly
      setTimeout(()=>{
        item.classList.remove('toast-hidden');
        item.classList.add('toast-enter-active');
        // remove enter classes after transition
        setTimeout(()=>{ item.classList.remove('toast-enter', 'toast-enter-active'); }, 300);
      }, 50 * idx);
    });
  });
})();
