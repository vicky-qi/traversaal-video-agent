// visual_type "chart": numbers from 03_checked.md. Fields: chart_type (bar|line|pie), chart_title, labels, values, unit, source_note
// Values are drawn exactly as given; nothing is rounded or calculated except the scale.
{
  const eyebrow = el("div", "eyebrow", SCENE.title);
  const head = el("h1", "headline", VC.chart_title || SCENE.title);
  head.style.fontSize = "64px";
  const unit = el("div", "unit", VC.unit || "");
  const chart = el("div", "chart");
  stage.append(eyebrow, head, unit, chart);
  tl.fromTo([eyebrow, head, unit], { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, stagger: 0.1, ease: "power3.out" }, 0.1);

  const labels = VC.labels || [];
  const values = (VC.values || []).map(Number);
  const fmt = (v) => (Math.abs(v) >= 1000 ? v.toLocaleString("en-US") : String(v));
  const colors = ["#38bdf8", "#f59e0b", "#a78bfa", "#34d399", "#f472b6", "#94a3b8", "#fb7185", "#facc15"];
  const type = VC.chart_type || "bar";

  if (type === "pie") {
    const total = values.reduce((a, b) => a + b, 0) || 1;
    let acc = 0;
    const stops = values.map((v, i) => {
      const a0 = (acc / total) * 360; acc += v; const a1 = (acc / total) * 360;
      return `${colors[i % colors.length]} ${a0}deg ${a1}deg`;
    });
    const donut = el("div");
    Object.assign(donut.style, { position: "absolute", left: "40px", top: "10px", width: "440px", height: "440px", borderRadius: "50%",
      background: `conic-gradient(${stops.join(",")})` });
    const hole = el("div");
    Object.assign(hole.style, { position: "absolute", left: "110px", top: "110px", width: "220px", height: "220px", borderRadius: "50%", background: "#0b1020" });
    donut.appendChild(hole);
    const legend = el("div", "legend");
    const items = labels.map((l, i) => {
      const it = el("div", "item");
      const sw = el("div", "sw"); sw.style.background = colors[i % colors.length];
      it.append(sw, el("span", null, `${l}: ${fmt(values[i])}`));
      legend.appendChild(it);
      return it;
    });
    chart.append(donut, legend);
    tl.fromTo(donut, { opacity: 0, rotate: -90, scale: 0.8 }, { opacity: 1, rotate: 0, scale: 1, duration: 1.0, ease: "power3.out" }, Math.max(0.8, lineAt(1)));
    tl.fromTo(items, { opacity: 0, x: 20 }, { opacity: 1, x: 0, duration: 0.4, stagger: 0.15 }, Math.max(1.2, lineAt(1) + 0.4));
  } else if (type === "line") {
    const W = 1500, H = 380, PAD = 60, TOP = 90;
    const min = Math.min(0, ...values), max = Math.max(...values, 1);
    const pts = values.map((v, i) => [PAD + (i * (W - 2 * PAD)) / Math.max(values.length - 1, 1), H - PAD - ((v - min) / (max - min || 1)) * (H - PAD - TOP)]);
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("width", W); svg.setAttribute("height", H + 60);
    const axis = document.createElementNS(ns, "line");
    Object.entries({ x1: PAD, y1: H - PAD, x2: W - PAD, y2: H - PAD, stroke: "#334155", "stroke-width": 2 }).forEach(([k, v]) => axis.setAttribute(k, v));
    const path = document.createElementNS(ns, "polyline");
    Object.entries({ points: pts.map((p) => p.join(",")).join(" "), fill: "none", stroke: "#38bdf8", "stroke-width": 8, "stroke-linejoin": "round", "stroke-linecap": "round" })
      .forEach(([k, v]) => path.setAttribute(k, v));
    svg.append(axis, path);
    const marks = [];
    pts.forEach(([x, y], i) => {
      const dot = document.createElementNS(ns, "circle");
      Object.entries({ cx: x, cy: y, r: 12, fill: "#38bdf8" }).forEach(([k, v]) => dot.setAttribute(k, v));
      const val = document.createElementNS(ns, "text");
      Object.entries({ x, y: y - 28, fill: "#f4f4f5", "font-size": 32, "font-weight": 700, "text-anchor": "middle" }).forEach(([k, v]) => val.setAttribute(k, v));
      val.textContent = fmt(values[i]);
      const lab = document.createElementNS(ns, "text");
      Object.entries({ x, y: H - PAD + 46, fill: "#cbd5e1", "font-size": 30, "text-anchor": "middle" }).forEach(([k, v]) => lab.setAttribute(k, v));
      lab.textContent = labels[i] || "";
      svg.append(dot, val, lab);
      marks.push(dot, val, lab);
    });
    chart.appendChild(svg);
    const len = pts.reduce((s, p, i) => (i ? s + Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]) : 0), 0);
    path.setAttribute("stroke-dasharray", len); path.setAttribute("stroke-dashoffset", len);
    const t0 = Math.max(0.8, lineAt(1));
    tl.to(path, { attr: { "stroke-dashoffset": 0 }, duration: 1.4, ease: "power2.inOut" }, t0);
    tl.fromTo(marks, { opacity: 0 }, { opacity: 1, duration: 0.3, stagger: 0.05 }, t0 + 0.3);
  } else {
    const max = Math.max(...values, 1);
    const bars = labels.map((l, i) => {
      const row = el("div", "bar-row");
      const lab = el("div", "bar-label", l);
      const track = el("div", "bar-track");
      const pct = (values[i] / max) * 82;
      const bar = el("div", "bar");
      bar.style.background = colors[i % 2 === 0 ? 0 : 1];
      bar.style.width = pct + "%";
      const val = el("div", "bar-val", fmt(values[i]));
      val.style.left = `calc(${pct}% + 20px)`;
      track.append(bar, val);
      row.append(lab, track);
      chart.appendChild(row);
      return { bar, val };
    });
    // Bars grow with a transform (scaleX) so motion stays smooth; values fade in at their final spot.
    bars.forEach((b, k) => {
      const t = Math.max(0.8, revealAt(k, bars.length));
      tl.fromTo(b.bar, { scaleX: 0, transformOrigin: "left center" }, { scaleX: 1, duration: 0.9, ease: "power2.out" }, t);
      tl.fromTo(b.val, { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.6, ease: "power2.out" }, t + 0.5);
    });
  }
}
