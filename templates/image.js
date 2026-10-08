// visual_type "image": a photo or illustration. Fields: image_description, caption?, image_path?
// Version 1 has no image source, so this draws a styled placeholder panel with the caption.
// image_description is not shown on screen; it is kept in the scene file for when real images arrive.
{
  const eyebrow = el("div", "eyebrow", SCENE.title);
  const panel = el("div", "panel");
  const orbs = [
    { w: 520, x: 1040, y: -140, c: "rgba(56,189,248,0.22)" },
    { w: 320, x: 1280, y: 220, c: "rgba(245,158,11,0.16)" },
    { w: 240, x: 860, y: 260, c: "rgba(56,189,248,0.12)" },
  ].map((o) => {
    const d = el("div", "orb");
    Object.assign(d.style, { width: o.w + "px", height: o.w + "px", left: o.x + "px", top: o.y + "px", background: o.c });
    panel.appendChild(d);
    return d;
  });
  const cap = el("div", "cap-in", VC.caption || SCENE.title);
  panel.appendChild(cap);
  stage.append(eyebrow, panel);

  tl.fromTo(eyebrow, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, 0.1);
  tl.fromTo(panel, { opacity: 0, scale: 0.97 }, { opacity: 1, scale: 1, duration: 0.8, ease: "power3.out" }, 0.3);
  tl.fromTo(orbs, { opacity: 0 }, { opacity: 1, duration: 1.2, stagger: 0.2 }, 0.6);
  tl.to(orbs, { x: -60, duration: Math.max(SCENE.duration - 1, 1), ease: "none" }, 0.6);
  tl.fromTo(cap, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }, 1.0);
}
