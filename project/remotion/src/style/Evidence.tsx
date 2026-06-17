import {
  AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {EV, mono, cond, PHOTO_SHADOW} from './evidence';

/** Graph-paper / case-file background. */
export const GraphPaper: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: EV.paper}}>
    <Img src={staticFile('bg/paper.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', opacity: 0.5, mixBlendMode: 'multiply'}} />
    {/* grid */}
    <AbsoluteFill style={{
      backgroundImage:
        `linear-gradient(rgba(60,54,42,0.10) 1px, transparent 1px),
         linear-gradient(90deg, rgba(60,54,42,0.10) 1px, transparent 1px)`,
      backgroundSize: '46px 46px',
    }} />
    <AbsoluteFill style={{boxShadow: 'inset 0 0 300px rgba(70,60,42,0.4)'}} />
  </AbsoluteFill>
);

const useReveal = (at: number, dur = 8) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at, fps, config: {damping: 16, stiffness: 150}});
  const o = interpolate(frame - at, [0, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return {s, o};
};

/** Monospace case-file heading with an optional yellow highlight swipe. */
export const TypeHeading: React.FC<{
  text: string; x: number; y: number; size?: number; at?: number; highlight?: boolean; color?: string;
}> = ({text, x, y, size = 30, at = 0, highlight, color = EV.ink}) => {
  const frame = useCurrentFrame();
  const {o} = useReveal(at);
  const hw = interpolate(frame - at - 4, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, fontFamily: mono, fontWeight: 700, fontSize: size, letterSpacing: '0.22em', textTransform: 'uppercase', color, whiteSpace: 'nowrap'}}>
      {highlight && (
        <div style={{position: 'absolute', left: -6, top: '12%', height: '80%', width: `calc(${hw * 100}% + 12px)`, background: EV.yellow, zIndex: -1, transform: 'skewX(-6deg)'}} />
      )}
      {text}
    </div>
  );
};

/** Big condensed headline with print texture + dashed underline. */
export const Headline: React.FC<{text: string; x: number; y: number; size?: number; at?: number}> = ({
  text, x, y, size = 92, at = 0,
}) => {
  const {s, o} = useReveal(at);
  const tx = interpolate(s, [0, 1], [-30, 0]);
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `translateX(${tx}px)`}}>
      <div style={{fontFamily: cond, fontWeight: 700, fontSize: size, lineHeight: 0.96, letterSpacing: '0.01em', textTransform: 'uppercase', color: EV.ink, background: EV.ink, WebkitBackgroundClip: 'text'}}>{text}</div>
      <div style={{marginTop: 6, height: 0, borderTop: `3px dashed ${EV.ink}`, width: '100%'}} />
    </div>
  );
};

/** A taped B/W photo with caption + redaction bar. */
export const TapedPhoto: React.FC<{
  src: string; cx: number; cy: number; w: number; rot?: number; at?: number; caption?: string; folder?: string;
}> = ({src, cx, cy, w, rot = 0, at = 0, caption, folder = 'photos'}) => {
  const {s, o} = useReveal(at);
  const scale = interpolate(s, [0, 1], [0.86, 1]);
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${scale})`, opacity: o, background: '#fbf8ef', padding: 12, paddingBottom: caption ? 44 : 12, boxShadow: PHOTO_SHADOW, width: w}}>
      {/* tape */}
      <div style={{position: 'absolute', top: -16, left: '50%', transform: 'translateX(-50%) rotate(-4deg)', width: 110, height: 30, background: EV.tape, boxShadow: '0 1px 2px rgba(0,0,0,0.15)'}} />
      <Img src={staticFile(`${folder}/${src}`)} style={{width: '100%', display: 'block', filter: 'grayscale(1) contrast(1.08) brightness(0.98)'}} />
      {caption && (
        <div style={{position: 'absolute', left: 14, bottom: 12, fontFamily: mono, fontSize: 18, color: EV.inkSoft, letterSpacing: '0.04em'}}>{caption}</div>
      )}
    </div>
  );
};

/** Justified case-file body text that wipes in line by line. */
export const BodyBlock: React.FC<{lines: string[]; x: number; y: number; w: number; at?: number; size?: number}> = ({
  lines, x, y, w, at = 0, size = 19,
}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, fontFamily: mono, fontSize: size, lineHeight: 1.5, color: EV.ink, textAlign: 'justify'}}>
      {lines.map((ln, i) => {
        const o = interpolate(frame - at - i * 6, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return <div key={i} style={{opacity: o}}>{ln}</div>;
      })}
    </div>
  );
};

/** An annotated antique map plate, darkened, slides in. */
export const MapPlate: React.FC<{cx: number; cy: number; w: number; at?: number; rot?: number; src?: string}> = ({
  cx, cy, w, at = 0, rot = 0, src = 'us1867.jpg',
}) => {
  const {s, o} = useReveal(at, 12);
  const scale = interpolate(s, [0, 1], [0.92, 1]);
  return (
    <div style={{position: 'absolute', left: cx, top: cy, width: w, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${scale})`, opacity: o, boxShadow: PHOTO_SHADOW, border: '6px solid #1b1812'}}>
      <Img src={staticFile(`maps/${src}`)} style={{width: '100%', display: 'block', filter: 'sepia(0.35) contrast(1.12) brightness(0.92) saturate(0.8)'}} />
    </div>
  );
};

