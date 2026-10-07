import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const MyComposition = () => {
  return (
    <Composition
      id="MyComp"
      component={MyComponent}
      durationInFrames={180}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};

export const MyComponent: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const fadeOut = interpolate(t, [5.4, 5.9], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const titleIn = interpolate(t, [0.2, 1.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const bar = interpolate(t, [0.8, 2.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });
  const subIn = interpolate(t, [1.6, 2.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        background: "#0b1020",
        alignItems: "center",
        justifyContent: "center",
        gap: 32,
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      <h1
        style={{
          margin: 0,
          color: "#f4f4f5",
          fontSize: 96,
          fontWeight: 700,
          letterSpacing: "-0.03em",
          opacity: titleIn * fadeOut,
          transform: `translateY(${(1 - titleIn) * 40}px)`,
        }}
      >
        Prompt → Video
      </h1>
      <div
        style={{
          width: 900,
          height: 14,
          borderRadius: 7,
          background: "#38bdf8",
          transformOrigin: "left center",
          transform: `scaleX(${bar})`,
          opacity: fadeOut,
        }}
      />
      <p style={{ margin: 0, color: "#94a3b8", fontSize: 40, opacity: subIn * fadeOut }}>
        Remotion test clip · Traversaal.ai capstone
      </p>
    </AbsoluteFill>
  );
};
