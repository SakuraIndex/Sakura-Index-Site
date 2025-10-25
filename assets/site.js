// assets/site.js
(function(){
  const cacheBust = () => `?v=${Date.now()}`;

  // 時間軸ボタンで画像切替
  document.querySelectorAll('[data-chart]').forEach(card=>{
    const img = card.querySelector('img.chart');
    const buttons = card.querySelectorAll('[data-src]');
    buttons.forEach(btn=>{
      btn.addEventListener('click',()=>{
        buttons.forEach(b=>b.classList.remove('active'));
        btn.classList.add('active');
        const src = btn.getAttribute('data-src');
        if(src){
          img.src = src + cacheBust();
        }
      });
    });
  });

  // 画像フォールバック（intraday → AM → 最後に「no image」）
  document.querySelectorAll('img.chart').forEach(img=>{
    const fallbacks = (img.dataset.fallback || '').split('|').filter(Boolean);
    let i = 0;
    img.addEventListener('error', ()=>{
      if(i < fallbacks.length){
        img.src = fallbacks[i++] + cacheBust();
      }else{
        // 何も無ければダミー
        img.src = `data:image/svg+xml;utf8,` + encodeURIComponent(
          `<svg xmlns='http://www.w3.org/2000/svg' width='900' height='260'>
             <rect width='100%' height='100%' fill='#0b1119'/>
             <text x='50%' y='50%' fill='#7c8da3' font-size='16' text-anchor='middle'>chart (no image)</text>
           </svg>`
        );
      }
    }, {once:false});
  });
})();
