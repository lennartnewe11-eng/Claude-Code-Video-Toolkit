import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const FONT =
  '"Inter", "Helvetica Neue", Arial, sans-serif';

/** Country tag that snaps in lower-left. */
export const CountryLabel: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, config: {damping: 14, stiffness: 180}});
  const y = interpolate(s, [0, 1], [40, 0]);
  return (
    <div
      style={{
        position: 'absolute',
        left: 80,
        bottom: 90,
        transform: `translateY(${y}px)`,
        opacity: s,
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: 64,
        color: '#fff',
        letterSpacing: 4,
        textShadow: '0 4px 24px rgba(0,0,0,0.6)',
        padding: '6px 22px',
        borderLeft: '8px solid #ff3b30',
      }}
    >
      {text}
    </div>
  );
};

/** Speed / fact overlay, snaps in upper-right, slight overshoot. */
export const SpeedOverlay: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, config: {damping: 10, stiffness: 200}});
  const scale = interpolate(s, [0, 1], [0.7, 1]);
  return (
    <div
      style={{
        position: 'absolute',
        right: 80,
        top: 90,
        transform: `scale(${scale})`,
        transformOrigin: 'right top',
        opacity: s,
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: 56,
        color: '#0a0a0a',
        background: '#ffd60a',
        padding: '10px 24px',
        borderRadius: 8,
        boxShadow: '0 8px 30px rgba(0,0,0,0.5)',
      }}
    >
      {text}
    </div>
  );
};

/**
 * Animated count-up used for the China HSR growth ("0 → 42.000 km").
 * Parses the trailing number out of the label and counts toward it.
 */
export const GrowthCounter: React.FC<{target: number; suffix: string}> = ({
  target,
  suffix,
}) => {
  const frame = useCurrentFrame();
  const value = Math.round(
    interpolate(frame, [0, 70], [0, target], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );
  return (
    <div
      style={{
        position: 'absolute',
        right: 80,
        top: 90,
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: 64,
        color: '#0a0a0a',
        background: '#ffd60a',
        padding: '10px 26px',
        borderRadius: 8,
        boxShadow: '0 8px 30px rgba(0,0,0,0.5)',
      }}
    >
      {value.toLocaleString('de-DE')} {suffix}
    </div>
  );
};
