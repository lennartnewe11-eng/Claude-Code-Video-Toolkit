import {AbsoluteFill, Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, Highlight, FileTag, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 720.96;
export const C3P17_DURATION = Math.round(33.4 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, DRONE = 0.06, DRAW = 0.3, PAPER = 0.3;
const LIGHT = '#f3efe4';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 7, show[1] - 8, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const FullPhoto: React.FC<{src: string; from: number; dur: number; gray?: number}> = ({src, from, dur, gray = 0}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <FullPhotoInner src={src} dur={dur} gray={gray} />
  </Sequence>
);
const FullPhotoInner: React.FC<{src: string; dur: number; gray: number}> = ({src, dur, gray}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 6, dur - 7, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.06, 1.15]);
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <Img src={staticFile(`photos/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: gray ? 'grayscale(1) contrast(1.14)' : 'saturate(1.06) contrast(1.04)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(95deg, rgba(10,10,12,0.78) 0%, rgba(10,10,12,0.38) 44%, rgba(10,10,12,0.05) 74%)'}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 280px rgba(0,0,0,0.65)'}} />
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
const Cap: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', left: 84, bottom: 60, fontFamily: mono, fontSize: 24, color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>{text}</div>
);
const BulletTrain: React.FC<{x: number; y: number; rot?: number; at: number; w?: number}> = ({x, y, rot = 0, at, w = 300}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const h = w * 70 / 300;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: o, transform: `translate(-50%,-50%) rotate(${rot}deg)`, filter: 'drop-shadow(3px 5px 6px rgba(20,16,10,0.4))'}}>
      <svg width={w} height={h} viewBox="0 0 300 70">
        <path d="M6,52 C36,26 86,20 150,20 L286,20 C293,20 296,24 296,30 L296,52 C296,56 293,58 288,58 L12,58 C7,58 5,56 6,52 Z" fill="#17140f" />
        <path d="M6,52 C36,26 86,20 150,20 L150,30 C92,30 44,34 22,52 Z" fill="#2a261d" />
        {[120, 150, 180, 210, 240, 270].map((wx) => <rect key={wx} x={wx} y={30} width={20} height={14} rx={2} fill="#cfc8b6" />)}
        <rect x={6} y={46} width={290} height={5} fill={EV.red} />
      </svg>
    </div>
  );
};

/** Cross-section: highway lanes | rail median | highway lanes (the clever trick). */
const MedianDiagram: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const W = 1080, laneH = 150;
  const dashShift = (frame * 6) % 80;
  const railO = interpolate(frame - from, [0, 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const Lane: React.FC<{top: number; dir: number}> = ({top, dir}) => (
    <div style={{position: 'absolute', left: 0, top, width: W, height: laneH, background: '#3c3a33'}}>
      <div style={{position: 'absolute', top: laneH / 2 - 3, left: 0, width: W, height: 6, backgroundImage: 'repeating-linear-gradient(90deg, #e8df0a 0 40px, transparent 40px 80px)', backgroundPositionX: dir * dashShift}} />
    </div>
  );
  return (
    <div style={{position: 'absolute', left: x, top: y, width: W, height: laneH * 2 + 120}}>
      <Lane top={0} dir={1} />
      <div style={{position: 'absolute', left: 8, top: 12, fontFamily: mono, fontWeight: 700, fontSize: 22, color: LIGHT}}>I-15 · Autobahn →</div>
      {/* median with rail + train */}
      <div style={{position: 'absolute', left: 0, top: laneH, width: W, height: 120, background: '#cfc8b6', borderTop: `4px solid ${EV.ink}`, borderBottom: `4px solid ${EV.ink}`, opacity: railO}}>
        <div style={{position: 'absolute', left: 0, top: 64, width: W, height: 5, background: EV.ink}} />
        <div style={{position: 'absolute', left: 0, top: 80, width: W, height: 5, background: EV.ink}} />
        <div style={{position: 'absolute', left: 12, top: 8, fontFamily: cond, fontWeight: 700, fontSize: 26, color: EV.ink, textTransform: 'uppercase'}}>Neue HGV-Trasse im Mittelstreifen</div>
      </div>
      <Lane top={laneH + 120} dir={-1} />
      <div style={{position: 'absolute', left: 8, top: laneH * 2 + 120 - 34, fontFamily: mono, fontWeight: 700, fontSize: 22, color: LIGHT}}>← I-15 · Autobahn</div>
      <BulletTrain x={interpolate(frame, [from, from + f(5)], [-160, W + 160], {extrapolateLeft: 'clamp'})} y={laneH + 60} rot={0} at={from} w={360} />
    </div>
  );
};

/** Wordless "bypass" diagram: a dead-straight elevated Brightline line that
 *  sails over the three hurdles that stopped the others (land, lawsuits,
 *  old winding track). */
const ObstacleBypass: React.FC<{from: number}> = ({from}) => {
  const frame = useCurrentFrame();
  const deckY = 560, groundY = 830, x0 = 130, x1 = 1380;
  const draw = interpolate(frame - from, [0, 26], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const obO = interpolate(frame - from, [4, 16], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const pillars = [x0 + 30, 460, 760, 1060, x1 - 30];
  // faded obstacle icons sitting on the ground
  const Obstacle: React.FC<{cx: number; kind: 'land' | 'law' | 'curve'}> = ({cx, kind}) => (
    <g opacity={obO * 0.5} transform={`translate(${cx},${groundY})`} stroke={EV.ink} fill="none" strokeWidth={4}>
      {kind === 'land' && [-60, -20, 20, 60].map((dx) => <g key={dx}><rect x={dx - 14} y={-44} width={28} height={44} /><path d={`M${dx - 16} -44 L${dx} -60 L${dx + 16} -44`} /></g>)}
      {kind === 'law' && <g><line x1={-46} y1={0} x2={46} y2={0} strokeWidth={6} /><line x1={-30} y1={-8} x2={20} y2={-58} strokeWidth={10} strokeLinecap="round" /><rect x={6} y={-78} width={44} height={24} rx={4} transform="rotate(-45 28 -66)" fill={EV.ink} /></g>}
      {kind === 'curve' && <path d="M-80,0 C -50,-46 -10,-46 20,-12 C 44,16 80,8 96,-30" strokeWidth={6} />}
    </g>
  );
  return (
    <svg style={{position: 'absolute', left: 0, top: 0}} width={1920} height={1080}>
      {/* the three hurdles (faded) */}
      <Obstacle cx={330} kind="land" />
      <Obstacle cx={760} kind="law" />
      <Obstacle cx={1130} kind="curve" />
      <line x1={120} y1={groundY} x2={1400} y2={groundY} stroke={EV.ink} strokeWidth={3} opacity={obO * 0.5} />
      {/* the straight elevated Brightline line, sailing over everything */}
      {pillars.map((px, i) => <line key={i} x1={px} y1={deckY + 8} x2={px} y2={groundY} stroke={EV.ink} strokeWidth={6} opacity={interpolate(frame - from, [10 + i * 3, 16 + i * 3], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />)}
      <line x1={x0} y1={deckY} x2={x1} y2={deckY} stroke={EV.ink} strokeWidth={12} strokeDasharray={x1 - x0} strokeDashoffset={(x1 - x0) * (1 - draw)} strokeLinecap="round" />
      <line x1={x0} y1={deckY + 16} x2={x0 + (x1 - x0) * draw} y2={deckY + 16} stroke={EV.red} strokeWidth={4} />
    </svg>
  );
};

export const Ch3P17Ev: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* ── intro: it's actually being built (189) ── */}
      <FullPhoto src="blwest.jpg" from={0} dur={f(7.3)} gray={0} />
      <Group show={[0, f(7.3)]}>
        <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 05 — DIE AUSNAHME</div>
        <OvBig lines={['Doch eines wird', 'tatsächlich gebaut']} at={f(0.5)} y={280} hl={1} size={72} />
        <OvBig lines={['Brightline West', 'Las Vegas ↔ Südkalifornien']} at={f(3.2)} y={520} size={48} />
        <Cap text="Brightline West — Bau der Station Las Vegas, 2025" />
      </Group>

      {/* ── Board B: the clever trick — the highway median ── */}
      <FullPhoto src="i15.jpg" from={f(7.1)} dur={f(4.2)} gray={0} />
      <Group show={[f(7.1), f(11.5)]}>
        <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>WARUM GERADE DIESES?</div>
        <OvBig lines={['Es weicht allen', 'Hürden geschickt aus']} at={f(7.5)} y={300} hl={1} size={66} />
        <Cap text="entlang der bestehenden I-15 durch die Wüste" />
      </Group>

      <Group show={[f(11.3), f(20.9)]}>
        <GraphPaper />
        <Halftone opacity={0.1} size={7} />
        <FileTag text="05" x={150} y={92} at={f(11.6)} size={62} />
        <TypeHeading text="Akte — Der Trick" x={210} y={78} size={26} at={f(11.5)} />
        <Crosshair x={1850} y={70} at={f(11.8)} />
        <Highlight x={120} y={250} w={1000} at={f(12.0)} h={48} />
        <Headline text="Im Mittelstreifen der Autobahn" x={120} y={160} size={64} at={f(11.7)} />
        <MedianDiagram x={420} y={430} from={f(13.0)} />
      </Group>

      {/* ── Board C: sailing over the hurdles + the 1965 lesson ── */}
      <Group show={[f(20.6), C3P17_DURATION]}>
        <GraphPaper />
        <Halftone opacity={0.1} size={7} />
        <TypeHeading text="Akte — Warum es gelingt" x={150} y={120} size={26} at={f(20.8)} />
        <Crosshair x={1850} y={70} at={f(21.0)} />
        <Highlight x={120} y={250} w={620} at={f(21.2)} h={48} />
        <Headline text="Über alle Hürden hinweg" x={120} y={160} size={72} at={f(20.9)} />

        <ObstacleBypass from={f(21.6)} />
        <BulletTrain x={interpolate(frame, [f(22.2), f(27.2)], [60, 1440], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} y={560} at={f(22.2)} w={300} />

        {/* the 1965 lesson, finally applied — a dotted connector, no stamp */}
        <TapedPhoto src="metroliner.jpg" cx={1560} cy={760} w={440} rot={3} at={f(27.0)} caption="1965" />
        <svg style={{position: 'absolute', left: 0, top: 0}} width={1920} height={1080}>
          <path d="M1440,575 C 1500,640 1540,680 1560,700" fill="none" stroke={EV.red} strokeWidth={4} strokeDasharray="3 10" strokeLinecap="round" opacity={interpolate(frame, [f(28.0), f(28.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
        </svg>
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P17_DURATION} volume={DRONE} />
      <Sfx src="riser.mp3" at={f(0.2)} volume={0.2} />
      <Sfx src="whoosh.mp3" at={f(7.1)} volume={0.32} />
      <Sfx src="whoosh.mp3" at={f(11.3)} volume={0.32} />
      <TypeClicks at={f(11.5)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(13.0)} volume={DRAW} />
      <Sfx src="whoosh.mp3" at={f(20.6)} volume={0.32} />
      <Sfx src="sfx_paper.mp3" at={f(27.0)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(21.6)} volume={DRAW} />
      <Sfx src="sfx_draw.mp3" at={f(28.0)} volume={0.25} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
