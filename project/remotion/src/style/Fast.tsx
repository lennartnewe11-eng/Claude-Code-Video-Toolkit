import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, body, display, CUTOUT_SHADOW} from './theme';

type Dir = 'l' | 'r' | 'u' | 'd';
const VEC: Record<Dir, [number, number]> = {l: [-1, 0], r: [1, 0], u: [0, -1], d: [0, 1]};

/**
 * High-frequency object: a cut-out flies in, holds briefly, flies out — so the
 * collage is in constant churn (each object used once). `at`/`life` in frames.
 */
export const ObjectBurst: React.FC<{
  src: string;
  at: number;
  life?: number;
  cx: number;
  cy: number;
  w: number;
  dir?: Dir;
  rot?: number;
  flip?: boolean;
}> = ({src, at, life = 34, cx, cy, w, dir = 'd', rot = 0, flip}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const l = frame - at;
  if (l < -1 || l > life + 2) return null;

  const enter = spring({frame: l, fps, config: {damping: 13, stiffness: 210}});
  const exitP = interpolate(l, [life - 8, life], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const [vx, vy] = VEC[dir];
  const inOff = (1 - enter) * 150;
  const outOff = exitP * 90;
  const tx = inOff * vx + outOff * vx;
  const ty = inOff * vy + outOff * vy;
  const opacity = interpolate(l, [0, 4, life - 7, life], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(enter, [0, 1], [0.62, 1]) * (1 - exitP * 0.12);

  return (
    <Img
      src={staticFile(`cutouts/${src}`)}
      style={{
        position: 'absolute',
        left: cx,
        top: cy,
        width: w,
        transform: `translate(-50%,-50%) translate(${tx}px,${ty}px) rotate(${rot}deg) scale(${scale}) ${flip ? 'scaleX(-1)' : ''}`,
        filter: CUTOUT_SHADOW,
        opacity,
      }}
    />
  );
};

/** A word/phrase that punches in fast and out (display or body serif). */
export const WordFlash: React.FC<{
  text: string;
  at: number;
  life?: number;
  cx: number;
  cy: number;
  size?: number;
  disp?: boolean;
  accent?: boolean;
  italic?: boolean;
  rot?: number;
}> = ({text, at, life = 34, cx, cy, size = 120, disp = true, accent, italic, rot = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const l = frame - at;
  if (l < -1 || l > life + 2) return null;
  const enter = spring({frame: l, fps, config: {damping: 11, stiffness: 240}});
  const opacity = interpolate(l, [0, 3, life - 6, life], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(enter, [0, 1], [0.7, 1]);
  return (
    <div
      style={{
        position: 'absolute',
        left: cx,
        top: cy,
        transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${scale})`,
        opacity,
        fontFamily: disp ? display : body,
        fontWeight: disp ? 900 : 700,
        fontStyle: italic ? 'italic' : 'normal',
        fontSize: size,
        lineHeight: 0.9,
        letterSpacing: disp ? '0.005em' : 0,
        textTransform: disp ? 'uppercase' : 'none',
        color: accent ? COLORS.accent : COLORS.ink,
        whiteSpace: 'nowrap',
        textAlign: 'center',
      }}
    >
      {text}
    </div>
  );
};

/** Tiny flickering registration mark / tick for texture. */
export const Tick: React.FC<{at: number; life?: number; x: number; y: number; color?: string}> = ({
  at, life = 26, x, y, color = COLORS.accent,
}) => {
  const frame = useCurrentFrame();
  const l = frame - at;
  if (l < 0 || l > life) return null;
  const o = interpolate(l, [0, 3, life - 4, life], [0, 1, 1, 0]);
  return <div style={{position: 'absolute', left: x, top: y, width: 34, height: 4, background: color, opacity: o}} />;
};
