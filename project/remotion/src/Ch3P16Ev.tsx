import {AbsoluteFill, Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, MapPlate, Dossier, Stamp, Highlight, RedNote, RouteLine, FileTag, Seal, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 684.282;
export const C3P16_DURATION = Math.round(36.7 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3, DRAW = 0.3;
const LIGHT = '#f3efe4';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 7, show[1] - 8, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Full-screen photo (Ken-Burns), colour or B/W, with text gradient. */
const FullPhoto: React.FC<{src: string; from: number; dur: number; gray?: number}> = ({src, from, dur, gray = 0}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <FullPhotoInner src={src} dur={dur} gray={gray} />
  </Sequence>
);
const FullPhotoInner: React.FC<{src: string; dur: number; gray: number}> = ({src, dur, gray}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 6, dur - 7, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.06, 1.16]);
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <Img src={staticFile(`photos/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: gray ? 'grayscale(1) contrast(1.14) brightness(0.95)' : 'saturate(1.06) contrast(1.04)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(95deg, rgba(10,10,12,0.8) 0%, rgba(10,10,12,0.4) 42%, rgba(10,10,12,0.05) 72%)'}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 280px rgba(0,0,0,0.7)'}} />
    </AbsoluteFill>
  );
};
const OvBig: React.FC<{lines: string[]; y?: number; at: number; hl?: number; size?: number}> = ({lines, y = 300, at, hl = -1, size = 70}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame - at, [0, 7], [-20, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 80, top: y, opacity: o, transform: `translateX(${tx}px)`}}>
      {lines.map((l, i) => <div key={i} style={{fontFamily: cond, fontWeight: 700, fontSize: size, lineHeight: 1.0, textTransform: 'uppercase', color: i === hl ? EV.yellow : LIGHT, textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>{l}</div>)}
    </div>
  );
};

/** Lone Star emblem. */
const LoneStar: React.FC<{x: number; y: number; size: number; at: number}> = ({x, y, size, at}) => {
  const frame = useCurrentFrame();
  const {o, sc} = {o: interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}), sc: interpolate(frame - at, [0, 10], [0.6, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})};
  return (
    <svg style={{position: 'absolute', left: x, top: y, opacity: o, transform: `scale(${sc}) rotate(-8deg)`, filter: 'drop-shadow(3px 5px 6px rgba(20,16,10,0.4))'}} width={size} height={size} viewBox="0 0 100 100">
      <circle cx={50} cy={50} r={48} fill="none" stroke={EV.ink} strokeWidth={3} />
      <path d="M50,8 L61,38 L94,38 L67,58 L78,90 L50,70 L22,90 L33,58 L6,38 L39,38 Z" fill={EV.ink} />
    </svg>
  );
};

const BulletTrain: React.FC<{x: number; y: number; rot: number; at: number; w?: number}> = ({x, y, rot, at, w = 320}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const h = w * 70 / 300;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: o, transform: `translate(-50%,-50%) rotate(${rot}deg)`, filter: 'drop-shadow(3px 5px 6px rgba(20,16,10,0.45))'}}>
      <svg width={w} height={h} viewBox="0 0 300 70">
        <path d="M6,52 C36,26 86,20 150,20 L286,20 C293,20 296,24 296,30 L296,52 C296,56 293,58 288,58 L12,58 C7,58 5,56 6,52 Z" fill="#17140f" />
        <path d="M6,52 C36,26 86,20 150,20 L150,30 C92,30 44,34 22,52 Z" fill="#2a261d" />
        {[120, 150, 180, 210, 240, 270].map((wx) => <rect key={wx} x={wx} y={30} width={20} height={14} rx={2} fill="#cfc8b6" />)}
        <rect x={6} y={46} width={290} height={5} fill={EV.red} />
      </svg>
    </div>
  );
};

/** One zoom level of the governance map: full-screen map, zoom-in, label + STOPP. */
const ZoomLevel: React.FC<{src: string; label: string; from: number; dur: number; z0: number; z1: number}> = ({src, label, from, dur, z0, z1}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <ZoomInner src={src} label={label} dur={dur} z0={z0} z1={z1} />
  </Sequence>
);
const ZoomInner: React.FC<{src: string; label: string; dur: number; z0: number; z1: number}> = ({src, label, dur, z0, z1}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 5, dur - 6, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const z = interpolate(frame, [0, dur], [z0, z1]);
  const stampO = interpolate(frame, [dur * 0.42, dur * 0.42 + 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#1c1a14', opacity: io}}>
      <Img src={staticFile(`maps/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z})`, filter: 'sepia(0.4) contrast(1.08) brightness(0.92)'}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 320px rgba(0,0,0,0.8)'}} />
      <div style={{position: 'absolute', left: 80, top: 120, fontFamily: cond, fontWeight: 700, fontSize: 96, color: LIGHT, textTransform: 'uppercase', textShadow: '0 3px 20px rgba(0,0,0,0.9)'}}>{label}</div>
      <div style={{position: 'absolute', left: 84, top: 250, transform: 'rotate(-5deg)', opacity: stampO}}>
        <div style={{fontFamily: cond, fontWeight: 700, fontSize: 56, color: EV.red, border: `5px solid ${EV.red}`, padding: '6px 24px', background: 'rgba(243,239,228,0.92)'}}>KANN BLOCKIEREN ✋</div>
      </div>
    </AbsoluteFill>
  );
};

export const Ch3P16Ev: React.FC = () => {
  const frame = useCurrentFrame();
  const cost = Math.round(interpolate(frame, [f(8.2), f(11.0)], [12, 41], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  // Dallas / Houston on the big Texas map plate (cx1280,cy590,w920)
  const DAL: [number, number] = [1300, 430];
  const HOU: [number, number] = [1420, 650];

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* ── intro: full-screen Texas oil (line 180) ── */}
      <FullPhoto src="pumpjack.jpg" from={0} dur={f(3.3)} gray={0} />
      <Group show={[0, f(3.3)]}>
        <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 04 — TEXAS</div>
        <OvBig lines={['In Texas:', 'dieselbe Geschichte']} at={f(0.5)} y={300} hl={1} size={72} />
        <div style={{position: 'absolute', left: 84, bottom: 60, fontFamily: mono, fontSize: 24, color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>… nur mit anderen Vorzeichen</div>
      </Group>

      {/* ── Board A: big Texas map + the Dallas–Houston project ── */}
      <AbsoluteFill style={{opacity: interpolate(frame, [f(3.0), f(3.8), f(12.4), f(13.0)], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        <GraphPaper />
        <Halftone opacity={0.1} size={7} />
        <FileTag text="04" x={150} y={92} at={f(3.6)} size={62} />
        <TypeHeading text="Akte — Texas" x={210} y={78} size={26} at={f(3.4)} />
        <Seal text={'TEXAS\nCENTRAL\nprivat'} x={1830} y={130} at={f(4.0)} size={140} rot={-10} />

        <MapPlate cx={1290} cy={600} w={920} at={f(3.6)} rot={-1} src="texas.jpg" />
        <LoneStar x={1180} y={150} size={150} at={f(4.6)} />
        <Img src={staticFile('cutouts/pumpjack.png')} style={{position: 'absolute', left: 760, top: 740, width: 300, filter: 'drop-shadow(4px 8px 8px rgba(20,16,10,0.45))', opacity: interpolate(frame, [f(5.4), f(6.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />

        <RouteLine points={[DAL, HOU]} at={f(5.0)} drawFrames={20} arrow width={6} />
        <BulletTrain x={(DAL[0] + HOU[0]) / 2} y={(DAL[1] + HOU[1]) / 2} rot={60} at={f(6.4)} w={300} />
        <div style={{position: 'absolute', left: DAL[0] - 30, top: DAL[1] - 52, fontFamily: mono, fontWeight: 700, fontSize: 26, color: EV.ink, background: 'rgba(243,239,228,0.85)', padding: '2px 8px'}}>Dallas</div>
        <div style={{position: 'absolute', left: HOU[0] + 20, top: HOU[1] + 30, fontFamily: mono, fontWeight: 700, fontSize: 26, color: EV.ink, background: 'rgba(243,239,228,0.85)', padding: '2px 8px'}}>Houston</div>

        <Headline text="Privat: Dallas ↔ Houston" x={110} y={210} size={56} at={f(3.9)} />
        <div style={{position: 'absolute', left: 120, top: 470, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.1em', color: EV.inkSoft}}>GESCHÄTZTE KOSTEN</div>
        <div style={{position: 'absolute', left: 120, top: 510, fontFamily: cond, fontWeight: 700, fontSize: 150, lineHeight: 0.9, color: cost > 30 ? EV.red : EV.ink}}>${cost}<span style={{fontSize: 50, fontFamily: mono}}> Mrd.</span></div>
        <RedNote text="von $12 → über $40 Mrd." x={400} y={720} size={40} at={f(11.0)} rot={-3} />
      </AbsoluteFill>

      {/* ── Board B: investors flee (collage) ── */}
      <Group show={[f(12.7), f(19.8)]}>
        <GraphPaper />
        <Halftone opacity={0.1} size={7} />
        <TypeHeading text="Akte — Das Aus" x={150} y={120} size={26} at={f(12.9)} />
        <Crosshair x={1850} y={70} at={f(13.0)} />
        <Highlight x={120} y={290} w={820} at={f(13.2)} h={48} />
        <Headline text="Die Investoren springen ab" x={120} y={200} size={74} at={f(12.9)} />
        <Dossier x={120} y={420} w={700} at={f(13.8)} title="Projektende"
          rows={[
            {label: 'Investoren', value: 'ziehen sich zurück', hl: true},
            {label: 'Staatliche Förderung', value: 'gestrichen', hl: true},
            {label: 'Status', value: 'gescheitert'},
          ]} />
        <Stamp text="abgesprungen" x={1400} y={500} size={70} at={f(15.4)} rot={-8} />
        <TypeHeading text="Dahinter: ein wiederkehrendes Muster" x={120} y={780} size={30} at={f(17.6)} highlight />
      </Group>

      {/* ── governance map-zoom (lines 185-186) ── */}
      <ZoomLevel src="us1867.jpg" label="Bund" from={f(19.6)} dur={f(2.7)} z0={1.0} z1={1.18} />
      <ZoomLevel src="texas.jpg" label="Bundesstaat" from={f(22.2)} dur={f(2.7)} z0={1.05} z1={1.25} />
      <ZoomLevel src="texascounty.jpg" label="Bezirke" from={f(24.8)} dur={f(2.7)} z0={1.1} z1={1.3} />
      <ZoomLevel src="wacomap.jpg" label="Städte" from={f(27.4)} dur={f(2.9)} z0={1.1} z1={1.32} />
      <Group show={[f(19.6), f(30.2)]}>
        <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>VIER EBENEN REDEN MIT</div>
      </Group>

      {/* ── end: nobody can decide → years in court (full-screen gavel) ── */}
      <FullPhoto src="gavel.jpg" from={f(29.9)} dur={C3P16_DURATION - f(29.9)} gray={1} />
      <Group show={[f(29.9), C3P16_DURATION]}>
        <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 04 — DIE FOLGE</div>
        <OvBig lines={['Niemand kann einfach', 'entscheiden zu bauen']} at={f(30.4)} y={250} size={62} />
        <OvBig lines={['Was folgt: jahrelange', 'Gerichtsprozesse']} at={f(33.4)} y={470} hl={1} size={62} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P16_DURATION} volume={DRONE} />
      <Sfx src="whoosh.mp3" at={f(3.0)} volume={0.35} />
      <TypeClicks at={f(3.4)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(5.0)} volume={DRAW} />
      <Sfx src="sfx_paper.mp3" at={f(5.4)} volume={PAPER} />
      <Sfx src="whoosh.mp3" at={f(12.7)} volume={0.32} />
      <Sfx src="sfx_stamp.mp3" at={f(15.4)} volume={STAMP} />
      {[19.6, 22.2, 24.8, 27.4].map((t, i) => <Sfx key={i} src="whoosh.mp3" at={f(t)} volume={0.3} />)}
      {[20.7, 23.3, 25.9, 28.6].map((t, i) => <Sfx key={`s${i}`} src="sfx_stamp.mp3" at={f(t)} volume={0.4} />)}
      <Sfx src="impact.mp3" at={f(29.9)} volume={0.45} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
