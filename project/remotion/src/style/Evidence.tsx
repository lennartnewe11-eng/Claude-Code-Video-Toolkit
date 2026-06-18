import {
  AbsoluteFill, Img, interpolate, OffthreadVideo, spring, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {EV, mono, cond, PHOTO_SHADOW} from './evidence';

/**
 * Full-screen archival video insert — breaks up the collage but stays in the
 * documentary look (B/W, grain, vignette, slow push, typewriter caption).
 * Place inside a <Sequence> so it plays from its start.
 */
export const FullScreenVideo: React.FC<{src: string; caption?: string; stamp?: string; durationFrames: number}> = ({
  src, caption, stamp, durationFrames,
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationFrames], [1.05, 1.12]);
  const inOut = interpolate(frame, [0, 4, durationFrames - 5, durationFrames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const flick = 0.92 + 0.08 * Math.abs(Math.sin(frame * 1.7));
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: inOut}}>
      <OffthreadVideo src={staticFile(`clips/${src}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: `grayscale(1) contrast(1.15) brightness(${flick})`}} />
      {/* grain + scanlines */}
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.18) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.5}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 260px rgba(0,0,0,0.85)'}} />
      {stamp && (
        <div style={{position: 'absolute', top: 60, right: 100, fontFamily: mono, fontWeight: 700, fontSize: 26, letterSpacing: '0.18em', color: '#e9e4d6'}}>{stamp}</div>
      )}
      {caption && (
        <div style={{position: 'absolute', left: 70, bottom: 70, fontFamily: mono, fontSize: 30, letterSpacing: '0.08em', color: '#e9e4d6', borderLeft: `4px solid ${EV.red}`, paddingLeft: 18}}>{caption}</div>
      )}
    </AbsoluteFill>
  );
};

/** Red marker ellipse that draws around something. */
export const Circle: React.FC<{x: number; y: number; rx: number; ry: number; at?: number; rot?: number}> = ({
  x, y, rx, ry, at = 0, rot = -5,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const C = 2 * Math.PI * Math.max(rx, ry);
  return (
    <svg style={{position: 'absolute', left: x - rx - 10, top: y - ry - 10}} width={rx * 2 + 20} height={ry * 2 + 20}>
      <ellipse cx={rx + 10} cy={ry + 10} rx={rx} ry={ry} fill="none" stroke={EV.red} strokeWidth={4} strokeDasharray={C} strokeDashoffset={C * (1 - p)} transform={`rotate(${rot} ${rx + 10} ${ry + 10})`} />
    </svg>
  );
};

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
  src: string; cx: number; cy: number; w: number; rot?: number; at?: number; caption?: string; folder?: string; gray?: boolean;
}> = ({src, cx, cy, w, rot = 0, at = 0, caption, folder = 'photos', gray = true}) => {
  const {s, o} = useReveal(at);
  const scale = interpolate(s, [0, 1], [0.86, 1]);
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${scale})`, opacity: o, background: '#fbf8ef', padding: 12, paddingBottom: caption ? 44 : 12, boxShadow: PHOTO_SHADOW, width: w}}>
      {/* tape */}
      <div style={{position: 'absolute', top: -16, left: '50%', transform: 'translateX(-50%) rotate(-4deg)', width: 110, height: 30, background: EV.tape, boxShadow: '0 1px 2px rgba(0,0,0,0.15)'}} />
      <Img src={staticFile(`${folder}/${src}`)} style={{width: '100%', display: 'block', filter: gray ? 'grayscale(1) contrast(1.08) brightness(0.98)' : 'contrast(1.03) saturate(1.05)'}} />
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

/** Faint antique map placed as a background texture (no frame). */
export const MapBackdrop: React.FC<{src: string; cx: number; cy: number; w: number; at?: number; opacity?: number; rot?: number}> = ({
  src, cx, cy, w, at = 0, opacity = 0.32, rot = 0,
}) => {
  const {o} = useReveal(at, 14);
  return (
    <Img src={staticFile(`maps/${src}`)} style={{position: 'absolute', left: cx, top: cy, width: w, transform: `translate(-50%,-50%) rotate(${rot}deg)`, opacity: o * opacity, filter: 'sepia(0.5) contrast(1.05) brightness(0.96)'}} />
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

/** Dashed box that draws/fades in around an area. */
export const DashedBox: React.FC<{x: number; y: number; w: number; h: number; at?: number; color?: string}> = ({
  x, y, w, h, at = 0, color = EV.ink,
}) => {
  const {o} = useReveal(at);
  return <div style={{position: 'absolute', left: x, top: y, width: w, height: h, border: `2px dashed ${color}`, opacity: o * 0.85}} />;
};

/** Corner registration brackets framing a region. */
export const CornerMarks: React.FC<{x: number; y: number; w: number; h: number; at?: number; size?: number; color?: string}> = ({
  x, y, w, h, at = 0, size = 28, color = EV.red,
}) => {
  const {o} = useReveal(at);
  const B = (st: React.CSSProperties) => <div style={{position: 'absolute', width: size, height: size, ...st}} />;
  const line = `3px solid ${color}`;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: o}}>
      {B({top: 0, left: 0, borderTop: line, borderLeft: line})}
      {B({top: 0, right: 0, borderTop: line, borderRight: line})}
      {B({bottom: 0, left: 0, borderBottom: line, borderLeft: line})}
      {B({bottom: 0, right: 0, borderBottom: line, borderRight: line})}
    </div>
  );
};

