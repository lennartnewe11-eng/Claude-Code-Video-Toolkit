import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, body, CUTOUT_SHADOW} from './theme';

/** Muted design block that slides in (olive / taupe). */
export const AccentBlock: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  color?: string;
  delay?: number;
  from?: 'left' | 'top';
}> = ({x, y, w, h, color = COLORS.olive, delay = 0, from = 'left'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 18, stiffness: 120}});
  const off = interpolate(s, [0, 1], [from === 'left' ? -w : -h, 0]);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        backgroundColor: color,
        opacity: 0.95,
        transform: from === 'left' ? `translateX(${off}px)` : `translateY(${off}px)`,
      }}
    />
  );
};

/** Small-caps kicker label with a short rule. */
export const Kicker: React.FC<{text: string; x: number; y: number; delay?: number}> = ({
  text,
  x,
  y,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - delay, [0, 10], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        opacity: o,
        fontFamily: body,
        fontWeight: 700,
        fontSize: 24,
        letterSpacing: '0.32em',
        textTransform: 'uppercase',
        color: COLORS.inkSoft,
        display: 'flex',
        alignItems: 'center',
        gap: 16,
      }}
    >
      <span style={{width: 46, height: 2, background: COLORS.accent, display: 'inline-block'}} />
      {text}
    </div>
  );
};

/** Thin horizontal rule that draws in. */
export const Rule: React.FC<{x: number; y: number; w: number; delay?: number}> = ({
  x,
  y,
  w,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 20, stiffness: 90}});
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w * s,
        height: 2,
        background: COLORS.ink,
        opacity: 0.5,
      }}
    />
  );
};

/** A non-cutout photo element (e.g. the vintage map) on a paper card. */
export const PhotoCard: React.FC<{
  src: string; // filename in public/cutouts
  cx: number;
  cy: number;
  width: number;
  rotate?: number;
  delay?: number;
  sepia?: boolean;
}> = ({src, cx, cy, width, rotate = 0, delay = 0, sepia}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 16, stiffness: 110}});
  const scale = interpolate(s, [0, 1], [0.85, 1]);
  return (
    <div
      style={{
        position: 'absolute',
        left: cx,
        top: cy,
        width,
        transform: `translate(-50%,-50%) rotate(${rotate}deg) scale(${scale})`,
        opacity: s,
        padding: 12,
        background: '#fbf8ef',
        filter: CUTOUT_SHADOW,
      }}
    >
      <Img
        src={staticFile(`cutouts/${src}`)}
        style={{
          width: '100%',
          display: 'block',
          filter: sepia ? 'sepia(0.7) contrast(1.02)' : 'grayscale(1) contrast(1.03)',
        }}
      />
    </div>
  );
};
