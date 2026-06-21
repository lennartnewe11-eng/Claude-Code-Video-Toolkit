import {AbsoluteFill, Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, Dossier, Stamp, Highlight, RedNote, FileTag, Seal, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 542.124;
export const C3P12_DURATION = Math.round(38.9 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3, DRAW = 0.3;
const LIGHT = '#f3efe4';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Full-screen archival photo with Ken-Burns push, B/W grain and vignette. */
const FullPhoto: React.FC<{src: string; folder?: string; from: number; dur: number}> = ({src, folder = 'photos', from, dur}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <FullPhotoInner src={src} folder={folder} dur={dur} />
  </Sequence>
);
const FullPhotoInner: React.FC<{src: string; folder: string; dur: number}> = ({src, folder, dur}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 10, dur - 10, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.06, 1.18]);
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <Img src={staticFile(`${folder}/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: 'grayscale(1) contrast(1.12) brightness(0.96)'}} />
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.35}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 320px rgba(0,0,0,0.9)'}} />
    </AbsoluteFill>
  );
};
const OvBig: React.FC<{text: string; x: number; y: number; size: number; at: number; color?: string}> = ({text, x, y, size, at, color = LIGHT}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame - at, [0, 7], [-22, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `translateX(${tx}px)`, fontFamily: cond, fontWeight: 700, fontSize: size, lineHeight: 0.96, textTransform: 'uppercase', color, textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>{text}</div>;
};
const Cap: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', left: 72, bottom: 60, fontFamily: mono, fontSize: 24, letterSpacing: '0.06em', color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>{text}</div>
);

/** A stock/value line crashing to zero (built-up, draws down). */
const CrashChart: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const W = 560, H = 300;
  const p = interpolate(frame - from, [0, 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const path = `M0 40 L120 70 L220 60 L320 130 L420 220 L${W} ${H - 6}`;
  const dot = [0, 120, 220, 320, 420, W];
  const dy = [40, 70, 60, 130, 220, H - 6];
  const idx = Math.min(5, Math.floor(p * 5.999));
  return (
    <svg style={{position: 'absolute', left: x, top: y}} width={W + 20} height={H + 20}>
      <line x1={0} y1={0} x2={0} y2={H} stroke={EV.ink} strokeWidth={3} />
      <line x1={0} y1={H} x2={W} y2={H} stroke={EV.ink} strokeWidth={3} />
      <path d={path} fill="none" stroke={EV.red} strokeWidth={6} strokeDasharray={900} strokeDashoffset={900 * (1 - p)} />
      <circle cx={dot[idx]} cy={dy[idx]} r={8} fill={EV.red} />
      <text x={W - 30} y={H - 16} fontFamily={cond} fontWeight={700} fontSize={40} fill={EV.red} opacity={p > 0.9 ? 1 : 0}>$0</text>
    </svg>
  );
};

/** A simple drawn Amtrak-style arrow mark. */
const ArrowMark: React.FC<{x: number; y: number; at: number}> = ({x, y, at}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <svg style={{position: 'absolute', left: x, top: y, opacity: o}} width={320} height={200}>
      <path d="M20 150 L150 30 L150 80 L300 80 L300 130 L150 130 L150 178 Z" fill={EV.red} stroke={EV.ink} strokeWidth={4} />
    </svg>
  );
};

export const Ch3P12Ev: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />

      {/* full-screen photos (A, D) */}
      <FullPhoto src="squandered.jpg" folder="footage" from={0} dur={f(5.2)} />
      <FullPhoto src="passengertrain.jpg" from={f(26.6)} dur={C3P12_DURATION - f(26.6)} />

      {/* ── A (full-screen): the system collapses ── */}
      <Group show={[0, f(5.2)]}>
        <div style={{position: 'absolute', left: 72, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 03 — DER ZUSAMMENBRUCH</div>
        <OvBig text="Während Amerika noch baute," x={72} y={300} size={56} at={f(0.6)} />
        <OvBig text="brach das System zusammen" x={72} y={372} size={56} at={f(1.4)} color={EV.yellow} />
        <Cap text="verlassene Bahnstrecke" />
      </Group>

      {/* ── B (collage): Penn Central bankruptcy ── */}
      <Group show={[f(4.9), f(16.2)]}>
        <FileTag text="3·i" x={150} y={92} at={f(5.2)} size={62} />
        <TypeHeading text="Akte — Der Zusammenbruch" x={210} y={78} size={26} at={f(5.0)} />
        <Crosshair x={1500} y={70} at={f(5.4)} />
        <Seal text={'INSOLVENZ\n1970'} x={1810} y={120} at={f(5.6)} size={150} rot={-10} />

        <Highlight x={120} y={290} w={760} at={f(5.6)} h={48} />
        <Headline text="Penn Central: Pleite" x={120} y={200} size={84} at={f(5.3)} />
        <RedNote text="1970" x={300} y={420} size={64} at={f(5.8)} rot={-6} />

        <Dossier x={120} y={520} w={620} at={f(9.4)} title="Bilanz"
          rows={[
            {label: 'Größter Bahnkonzern', value: 'der USA', hl: true},
            {label: 'Status', value: 'zahlungsunfähig'},
            {label: 'Rekord', value: 'größte Pleite bis dahin', hl: true},
          ]} />
        <CrashChart x={1180} y={300} from={f(6.4)} />
        <Stamp text="bankrott" x={1430} y={690} size={64} at={f(12.0)} rot={-8} />
      </Group>

      {/* ── C (collage): Amtrak 1971 ── */}
      <Group show={[f(15.9), f(26.9)]}>
        <TypeHeading text="Akte — Die staatliche Antwort" x={150} y={120} size={26} at={f(16.1)} />
        <Crosshair x={1850} y={70} at={f(16.2)} />
        <Highlight x={150} y={300} w={560} at={f(16.4)} h={50} />
        <Headline text="1971: Amtrak" x={150} y={210} size={92} at={f(16.1)} />
        <ArrowMark x={150} y={420} at={f(17.0)} />

        <Dossier x={620} y={420} w={680} at={f(17.6)} title="Halbstaatliche Gesellschaft"
          rows={[
            {label: 'Übernimmt', value: 'den Personenverkehr', hl: true},
            {label: 'Ab', value: '1971'},
            {label: 'Darunter auch', value: 'der Metroliner', hl: true},
          ]} />
        <TypeHeading text="Befreit die privaten Konzerne von der Last" x={150} y={700} size={28} at={f(22.0)} highlight />
        <Stamp text="Personenverkehr = Last" x={520} y={820} size={42} at={f(24.0)} rot={-5} />
      </Group>

      {/* ── D (full-screen): not an investment — a hospice ── */}
      <Group show={[f(26.6), C3P12_DURATION]}>
        <div style={{position: 'absolute', left: 72, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 03 — DAS FAZIT</div>
        <OvBig text="Keine Investition" x={72} y={300} size={70} at={f(33.4)} />
        <OvBig text="in die Zukunft —" x={72} y={384} size={70} at={f(33.8)} />
        <OvBig text="eher eine Sterbebegleitung" x={72} y={500} size={58} at={f(36.6)} color={EV.yellow} />
        <Cap text="der US-Personenverkehr — verwaltet, nicht erneuert" />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P12_DURATION} volume={DRONE} />
      <Sfx src="whoosh.mp3" at={f(0.0)} volume={0.35} />
      <TypeClicks at={f(5.0)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(6.4)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(12.0)} volume={STAMP} />
      <Sfx src="whoosh.mp3" at={f(15.9)} volume={0.35} />
      <TypeClicks at={f(16.1)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(24.0)} volume={STAMP} />
      <Sfx src="whoosh.mp3" at={f(26.6)} volume={0.35} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
