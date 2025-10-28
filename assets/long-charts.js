// /assets/long-charts.js
// .long-card[data-key] 要素に対して、docs/charts/<FOLDER> から 7d/1m/1y を張り付ける。
// last_run.txt を ?v= に使い、キャッシュ更新を担保。

(function () {
  const FOLDER = {
    'ASTRA4': 'ASTRA4',
    'R-BANK9': 'R_BANK9',
    'AIN-10': 'AIN10',
    'AIN10': 'AIN10',
    'S-COIN+': 'S-COIN+'
  };
  const BASE = '/docs/charts';

  async function getText(url){
    try{
      const r = await fetch(url, {cache:'no-cache'});
      if(!r.ok) throw new Error(r.status);
      return (await r.text()).trim();
    }catch(_){ return null; }
  }

  async function hydrate(card){
    const key  = card.dataset.key;           // 例: R-BANK9
    const fold = FOLDER[key] || key;
    const v    = (await getText(`${BASE}/${fold}/last_run.txt`)) || Date.now();

    card.querySelectorAll('img.long-img').forEach(img=>{
      const span = img.dataset.span;         // "7d" | "1m" | "1y"
      const src  = `${BASE}/${fold}/${span}.png?v=${encodeURIComponent(v)}`;
      img.src = src;
      img.alt = `${key} (${span})`;
    });

    const when = await getText(`${BASE}/${fold}/last_run.txt`);
    if (when) {
      const el = card.querySelector('.last-run');
      if (el) el.textContent = new Date(when).toLocaleString('ja-JP');
    }
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    document.querySelectorAll('.long-card[data-key]').forEach(hydrate);
  });
})();
