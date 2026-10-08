// visual_type "quote": one exact quote. Fields: quote_text, attribution
{
  const box = el("div", "quote");
  const q = el("div", "q", "“" + (VC.quote_text || "") + "”");
  const who = el("div", "who", VC.attribution ? "— " + VC.attribution : "");
  box.append(q, who);
  stage.appendChild(box);

  tl.fromTo(box, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.8, ease: "power3.out" }, 0.3);
  tl.fromTo(who, { opacity: 0 }, { opacity: 1, duration: 0.6 }, Math.max(1.4, lineAt(1)));
}
