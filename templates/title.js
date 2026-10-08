// visual_type "title": opening, section break or closing. Fields: headline, subheadline?, background_description?
{
  const wrap = el("div", "title-wrap");
  const eyebrow = el("div", "eyebrow", SCENE.topic || "");
  const head = el("h1", "headline", VC.headline || SCENE.title);
  wrap.append(eyebrow, head);
  let sub = null;
  if (VC.subheadline) { sub = el("p", "sub", VC.subheadline); wrap.appendChild(sub); }
  const bar = el("div", "title-bar");
  wrap.appendChild(bar);
  stage.appendChild(wrap);

  tl.fromTo(eyebrow, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, 0.2);
  tl.fromTo(head, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" }, 0.4);
  if (sub) tl.fromTo(sub, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, Math.max(1.2, lineAt(1)));
  tl.fromTo(bar, { scaleX: 0, transformOrigin: "left center" }, { scaleX: 1, duration: 0.8, ease: "power2.out" }, 0.9);
}
