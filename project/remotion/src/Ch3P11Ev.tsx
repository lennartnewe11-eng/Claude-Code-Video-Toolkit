import {AbsoluteFill, Audio, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, Highlight, RedNote, Stamp, FileTag, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 512.886;
export const C3P11_DURATION = Math.round(29.0 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, DRAW = 0.3;
const LIGHT = '#f3efe4';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 7, show[1] - 8, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Full-bleed video, played once (no loop), B/W grain + vignette. */
const FBOnce: React.FC<{src: string; from: number; dur: number}> = ({src, from, dur}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <FBInner src={src} dur={dur} />
  </Sequence>
);
const FBInner: React.FC<{src: string; dur: number}> = ({src, dur}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 8, dur - 8, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.05, 1.12]);
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <OffthreadVideo src={staticFile(`clips/${src}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: 'grayscale(1) contrast(1.15) brightness(1.0)'}} />
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.38}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 300px rgba(0,0,0,0.88)'}} />
    </AbsoluteFill>
  );
};

const OvBig: React.FC<{text: string; x: number; y: number; size: number; at: number; color?: string}> = ({text, x, y, size, at, color = LIGHT}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame - at, [0, 7], [-22, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `translateX(${tx}px)`, fontFamily: cond, fontWeight: 700, fontSize: size, lineHeight: 0.96, textTransform: 'uppercase', color, textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>{text}</div>;
};

/** Two contrasting track lines: winding (✗) vs dead-straight (✓). */
const TrackContrast: React.FC<{from: number}> = ({from}) => {
  const frame = useCurrentFrame();
  const dw = interpolate(frame - from, [0, 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sw = interpolate(frame - from - 20, [0, 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const WIND = 'M0 40 C 80 0, 160 80, 240 40 S 400 0, 480 40 S 640 80, 760 40';
  return (
    <svg style={{position: 'absolute', left: 150, top: 470}} width={820} height={300}>
      {/* winding */}
      <path d={WIND} fill="none" stroke="#9a8f78" strokeWidth={8} strokeDasharray={1100} strokeDashoffset={1100 * (1 - dw)} />
      <text x={0} y={-12} fontFamily={mono} fontWeight={700} fontSize={22} fill={EV.ink}>ALTE GLEISE — AUFRÜSTEN?</text>
      {dw > 0.95 && <text x={770} y={48} fontFamily={cond} fontWeight={700} fontSize={70} fill={EV.red}>✗</text>}
      {/* straight */}
      <g transform="translate(0,210)">
        <rect x={-6} y={-22} width={772} height={44} fill={EV.yellow} opacity={0.85 * sw} transform="skewX(-4)" />
        <line x1={0} y1={0} x2={760 * sw} y2={0} stroke={EV.ink} strokeWidth={9} />
        {Array.from({length: 26}).map((_, i) => <line key={i} x1={i * 30} y1={-14} x2={i * 30} y2={14} stroke={EV.ink} strokeWidth={3} opacity={i / 26 < sw ? 1 : 0} />)}
        <text x={0} y={-40} fontFamily={mono} fontWeight={700} fontSize={22} fill={EV.ink}>NEUE, SCHNURGERADE STRECKE</text>
        {sw > 0.95 && <text x={772} y={18} fontFamily={cond} fontWeight={700} fontSize={70} fill={EV.ink}>✓</text>}
      </g>
    </svg>
  );
};

export const Ch3P11Ev: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />

      {/* full-screen Shinkansen footage (phase B) */}
      <FBOnce src="shinkansen2.mp4" from={f(3.7)} dur={f(9.2)} />

      {/* ── A (collage): Japan did it differently ── */}
      <Group show={[0, f(4.0)]}>
        <FileTag text="3·h" x={150} y={92} at={f(0.4)} size={62} />
        <TypeHeading text="Akte — Japans Weg" x={210} y={78} size={26} at={f(0.2)} />
        <Crosshair x={1850} y={70} at={f(0.8)} />
        <Highlight x={120} y={300} w={960} at={f(1.0)} h={50} />
        <Headline text="Japan machte es anders" x={120} y={200} size={92} at={f(0.6)} />
        <TypeHeading text="Ein entscheidender Schritt" x={125} y={420} size={28} at={f(1.8)} color="#5d574c" />
      </Group>

      {/* ── B (full-screen footage): the brand-new straight line ── */}
      <Group show={[f(3.7), f(12.9)]}>
        <div style={{position: 'absolute', left: 72, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 03 — JAPANS WEG</div>
        <OvBig text="Eine komplett neue," x={72} y={150} size={62} at={f(4.4)} />
        <OvBig text="schnurgerade Strecke" x={72} y={222} size={62} at={f(4.8)} color={EV.yellow} />
        <OvBig text="Einzig für Tempo gebaut" x={72} y={400} size={46} at={f(9.8)} />
        <div style={{position: 'absolute', left: 72, bottom: 60, fontFamily: mono, fontSize: 24, letterSpacing: '0.06em', color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>Shinkansen, Japan — eigene Trasse</div>
      </Group>

      {/* ── C (collage): Shinkansen = main line ── */}
      <Group show={[f(12.6), f(17.2)]}>
        <TypeHeading text="Akte — Wortbedeutung" x={150} y={120} size={26} at={f(12.8)} />
        <Crosshair x={1850} y={70} at={f(12.9)} />
        <Headline text="Shinkansen" x={150} y={210} size={96} at={f(12.9)} />
        <div style={{position: 'absolute', left: 1180, top: 200, fontFamily: cond, fontWeight: 700, fontSize: 150, color: EV.ink, opacity: interpolate(frame, [f(13.2), f(13.9)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>新幹線</div>
        {[['新', 'neu'], ['幹', 'Haupt-'], ['線', 'Linie']].map(([k, m], i) => (
          <div key={i} style={{position: 'absolute', left: 160 + i * 260, top: 470, opacity: interpolate(frame, [f(14.0 + i * 0.5), f(14.6 + i * 0.5)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
            <div style={{fontFamily: cond, fontWeight: 700, fontSize: 90, color: EV.ink}}>{k}</div>
            <div style={{fontFamily: mono, fontSize: 26, color: EV.inkSoft, letterSpacing: '0.08em'}}>{m}</div>
          </div>
        ))}
        <Highlight x={150} y={720} w={640} at={f(15.6)} h={48} />
        <Headline text="= »Hauptlinie«" x={150} y={690} size={72} at={f(15.5)} />
        <RedNote text="kein Anhängsel — das Rückgrat" x={900} y={730} size={38} at={f(16.2)} rot={-4} />
      </Group>

      {/* ── D (collage): the central insight ── */}
      <Group show={[f(16.8), C3P11_DURATION]}>
        <TypeHeading text="Die zentrale Erkenntnis" x={150} y={170} size={30} at={f(17.0)} highlight />
        <Headline text="Hochgeschwindigkeit ist kein Zug," x={150} y={300} size={62} at={f(20.6)} />
        <Headline text="den man auf alte Schienen setzt" x={150} y={380} size={62} at={f(21.0)} />
        <TrackContrast from={f(17.4)} />
        {/* the jet-engine train: exactly that mistake */}
        <TapedPhoto src="m497.jpg" cx={1480} cy={300} w={560} rot={3} at={f(21.6)} caption="M-497: ein Jet auf alten Gleisen" />
        <RedNote text="genau dieser Irrtum" x={1320} y={120} size={36} at={f(22.6)} rot={-6} />
        <Stamp text="eigene Trasse · Planung · Geduld" x={620} y={870} size={40} at={f(24.4)} rot={-4} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P11_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="whoosh.mp3" at={f(3.7)} volume={0.4} />
      <Sfx src="whoosh.mp3" at={f(12.6)} volume={0.35} />
      <TypeClicks at={f(12.8)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(17.4)} volume={DRAW} />
      <Sfx src="sfx_draw.mp3" at={f(18.4)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(24.4)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
