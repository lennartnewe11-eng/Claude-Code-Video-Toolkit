import {AbsoluteFill, Audio, interpolate, Loop, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, Dossier, Stamp, Highlight, RedNote, RouteLine, FileTag, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 449.142;
export const C3P9_DURATION = Math.round(32.4 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3, DRAW = 0.3;
const LIGHT = '#f3efe4';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 7, show[1] - 8, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Full-bleed archival video with B/W grain, vignette and in/out fade. */
const FB: React.FC<{src: string; from: number; dur: number; loopFrames: number; gray?: number}> = ({src, from, dur, loopFrames, gray = 1}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <FBInner src={src} dur={dur} loopFrames={loopFrames} gray={gray} />
  </Sequence>
);
const FBInner: React.FC<{src: string; dur: number; loopFrames: number; gray: number}> = ({src, dur, loopFrames, gray}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 8, dur - 8, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.05, 1.13]);
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <Loop durationInFrames={loopFrames} layout="none">
        <OffthreadVideo src={staticFile(`clips/${src}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: `grayscale(${gray}) contrast(1.14) brightness(1.0)`}} />
      </Loop>
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.38}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 300px rgba(0,0,0,0.88)'}} />
    </AbsoluteFill>
  );
};

const Cap: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', left: 70, bottom: 60, fontFamily: mono, fontSize: 24, letterSpacing: '0.06em', color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>{text}</div>
);
const OvBig: React.FC<{text: string; x: number; y: number; size: number; at: number; color?: string}> = ({text, x, y, size, at, color = LIGHT}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame - at, [0, 7], [-24, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `translateX(${tx}px)`, fontFamily: cond, fontWeight: 700, fontSize: size, lineHeight: 0.95, textTransform: 'uppercase', color, textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>{text}</div>;
};

/** A spinning clock — time running out. */
const Clock: React.FC<{x: number; y: number; r: number; at: number}> = ({x, y, r, at}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const mh = (frame - at) * 9, hh = (frame - at) * 0.9;
  return (
    <svg style={{position: 'absolute', left: x - r - 14, top: y - r - 14, opacity: o}} width={(r + 14) * 2} height={(r + 14) * 2}>
      <g transform={`translate(${r + 14} ${r + 14})`}>
        <circle r={r} fill="#fbf8ef" stroke={EV.ink} strokeWidth={5} />
        {Array.from({length: 12}).map((_, i) => <line key={i} x1={0} y1={-r + 6} x2={0} y2={-r + 16} stroke={EV.ink} strokeWidth={3} transform={`rotate(${i * 30})`} />)}
        <line x1={0} y1={0} x2={0} y2={-r * 0.55} stroke={EV.ink} strokeWidth={6} transform={`rotate(${hh})`} />
        <line x1={0} y1={0} x2={0} y2={-r * 0.82} stroke={EV.red} strokeWidth={4} transform={`rotate(${mh})`} />
        <circle r={6} fill={EV.ink} />
      </g>
    </svg>
  );
};

/** Calendar pages piling up — time slipping away (built-up motif). */
const PagePile: React.FC<{x: number; y: number; from: number; years: string[]}> = ({x, y, from, years}) => {
  const frame = useCurrentFrame();
  const cw = 150, ch = 110, step = 30;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: cw + 80, height: ch + years.length * step}}>
      {years.map((yr, i) => {
        const appear = from + i * 8;
        const o = interpolate(frame - appear, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const ty = interpolate(frame - appear, [0, 7], [-40, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const rot = (i % 2 ? 1 : -1) * (3 + (i % 3));
        const top = (years.length - 1 - i) * step;
        return (
          <div key={i} style={{position: 'absolute', left: (i * 11) % 26, top: top + ty, width: cw, height: ch, opacity: o, transform: `rotate(${rot}deg)`, background: '#fbf8ef', boxShadow: '2px 4px 8px rgba(20,16,10,0.3)', zIndex: 50 - top}}>
            <div style={{height: 26, background: EV.red, opacity: 0.85}} />
            <div style={{textAlign: 'center', fontFamily: cond, fontWeight: 700, fontSize: 54, color: EV.ink, marginTop: 12}}>{yr}</div>
          </div>
        );
      })}
    </div>
  );
};

const Check: React.FC<{text: string; x: number; y: number; at: number}> = ({text, x, y, at}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const hw = interpolate(frame - at - 3, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, display: 'flex', alignItems: 'center'}}>
      <span style={{fontFamily: cond, fontWeight: 700, fontSize: 50, color: EV.yellow, marginRight: 18, textShadow: '0 2px 10px rgba(0,0,0,0.8)'}}>✓</span>
      <span style={{position: 'relative', fontFamily: cond, fontWeight: 700, fontSize: 50, color: LIGHT, textTransform: 'uppercase', textShadow: '0 2px 14px rgba(0,0,0,0.85)'}}>
        <span style={{position: 'absolute', left: -6, top: '20%', height: '64%', width: `calc(${hw * 100}% + 12px)`, background: EV.yellow, opacity: 0.28, zIndex: -1}} />
        {text}
      </span>
    </div>
  );
};

export const Ch3P9Ev: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />

      {/* full-bleed footage (C, D) */}
      <FB src="oldline.mp4" from={f(11.8)} dur={f(11.8)} loopFrames={f(8)} />
      <FB src="tgv.mp4" from={f(23.2)} dur={C3P9_DURATION - f(23.2)} loopFrames={f(5)} />

      {/* ── Board A (collage): the dispute wastes time ── */}
      <Group show={[0, f(6.6)]}>
        <FileTag text="3·f" x={150} y={92} at={f(0.4)} size={62} />
        <TypeHeading text="Akte — Verlorene Zeit" x={210} y={78} size={26} at={f(0.2)} />
        <Crosshair x={1850} y={70} at={f(0.8)} />
        <Highlight x={120} y={290} w={760} at={f(1.0)} h={48} />
        <Headline text="Der Streit kostet Zeit" x={120} y={200} size={82} at={f(0.6)} />
        <PagePile x={150} y={430} from={f(2.0)} years={['1965', '1966', '1967', '1968', '1969']} />
        <Clock x={1480} y={460} r={150} at={f(1.0)} />
        <TypeHeading text="Kein Spielraum mehr für einen neuen Zug" x={620} y={760} size={28} at={f(3.4)} highlight />
        <Stamp text="Zeit verloren" x={1480} y={760} size={48} at={f(5.0)} rot={-7} />
      </Group>

      {/* ── Board B (collage): the stop-gap ── */}
      <Group show={[f(6.2), f(12.2)]}>
        <TypeHeading text="Akte — Die Notlösung" x={150} y={78} size={26} at={f(6.4)} />
        <Crosshair x={1850} y={70} at={f(6.6)} />
        <Highlight x={120} y={250} w={660} at={f(6.9)} h={48} />
        <Headline text="Die Notlösung" x={120} y={160} size={88} at={f(6.7)} />

        {/* concept: existing car + speed = compromise */}
        <div style={{position: 'absolute', left: 150, top: 470, fontFamily: cond, fontWeight: 700, fontSize: 60, color: EV.ink, textTransform: 'uppercase', opacity: interpolate(frame, [f(7.6), f(8.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>vorhandene Waggons</div>
        <RedNote text="→ kurzerhand umgebaut" x={420} y={580} size={44} at={f(8.6)} rot={-3} />
        <Dossier x={1080} y={420} w={620} at={f(9.0)} title="Kompromiss statt Neubau"
          rows={[
            {label: 'Zeit', value: 'keine mehr', hl: true},
            {label: 'Lösung', value: 'Umbau', hl: true},
            {label: 'Neuer Zug', value: 'gestrichen'},
          ]} />
        <Stamp text="Notlösung" x={520} y={760} size={110} at={f(9.4)} rot={-8} />
      </Group>

      {/* ── Board C (footage): the old winding line ── */}
      <Group show={[f(11.8), f(23.6)]}>
        <div style={{position: 'absolute', left: 70, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 03 — DAS KERNPROBLEM</div>
        <OvBig text="Das größte Problem" x={72} y={150} size={64} at={f(12.2)} />
        <OvBig text="Die alte, gewundene Trasse" x={72} y={330} size={70} at={f(15.4)} />
        <div style={{position: 'absolute', left: 76, top: 440, opacity: interpolate(frame, [f(16.4), f(17.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
          <span style={{position: 'relative', fontFamily: cond, fontWeight: 700, fontSize: 70, color: EV.ink, textTransform: 'uppercase'}}>
            <span style={{position: 'absolute', left: -8, top: '14%', height: '74%', width: 'calc(100% + 16px)', background: EV.yellow, zIndex: -1, transform: 'skewX(-6deg)'}} />
            dieselben Gleise wie vor 100 Jahren
          </span>
        </div>
        {/* curve annotation drawn over the footage (collage × footage) */}
        <RouteLine points={[[980, 470], [1080, 560], [1240, 640], [1420, 690], [1620, 700]]} at={f(18.0)} drawFrames={26} arrow width={6} />
        <RedNote text="gewunden · langsam" x={1380} y={600} size={40} at={f(20.2)} rot={-6} />
        <Cap text="alte Strecke — seit dem 19. Jahrhundert" />
      </Group>

      {/* ── Board D (footage + collage checklist): what real HSR needs ── */}
      <Group show={[f(23.2), C3P9_DURATION]}>
        <div style={{position: 'absolute', left: 70, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 03 — DER MASSSTAB</div>
        <OvBig text="So sieht echte" x={72} y={150} size={60} at={f(23.6)} />
        <OvBig text="Hochgeschwindigkeit aus" x={72} y={222} size={60} at={f(23.9)} color={EV.yellow} />
        <Check text="lückenlos verschweißte Schienen" x={90} y={430} at={f(27.2)} />
        <Check text="möglichst sanfte Kurven" x={90} y={530} at={f(28.4)} />
        <Check text="stabile Stromversorgung" x={90} y={630} at={f(29.6)} />
        <Cap text="Europa & Japan: eigene, neue Trassen" />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P9_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(2.0)} volume={0.22} />
      <Sfx src="sfx_paper.mp3" at={f(2.6)} volume={0.2} />
      <Sfx src="sfx_stamp.mp3" at={f(5.0)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(9.4)} volume={STAMP} />
      <Sfx src="whoosh.mp3" at={f(11.8)} volume={0.4} />
      <Sfx src="sfx_draw.mp3" at={f(18.0)} volume={DRAW} />
      <Sfx src="whoosh.mp3" at={f(23.2)} volume={0.4} />
      <Sfx src="sfx_stamp.mp3" at={f(27.2)} volume={0.3} />
      <Sfx src="sfx_stamp.mp3" at={f(28.4)} volume={0.3} />
      <Sfx src="sfx_stamp.mp3" at={f(29.6)} volume={0.3} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
