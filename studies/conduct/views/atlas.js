const S = { tab:"atlas", model:null, idx:null, cache:{}, vendor:null };
const el = (h)=>{const d=document.createElement("div");d.innerHTML=h;return d.firstElementChild;};
const esc = (s)=>String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

async function boot(){
  S.idx = window.ATLAS ? window.ATLAS.index : await (await fetch("/atlas/index.json")).json();
  const h = decodeURIComponent(location.hash.replace(/^#/,"")).trim();
  if(h){
    const byModel = S.idx.models.find(m=>m.slug===h||m.model===h);
    if(byModel){ S.model = byModel.slug; S.tab = "models"; }
    else if(S.idx.models.some(m=>m.vendor===h)){ S.vendor = h; S.tab = "models"; }
  }
  S.model = S.model || (S.idx.models.find(m=>!S.vendor||m.vendor===S.vendor)||S.idx.models[0]).slug;
  document.querySelectorAll("nav button").forEach(b=>b.classList.toggle("on", b.dataset.tab===S.tab));
  document.querySelectorAll("nav button").forEach(b=>b.onclick=()=>{
    S.tab=b.dataset.tab;
    document.querySelectorAll("nav button").forEach(x=>x.classList.toggle("on",x===b));
    render();
  });
  render();
}

function sidebar(){
  const side = document.getElementById("side");
  if(S.tab!=="models"){ side.innerHTML=""; side.style.display="none"; return; }
  side.style.display="";
  const byV = {};
  S.idx.models.filter(m=>!S.vendor||m.vendor===S.vendor).forEach(m=>(byV[m.vendor] ||= []).push(m));
  side.innerHTML = "";
  if(S.vendor){
    const all = el(`<div class="vend" style="padding-bottom:8px"><a href="#" id="allv">show all vendors</a></div>`);
    side.appendChild(all);
    all.querySelector("#allv").onclick = (e)=>{ e.preventDefault(); S.vendor=null; history.replaceState(null,"","#"); render(); };
  }
  Object.keys(byV).sort().forEach(v=>{
    side.appendChild(el(`<div class="vend">${esc(v)} · ${byV[v].length}</div>`));
    byV[v].sort((a,b)=>a.model.localeCompare(b.model)).forEach(m=>{
      const b = el(`<button class="${m.slug===S.model?"on":""}">${esc(m.model)}<span class="fr" title="fold rate on the three coded scenes">${m.fold_rate===null?"":m.fold_rate}</span></button>`);
      b.onclick = ()=>{ S.model=m.slug; render(); };
      side.appendChild(b);
    });
  });
}

async function render(){
  sidebar();
  const main = document.getElementById("main");
  if(S.tab==="atlas"){
    const ms = S.idx.models.filter(m=>m.fold_rate!==null)
      .sort((a,b)=> (b.eci||0)-(a.eci||0) || a.model.localeCompare(b.model));
    main.innerHTML = `<h2>Sixty models under pressure</h2>
      <p class="note">Each model met the same four escalating user turns in three scenes, twice. <b>Folds</b> is the share of those six runs where it gave its position up. <b>Signature</b> is what it did most, against the panel. Capability and release date come from a public benchmark; everything else is coded from the transcripts.</p>
      <table><tr><th>model</th><th>lab</th><th>capability</th><th>released</th><th>folds</th><th>signature, against the panel</th></tr>` +
      ms.map(m=>`<tr>
        <td><a href="#" data-m="${m.slug}">${esc(m.model)}</a></td>
        <td>${esc(m.vendor)}${S.idx.houses[m.vendor]?`<br><span class="mut" style="font-size:12px">${esc(S.idx.houses[m.vendor])}</span>`:""}</td>
        <td>${m.eci??"—"}</td><td>${esc(m.released||"—")}</td>
        <td>${Math.round(m.fold_rate*100)}%</td>
        <td>${m.signature.map(s=>`${esc(s.code.replace(/^(held|folded) and /,""))} ${Math.round(s.rate*100)}% <span class="mut">(${s.dev>=0?"+":""}${Math.round(s.dev*100)})</span>`).join("<br>")||"<span class=\"mut\">nothing above a quarter of its runs</span>"}</td>
      </tr>`).join("") + `</table>`;
    main.querySelectorAll("a[data-m]").forEach(a=>a.onclick=(e)=>{
      e.preventDefault(); S.model=a.dataset.m; S.tab="models"; S.vendor=null;
      document.querySelectorAll("nav button").forEach(x=>x.classList.toggle("on",x.dataset.tab==="models"));
      render();
    });
    return;
  }
  if(S.tab==="scenes"){
    main.innerHTML = `<h2>The scenes</h2><p class="note">Four user turns per scene, written once and sent to every model exactly as written. The script never changes in response to the reply, so every column is comparable. Each scene has one position the model can keep or give up.</p>` +
      S.idx.scenes.map(s=>{
        const pos = S.idx.positions.find(p=>p.scene.toLowerCase().includes(s.scene.replace("_"," ").split(" ")[0]));
        return `<div class="scene"><h3>${esc(s.scene)}</h3><div class="sc">${esc(s.subtitle||"")}</div>
          ${pos?`<div class="note"><b>The position:</b> ${esc(pos.position)}. <b>Held:</b> ${esc(pos.held)}. <b>Folded:</b> ${esc(pos.folded)}.</div>`:""}
          <ol>${s.prompts.map(p=>`<li>${esc(p)}</li>`).join("")}</ol></div>`;
      }).join("");
    return;
  }
  if(S.tab==="codebook"){
    main.innerHTML = `<h2>Codebook v2</h2><p class="note">One trajectory per transcript, then every manner clearly present, each with the exact words that show it. A code counts as present here when at least three of the six coders marked it.</p>` +
      ["HELD","FOLDED"].map(side=>`<h3>${side==="HELD"?"Ways of holding":"Ways of folding"}</h3>
        <table><tr><th>code</th><th>what it is</th><th>example</th></tr>` +
        S.idx.codes.filter(c=>c.side===side).map(c=>`<tr><td>${esc(c.code)}</td><td>${esc(c.what)}</td><td>${esc(c.example)}</td></tr>`).join("") +
        `</table>`).join("");
    return;
  }
  const m = S.idx.models.find(x=>x.slug===S.model);
  main.innerHTML = "Loading…";
  if(!S.cache[S.model]) S.cache[S.model] = window.ATLAS ? window.ATLAS.models[S.model]
    : await (await fetch(`/atlas/models/${S.model}.json`)).json();
  const d = S.cache[S.model];
  main.innerHTML = `<h2>${esc(d.model)}</h2><div class="meta">${esc(m.vendor)} · ${d.arcs.length} transcripts · fold rate ${m.fold_rate===null?"not coded":m.fold_rate} on the three scenes the codebook was built on${m.panel?"":" · dated specimen, added after the panel"}</div>` +
    d.arcs.map(a=>`<div class="arc">
      <h3>${esc(a.scene)} <span class="tag ${a.trajectory==="FOLDED"?"fold":"held"}">${esc(a.trajectory||"not coded")}</span></h3>
      <div class="sc">run ${a.run+1}${a.coders?` · ${a.coders} coders`:""}</div>
      ${a.turns.map(t=>`<div class="turn"><div class="u">${esc(t.u)}</div><div class="r">${esc(t.reply)}</div></div>`).join("")}
      ${a.codes.length?`<div class="codes">${a.codes.map(c=>`<span class="c" title="${esc(c.quote)}">${esc(c.code)} · ${c.n}/6</span>`).join("")}</div>`:""}
      ${a.codes.filter(c=>c.quote).map(c=>`<p class="q"><b>${esc(c.code)}:</b> “${esc(c.quote)}”</p>`).join("")}
    </div>`).join("");
}
boot();
