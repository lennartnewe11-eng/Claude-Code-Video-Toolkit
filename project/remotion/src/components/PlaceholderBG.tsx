import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

/**
 * Animated gradient placeholder used until real footage is wired in.
 * `drift` gives constant motion so even the placeholder reads as "moving"
 * in the fast-cut phase. Each segment passes a themed colour pair.
 */
export const PlaceholderBG: React.FC<{
  colors: [string, string];
  drift?: number; // px of horizontal pan across the clip
  label?: string;
}> = ({colors, drift = 120, label}) => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, 60], [0, -drift], {
    extrapolateRight: 'extend',
  });
  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: colors[0]}}>
      <AbsoluteFill
        style={{
          transform: `translateX(${x}px) scale(1.15)`,
          background: `linear-gradient(115deg, ${colors[0]} 0%, ${colors[1]} 100%)`,
        }}
      />
      {/* moving streaks to fake speed/motion */}
      <AbsoluteFill
        style={{
          transform: `translateX(${x * 1.8}px)`,
          backgroundImage:
            'repeating-linear-gradient(100deg, rgba(255,255,255,0.05) 0 2px, transparent 2px 60px)',
        }}
      />
      {label ? (
        <AbsoluteFill
          style={{
            justifyContent: 'center',
            alignItems: 'center',
            opacity: 0.08,
            fontSize: 240,
            fontWeight: 900,
            color: '#fff',
            letterSpacing: 8,
          }}
        >
          {label}
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
