/* core.js — the dumb transcript renderer.
 *
 * Knows transcripts (scenes → runs → {u, reply}) and nothing else: no markers, no
 * verdicts, no house styles. A study layers its own views on top by passing decorator
 * callbacks (badge / header / between-turn) that return HTML strings — core never
 * interprets them, it only places them.
 *
 * Exposes window.Core = { esc, md, lighten, renderArc, renderCompare }.
 */
(function () {
  const esc = (s) => (s == null ? '' : String(s)).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

  /* ---- minimal markdown (generic; used by study doc tabs) ---- */
  function inline(s) {
    s = esc(s);
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    s = s.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
    s = s.replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>');
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    return s;
  }
  function md(src) {
    const lines = (src || '').split('\n'); let out = [], i = 0;
    const isBlock = (s) => /^\s*(#{1,6}\s|>|---|\*\*\*|___|\d+\.\s+|[-*]\s|\|.*\|\s*$|```)/.test(s);
    const list = (ol) => {
      let items = [];
      while (i < lines.length) {
        const re = ol ? /^\s*\d+\.\s+/ : /^\s*[-*]\s+/;
        if (re.test(lines[i])) { items.push(lines[i].replace(re, '')); i++; }
        else if (lines[i].trim() === '') {
          let j = i + 1; while (j < lines.length && lines[j].trim() === '') j++;
          if (j < lines.length && re.test(lines[j])) i = j; else break;
        } else if (items.length && !isBlock(lines[i])) { items[items.length - 1] += ' ' + lines[i].trim(); i++; }
        else break;
      }
      out.push((ol ? '<ol>' : '<ul>') + items.map(x => '<li>' + inline(x) + '</li>').join('') + (ol ? '</ol>' : '</ul>'));
    };
    while (i < lines.length) {
      let ln = lines[i];
      if (/^\s*```/.test(ln)) { let b = []; i++; while (i < lines.length && !/^\s*```/.test(lines[i])) { b.push(esc(lines[i])); i++; } i++; out.push('<pre><code>' + b.join('\n') + '</code></pre>'); continue; }
      if (/^#{1,6}\s/.test(ln)) { const n = ln.match(/^#+/)[0].length; out.push('<h' + n + '>' + inline(ln.replace(/^#+\s/, '')) + '</h' + n + '>'); i++; continue; }
      if (/^\s*(---|\*\*\*|___)\s*$/.test(ln)) { out.push('<hr>'); i++; continue; }
      if (/^\s*>/.test(ln)) { let b = []; while (i < lines.length && /^\s*>/.test(lines[i])) { b.push(lines[i].replace(/^\s*>\s?/, '')); i++; } out.push('<blockquote>' + md(b.join('\n')) + '</blockquote>'); continue; }
      if (/^\s*\|.*\|\s*$/.test(ln) && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1])) {
        const row = r => r.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
        const head = row(ln); i += 2; let body = [];
        while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) { body.push(row(lines[i])); i++; }
        out.push('<table><thead><tr>' + head.map(h => '<th>' + inline(h) + '</th>').join('') + '</tr></thead><tbody>' +
          body.map(r => '<tr>' + r.map(c => '<td>' + inline(c) + '</td>').join('') + '</tr>').join('') + '</tbody></table>'); continue;
      }
      if (/^\s*[-*]\s+/.test(ln)) { list(false); continue; }
      if (/^\s*\d+\.\s+/.test(ln)) { list(true); continue; }
      if (ln.trim() === '') { i++; continue; }
      let b = [lines[i]]; i++;
      while (i < lines.length && lines[i].trim() !== '' && !isBlock(lines[i])) { b.push(lines[i]); i++; }
      out.push('<p>' + inline(b.join(' ')) + '</p>');
    }
    return out.join('\n');
  }

  /* ---- color util: blend a hex toward white (studies use it for "unstable" cells) ---- */
  function lighten(hex, f) {
    f = f == null ? .55 : f; const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
    r = Math.round(r + (255 - r) * f); g = Math.round(g + (255 - g) * f); b = Math.round(b + (255 - b) * f);
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }

  /* ---- renderArc: one scene's runs as escalating user/reply panels ----
   * sc = { runs: [[{u, reply}], ...] }. opts.badge(sc) / opts.sub(sc) are optional
   * study decorators returning HTML; core only places what they return. */
  function renderArc(sc, opts) {
    opts = opts || {};
    const badge = opts.badge ? opts.badge(sc) : '';
    const sub = opts.sub ? opts.sub(sc) : '';
    const runs = sc.runs.map((run, ri) => {
      const panels = run.map(p => '<div class="panel"><div class="u">' + esc(p.u) + '</div>' +
        '<div class="a' + (p.reply ? '' : ' none') + '">' + (p.reply ? esc(p.reply) : '[no reply]') + '</div></div>').join('');
      return '<div class="run"><h4>run ' + ri + '</h4>' + panels + '</div>';
    }).join('');
    return sub + '<div class="runs">' + runs + '</div>';
  }

  /* ---- renderCompare: N transcripts side by side for one scene, one run ----
   * scene = { turns: [...] }; cols = [{ id, scene }] where scene is that column's
   * transcript-scene { runs }. opts.head(col) is an optional per-column header decorator. */
  function renderCompare(scene, cols, runIdx, opts) {
    opts = opts || {};
    let h = '<div class="cgrid chead">' + cols.map(c =>
      '<div class="ch"><span class="cm">' + esc(c.id) + '</span>' + (opts.head ? opts.head(c) : '') + '</div>'
    ).join('') + '</div>';
    scene.turns.forEach((u, i) => {
      h += '<div class="cu"><span class="un">U' + (i + 1) + '</span>' + esc(u) + '</div>';
      h += '<div class="cgrid">' + cols.map(c => {
        const turn = c.scene && c.scene.runs[runIdx] && c.scene.runs[runIdx][i];
        const reply = turn && turn.reply;
        return '<div class="ccell' + (reply ? '' : ' none') + '"><span class="cml">' + esc(c.id) + '</span>' +
          (reply ? esc(reply) : '[no reply]') + '</div>';
      }).join('') + '</div>';
    });
    return h;
  }

  window.Core = { esc, md, inline, lighten, renderArc, renderCompare };
})();