/** Red marker route that draws on (SVG), with optional arrow head. */
export const RouteLine: React.FC<{
  points: [number, number][]; at?: number; drawFrames?: number; arrow?: boolean; width?: number;
}> = ({points, at = 0, drawFrames = 24, arrow = true, width = 4}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, drawFrames], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const d = points.map((pt, i) => `${i ? 'L' : 'M'}${pt[0]},${pt[1]}`).join(' ');
  // total length approx
  let len = 0;
  for (let i = 1; i < points.length; i++) len += Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]);
  const end = points[points.length - 1];
  const prev = points[points.length - 2] ?? end;
  const ang = Math.atan2(end[1] - prev[1], end[0] - prev[0]) * 180 / Math.PI;
  return (
    <svg style={{position: 'absolute', left: 0, top: 0}} width={1920} height={1080}>
      <path d={d} fill="none" stroke={EV.red} strokeWidth={width} strokeDasharray={len} strokeDashoffset={len * (1 - p)} strokeLinecap="round" />
      {arrow && p > 0.96 && (
        <g transform={`translate(${end[0]},${end[1]}) rotate(${ang})`}>
          <path d="M0,0 L-22,-9 L-22,9 Z" fill={EV.red} />
        </g>
      )}
    </svg>
  );
};

/** Red X mark that stamps in. */
export const XMark: React.FC<{x: number; y: number; at?: number; size?: number}> = ({x, y, at = 0, size = 34}) => {
  const {s} = useReveal(at);
  const sc = interpolate(s, [0, 1], [1.6, 1]);
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) scale(${sc})`, opacity: interpolate(s, [0, 0.3], [0, 1]), color: EV.red, fontFamily: cond, fontWeight: 700, fontSize: size}}>✕</div>
  );
};

/** Circled label (red ellipse draws around text). */
export const CircleLabel: React.FC<{text: string; x: number; y: number; at?: number; size?: number}> = ({
  text, x, y, at = 0, size = 30,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const {o} = useReveal(at);
  const C = 2 * Math.PI * 60;
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: 'translate(-50%,-50%)'}}>
      <svg width={180} height={96} style={{position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%,-50%)'}}>
        <ellipse cx={90} cy={48} rx={78} ry={36} fill="none" stroke={EV.red} strokeWidth={4} strokeDasharray={C} strokeDashoffset={C * (1 - p)} transform="rotate(-6 90 48)" />
      </svg>
      <div style={{opacity: o, fontFamily: mono, fontWeight: 700, fontSize: size, color: EV.ink, letterSpacing: '0.08em'}}>{text}</div>
    </div>
  );
};

/** A map marker: red dot pops in with a small typewriter label. */
export const MapDot: React.FC<{x: number; y: number; label?: string; at?: number; struck?: boolean; below?: boolean}> = ({
  x, y, label, at = 0, struck, below,
}) => {
  const {s, o} = useReveal(at);
  const sc = interpolate(s, [0, 1], [0, 1]);
  return (
    <div style={{position: 'absolute', left: x, top: y}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 18, height: 18, borderRadius: '50%', background: struck ? '#5d574c' : EV.red, border: `3px solid ${EV.paper}`, transform: `translate(-50%,-50%) scale(${sc})`}} />
      {label && (
        <div style={{position: 'absolute', left: 16, top: below ? 8 : -30, opacity: o, fontFamily: mono, fontWeight: 700, fontSize: 18, letterSpacing: '0.08em', color: EV.ink, whiteSpace: 'nowrap', textDecoration: struck ? 'line-through' : 'none'}}>{label}</div>
      )}
    </div>
  );
};

/** Crosshair registration mark. */
export const Crosshair: React.FC<{x: number; y: number; at?: number}> = ({x, y, at = 0}) => {
  const {o} = useReveal(at);
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o * 0.7, color: EV.ink, fontFamily: cond, fontSize: 34}}>+</div>
  );
};

/** Yellow highlighter bar. */
export const Highlight: React.FC<{x: number; y: number; w: number; at?: number; h?: number}> = ({x, y, w, at = 0, h = 22}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', left: x, top: y, width: w * p, height: h, background: EV.yellow, opacity: 0.85, transform: 'skewX(-8deg)'}} />;
};

/** Red rubber stamp — slams in slightly oversized then settles, rotated. */
export const Stamp: React.FC<{text: string; x: number; y: number; size?: number; at?: number; rot?: number}> = ({
  text, x, y, size = 64, at = 0, rot = -8,
}) => {
  const {s} = useReveal(at);
  const sc = interpolate(s, [0, 0.5, 1], [1.8, 0.95, 1]);
  const op = interpolate(s, [0, 0.25], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${sc})`, opacity: op * 0.92}}>
      <div style={{fontFamily: cond, fontWeight: 700, fontSize: size, letterSpacing: '0.04em', textTransform: 'uppercase', color: EV.red, border: `5px solid ${EV.red}`, padding: '6px 22px', borderRadius: 6}}>{text}</div>
    </div>
  );
};

/** Big red marker number/annotation. */
export const RedNote: React.FC<{text: string; x: number; y: number; size?: number; at?: number; rot?: number}> = ({
  text, x, y, size = 80, at = 0, rot = -3,
}) => {
  const {s, o} = useReveal(at);
  const sc = interpolate(s, [0, 1], [0.7, 1]);
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${sc})`, opacity: o, fontFamily: cond, fontWeight: 700, fontSize: size, color: EV.red, whiteSpace: 'nowrap'}}>{text}</div>
  );
};

/** Redaction bar. */
export const Redaction: React.FC<{x: number; y: number; w: number; at?: number; h?: number}> = ({x, y, w, at = 0, h = 20}) => {
  const {o} = useReveal(at);
  return <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: EV.ink, opacity: o}} />;
};
