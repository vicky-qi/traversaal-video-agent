// visual_type "bullets": 2-5 parts, steps or reasons. Fields: heading?, bullets
{
  const eyebrow = el("div", "eyebrow", SCENE.title);
  const head = el("h1", "headline", VC.heading || SCENE.title);
  head.style.fontSize = "72px";
  const rows = el("div", "rows");
  const items = (VC.bullets || []).map((b, i) => {
    const r = el("div", "row");
    r.append(el("div", "num", String(i + 1)), el("div", "txt", b));
    rows.appendChild(r);
    return r;
  });
  stage.append(eyebrow, head, rows);

  tl.fromTo([eyebrow, head], { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, stagger: 0.1, ease: "power3.out" }, 0.1);
  tl.fromTo(items, { opacity: 0, y: 30 }, { opacity: 0.35, y: 0, duration: 0.5, stagger: 0.08, ease: "power2.out" }, 0.5);
  // Each row lights up in turn, spread across the narration.
  items.forEach((r, k) => {
    const t = Math.max(1.0, revealAt(k, items.length));
    tl.to(r, { opacity: 1, duration: 0.4, ease: "power2.out" }, t);
    tl.set(r, { className: "row on" }, t);
  });
}