/** Round rubber seal/stamp (e.g. file authority). */
export const Seal: React.FC<{text: string; x: number; y: number; at?: number; size?: number; rot?: number}> = ({
  text, x, y, at = 0, size = 150, rot = -12,
}) => {
  const {s} = useReveal(at);
  const sc = interpolate(s, [0, 0.5, 1], [1.6, 0.95, 1]);
  const op = interpolate(s, [0, 0.25], [0, 1], {extrapolateRight: 'clamp'}) * 0.8;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: size, height: size, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${sc})`, opacity: op, borderRadius: '50%', border: `4px double ${EV.red}`, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: EV.red, fontFamily: mono, fontWeight: 700, fontSize: size * 0.13, letterSpacing: '0.12em', textTransform: 'uppercase', padding: size * 0.12, lineHeight: 1.2}}>
      {text}
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

/** Typewriter reveal — characters appear one by one with a blinking cursor. */
export const Typewriter: React.FC<{
  text: string; x: number; y: number; size?: number; at?: number; cps?: number; color?: string; bold?: boolean;
}> = ({text, x, y, size = 42, at = 0, cps = 28, color = EV.ink, bold}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const elapsed = Math.max(0, frame - at);
  const n = Math.floor((elapsed / fps) * cps);
  const shown = text.slice(0, n);
  const done = n >= text.length;
  const cursor = !done && Math.floor(frame / 8) % 2 === 0;
  if (elapsed <= 0) return null;
  return (
    <div style={{position: 'absolute', left: x, top: y, fontFamily: mono, fontWeight: bold ? 700 : 400, fontSize: size, letterSpacing: '0.02em', color, whiteSpace: 'pre'}}>
      {shown}<span style={{opacity: cursor ? 1 : 0}}>▌</span>
    </div>
  );
};

/** Big red X drawn over a region (to strike something out). */
export const BigX: React.FC<{x: number; y: number; w: number; h: number; at?: number}> = ({x, y, w, h, at = 0}) => {
  const frame = useCurrentFrame();
  const p1 = interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const p2 = interpolate(frame - at, [6, 13], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const d = Math.hypot(w, h);
  return (
    <svg style={{position: 'absolute', left: x, top: y}} width={w} height={h}>
      <line x1={0} y1={0} x2={w} y2={h} stroke={EV.red} strokeWidth={9} strokeLinecap="round" strokeDasharray={d} strokeDashoffset={d * (1 - p1)} />
      <line x1={w} y1={0} x2={0} y2={h} stroke={EV.red} strokeWidth={9} strokeLinecap="round" strokeDasharray={d} strokeDashoffset={d * (1 - p2)} />
    </svg>
  );
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

/** Risograph / newsprint halftone dot texture overlay. */
export const Halftone: React.FC<{opacity?: number; size?: number; color?: string}> = ({opacity = 0.1, size = 7, color = 'rgba(20,16,10,1)'}) => (
  <AbsoluteFill style={{backgroundImage: `radial-gradient(${color} 1px, transparent 1.5px)`, backgroundSize: `${size}px ${size}px`, opacity, mixBlendMode: 'multiply', pointerEvents: 'none'}} />
);

/** Typed case-file document: LABEL ........ value rows, revealed line by line,
 *  with optional yellow highlight on key rows. */
export const Dossier: React.FC<{
  x: number; y: number; w: number; at?: number; title?: string; size?: number;
  rows: {label: string; value: string; hl?: boolean}[];
}> = ({x, y, w, at = 0, title, size = 22, rows}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, fontFamily: mono, color: EV.ink}}>
      {title && (
        <div style={{fontWeight: 700, fontSize: size * 0.92, letterSpacing: '0.16em', textTransform: 'uppercase', borderBottom: `2px solid ${EV.ink}`, paddingBottom: 6, marginBottom: 14, opacity: interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{title}</div>
      )}
      {rows.map((r, i) => {
        const o = interpolate(frame - at - 8 - i * 7, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const hw = interpolate(frame - at - 8 - i * 7, [4, 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (
          <div key={i} style={{display: 'flex', alignItems: 'baseline', opacity: o, marginBottom: size * 0.62, position: 'relative'}}>
            <span style={{fontSize: size * 0.74, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: EV.inkSoft, whiteSpace: 'nowrap'}}>{r.label}</span>
            <span style={{flex: 1, margin: '0 8px', borderBottom: `2px dotted ${EV.inkSoft}`, transform: 'translateY(-4px)', opacity: 0.6}} />
            <span style={{position: 'relative', fontSize: size, fontWeight: 700, whiteSpace: 'nowrap'}}>
              {r.hl && <span style={{position: 'absolute', left: -5, top: '14%', height: '78%', width: `calc(${hw * 100}% + 10px)`, background: EV.yellow, zIndex: -1, transform: 'skewX(-6deg)'}} />}
              {r.value}
            </span>
          </div>
        );
      })}
    </div>
  );
};

/** A taped quote / caption card (white slip with a handwritten-style quote). */
export const QuoteBox: React.FC<{text: string; x: number; y: number; w: number; at?: number; rot?: number; size?: number; cite?: string}> = ({
  text, x, y, w, at = 0, rot = -2, size = 26, cite,
}) => {
  const {s, o} = useReveal(at);
  const sc = interpolate(s, [0, 1], [0.9, 1]);
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, transform: `rotate(${rot}deg) scale(${sc})`, opacity: o, background: '#fbf8ef', padding: '20px 22px', boxShadow: PHOTO_SHADOW}}>
      <div style={{position: 'absolute', top: -14, left: 28, width: 90, height: 26, background: EV.tape, transform: 'rotate(-3deg)'}} />
      <div style={{fontFamily: mono, fontSize: size, lineHeight: 1.35, color: EV.ink}}>{`„${text}"`}</div>
      {cite && <div style={{fontFamily: mono, fontSize: size * 0.62, color: EV.inkSoft, marginTop: 10, textAlign: 'right'}}>— {cite}</div>}
    </div>
  );
};

/** A hand-drawn ink circle around a small filing number/annotation. */
export const FileTag: React.FC<{text: string; x: number; y: number; at?: number; size?: number; color?: string}> = ({
  text, x, y, at = 0, size = 64, color = EV.ink,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const C = 2 * Math.PI * (size * 0.5);
  return (
    <div style={{position: 'absolute', left: x, top: y, width: size, height: size, transform: 'translate(-50%,-50%)'}}>
      <svg width={size} height={size} style={{position: 'absolute', left: 0, top: 0}}>
        <ellipse cx={size / 2} cy={size / 2} rx={size * 0.46} ry={size * 0.42} fill="none" stroke={color} strokeWidth={3} strokeDasharray={C} strokeDashoffset={C * (1 - p)} transform={`rotate(-12 ${size / 2} ${size / 2})`} />
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: cond, fontWeight: 700, fontSize: size * 0.42, color, opacity: interpolate(frame - at, [2, 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{text}</div>
    </div>
  );
};
