import {AbsoluteFill, Audio, interpolate, Loop, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, Dossier, QuoteBox, FileTag, Seal, Stamp, Highlight, RedNote, CornerMarks, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 324.30;
export const C3P4_DURATION = Math.round(32.8 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3, DRAW = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Looping archival video panel (B/W, grain, vignette), optionally taped/tilted. */
const VideoPanel: React.FC<{src: string; left: number; top: number; w: number; h: number; loopFrames: number; startFrom?: number; rot?: number; tape?: boolean}> = ({
  src, left, top, w, h, loopFrames, startFrom = 0, rot = 0, tape,
}) => (
  <div style={{position: 'absolute', left, top, width: w, height: h, transform: `rotate(${rot}deg)`, boxShadow: '6px 10px 18px rgba(20,16,10,0.36)', border: '8px solid #1b1812'}}>
    {tape && <div style={{position: 'absolute', top: -18, left: '50%', transform: 'translateX(-50%) rotate(-4deg)', width: 110, height: 28, background: EV.tape, zIndex: 3}} />}
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
      <Loop durationInFrames={loopFrames} layout="none">
        <OffthreadVideo src={staticFile(`clips/${src}`)} muted startFrom={startFrom} style={{width: w, height: h, objectFit: 'cover', filter: 'grayscale(1) contrast(1.16)'}} />
      </Loop>
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.16) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.4}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 100px rgba(0,0,0,0.6)'}} />
    </div>
  </div>
);

/** Blueprint reconstruction: a railcar with two jet engines bolted to the roof. */
const JetSchematic: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [from, from + f(2.6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const thrust = interpolate(frame, [from + f(2.4), from + f(3.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const drop = (1 - p) * -120; // engines descend onto the roof
  const Engine: React.FC<{ex: number}> = ({ex}) => (
    <g transform={`translate(${ex},${70 + drop})`} opacity={p}>
      <rect x={0} y={0} width={150} height={46} rx={23} fill="#cfc8b6" stroke={EV.ink} strokeWidth={3} />
      <ellipse cx={4} cy={23} rx={9} ry={22} fill="#2a261d" stroke={EV.ink} strokeWidth={2} />
      <rect x={150} y={10} width={24} height={26} rx={4} fill="#2a261d" />
      {/* mount struts */}
      <line x1={28} y1={46} x2={28} y2={70} stroke={EV.ink} strokeWidth={3} />
      <line x1={120} y1={46} x2={120} y2={70} stroke={EV.ink} strokeWidth={3} />
      {/* thrust */}
      <g opacity={thrust}>
        {[0, 1, 2].map((i) => (
          <line key={i} x1={176 + i * 14} y1={23} x2={196 + i * 14} y2={23} stroke={EV.red} strokeWidth={4 - i} />
        ))}
      </g>
    </g>
  );
  return (
    <svg style={{position: 'absolute', left: x, top: y}} width={900} height={320}>
      {/* track */}
      <line x1={20} y1={250} x2={880} y2={250} stroke={EV.ink} strokeWidth={3} />
      <line x1={20} y1={258} x2={880} y2={258} stroke={EV.inkSoft} strokeWidth={2} strokeDasharray="14 10" />
      {/* car body */}
      <rect x={70} y={140} width={760} height={96} rx={16} fill="rgba(207,200,182,0.5)" stroke={EV.ink} strokeWidth={3} />
      {/* cab nose (right) */}
      <path d="M830 140 q40 8 40 48 q0 40 -40 48 Z" fill="rgba(207,200,182,0.5)" stroke={EV.ink} strokeWidth={3} />
      {/* windows */}
      {Array.from({length: 9}).map((_, i) => (
        <rect key={i} x={96 + i * 78} y={158} width={52} height={30} rx={3} fill="#2a261d" opacity={0.85} />
      ))}
      {/* wheels */}
      {[170, 250, 640, 720].map((wx) => (
        <circle key={wx} cx={wx} cy={250} r={18} fill="none" stroke={EV.ink} strokeWidth={3} />
      ))}
      {/* the two jet engines */}
      <Engine ex={150} />
      <Engine ex={470} />
      {/* annotations */}
      <text x={150} y={36} fontFamily={mono} fontWeight={700} fontSize={20} fill={EV.ink} opacity={p}>2× GE J47 DÜSENTRIEBWERK</text>
      <line x1={300} y1={44} x2={300} y2={66} stroke={EV.red} strokeWidth={3} opacity={p} />
      <text x={360} y={206} fontFamily={mono} fontSize={18} fill={EV.inkSoft}>ganz normaler Personenwagon</text>
    </svg>
  );
};

/** Semicircular speed gauge counting up to a target. */
const Speedo: React.FC<{x: number; y: number; from: number; to: number; target: number}> = ({x, y, from, to, target}) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [from, to], [0, target], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const R = 150, cx = 170, cy = 170, MAX = 300;
  const fr = Math.min(1, v / MAX);
  const a = Math.PI * (1 - fr); // radians, 180°→0°
  const px = cx + R * Math.cos(a), py = cy - R * Math.sin(a);
  const nx = cx + (R - 26) * Math.cos(a), ny = cy - (R - 26) * Math.sin(a);
  const big = fr > 0.9; // past 270
  return (
    <div style={{position: 'absolute', left: x, top: y}}>
      <svg width={340} height={210}>
        <path d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`} fill="none" stroke="rgba(60,54,42,0.3)" strokeWidth={14} />
        <path d={`M ${cx - R} ${cy} A ${R} ${R} 0 ${fr > 0.5 ? 1 : 0} 1 ${px} ${py}`} fill="none" stroke={big ? EV.red : EV.ink} strokeWidth={14} />
        {/* ticks */}
        {Array.from({length: 7}).map((_, i) => {
          const ta = Math.PI * (1 - i / 6);
          return <line key={i} x1={cx + (R + 4) * Math.cos(ta)} y1={cy - (R + 4) * Math.sin(ta)} x2={cx + (R + 16) * Math.cos(ta)} y2={cy - (R + 16) * Math.sin(ta)} stroke={EV.ink} strokeWidth={2} />;
        })}
        {/* needle */}
        <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={EV.red} strokeWidth={5} />
        <circle cx={cx} cy={cy} r={10} fill={EV.ink} />
      </svg>
      <div style={{position: 'absolute', left: cx, top: cy - 6, transform: 'translateX(-50%)', textAlign: 'center'}}>
        <div style={{fontFamily: cond, fontWeight: 700, fontSize: 96, lineHeight: 0.9, color: big ? EV.red : EV.ink}}>{Math.round(v)}</div>
        <div style={{fontFamily: mono, fontWeight: 700, fontSize: 24, letterSpacing: '0.2em', color: EV.ink}}>KM/H</div>
      </div>
    </div>
  );
};

export const Ch3P4Ev: React.FC = () => {
  const frame = useCurrentFrame();
  const RAIL = f(14);

  return (
    <AbsoluteFill>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />

      {/* persistent header */}
      <FileTag text="3·b" x={150} y={92} at={f(0.4)} size={62} />
      <TypeHeading text="Akte — Der Düsen-Stunt" x={210} y={78} size={26} at={f(0.2)} />
      <Crosshair x={1500} y={70} at={f(0.8)} />
      <Seal text={'NEW YORK\nCENTRAL\nOHIO 1966'} x={1810} y={120} at={f(1.0)} size={150} rot={-10} />

      {/* ── Board 1: the equation — normal car + jets = the M-497 ── */}
      <Group show={[0, f(12.6)]}>
        <Headline text="Amerika spielte mit Tempo" x={120} y={200} size={66} at={f(0.6)} />
        <TypeHeading text="New York Central · Ohio · Ende der 1950er" x={125} y={296} size={24} at={f(5.4)} color="#5d574c" />
        <Highlight x={120} y={410} w={620} at={f(5.6)} h={44} />
        <Headline text="Ein absurder Versuch" x={120} y={388} size={74} at={f(5.5)} />

        {/* RDC + J47 = M-497 */}
        <TapedPhoto src="rdc.jpg" cx={300} cy={730} w={420} rot={-3} at={f(6.4)} caption="normaler Personenwagon (RDC)" />
        <div style={{position: 'absolute', left: 540, top: 690, fontFamily: cond, fontWeight: 700, fontSize: 80, color: EV.ink, opacity: interpolate(frame, [f(7.4), f(8.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>+</div>
        <TapedPhoto src="j47.jpg" cx={800} cy={730} w={420} rot={3} at={f(8.0)} caption="2× Düsentriebwerk (J47)" />
        <RedNote text="×2" x={1010} y={600} size={56} at={f(9.0)} rot={-8} />
        <div style={{position: 'absolute', left: 1050, top: 690, fontFamily: cond, fontWeight: 700, fontSize: 80, color: EV.ink, opacity: interpolate(frame, [f(9.8), f(10.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>=</div>
        <TapedPhoto src="m497.jpg" cx={1510} cy={700} w={760} rot={-1} at={f(10.6)} caption="M-497 »Black Beetle« — New York Central, 1966" />
        <CornerMarks x={1130} y={500} w={760} h={420} at={f(11.0)} />
        <TypeHeading text="= das Ergebnis" x={1150} y={470} size={26} at={f(11.0)} highlight />
      </Group>

      {/* ── Board 2: the reconstruction (blueprint) ── */}
      <Group show={[f(12.1), f(23.2)]}>
        <Headline text="Zwei Triebwerke aufs Dach" x={120} y={200} size={72} at={f(12.4)} />
        <TypeHeading text="…geschraubt — und über eine schnurgerade Strecke gejagt" x={125} y={300} size={24} at={f(13.8)} color="#5d574c" />

        <div style={{position: 'absolute', left: 470, top: 360, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.18em', color: EV.inkSoft}}>REKONSTRUKTION</div>
        <JetSchematic x={470} y={400} from={f(13.4)} />

        {/* small looping period-rail panel = the test track motion */}
        <VideoPanel src="railpax.mp4" left={110} top={430} w={330} h={240} loopFrames={RAIL} startFrom={Math.round(4.5 * FPS)} rot={-2} tape />
        <div style={{position: 'absolute', left: 120, top: 682, fontFamily: mono, fontSize: 18, color: EV.inkSoft}}>schnurgerade Teststrecke (Symbolbild)</div>

        <Dossier x={1320} y={430} w={520} at={f(15.0)} title="Versuchsaufbau"
          rows={[
            {label: 'Träger', value: 'Budd RDC'},
            {label: 'Antrieb', value: '2× GE J47', hl: true},
            {label: 'Strecke', value: 'flach & gerade'},
            {label: 'Ziel', value: 'reines Tempo', hl: true},
          ]} />
      </Group>

      {/* ── Board 3: the record ── */}
      <Group show={[f(22.7), C3P4_DURATION]}>
        <Headline text="Über 270 km/h" x={120} y={210} size={92} at={f(23.4)} />
        <Highlight x={120} y={350} w={900} at={f(25.0)} h={40} />
        <TypeHeading text="Schneller als alles auf US-Schienen" x={125} y={332} size={30} at={f(24.8)} />

        <Speedo x={150} y={470} from={f(24.0)} to={f(30.0)} target={272} />

        <TapedPhoto src="m497run.jpg" cx={1360} cy={560} w={620} rot={2} at={f(23.6)} caption="M-497 auf Rekordfahrt, Ohio" />
        <CornerMarks x={1010} y={250} w={700} h={620} at={f(24.2)} />
        <Stamp text="Rekord auf dem Papier" x={1360} y={870} size={42} at={f(28.6)} rot={-5} />
        <QuoteBox text="Schneller als alles, was sonst auf US-Schienen fuhr." x={150} y={800} w={560} at={f(29.4)} rot={-2} size={22} cite="New York Central, Ohio" />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P4_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(1.0)} volume={0.4} />
      <Sfx src="sfx_paper.mp3" at={f(6.4)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(8.0)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(10.6)} volume={0.45} />
      <Sfx src="sfx_draw.mp3" at={f(13.4)} volume={DRAW} />
      <TypeClicks at={f(15.0)} n={8} gap={5} volume={TYPE} />
      <Sfx src="sfx_skid.mp3" at={f(24.0)} volume={0.3} />
      <Sfx src="sfx_stamp.mp3" at={f(28.6)} volume={STAMP} />
      <Sfx src="sfx_paper.mp3" at={f(29.4)} volume={PAPER} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
