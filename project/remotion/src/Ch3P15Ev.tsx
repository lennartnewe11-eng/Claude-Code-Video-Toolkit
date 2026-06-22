import {AbsoluteFill, Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {Halftone, Stamp, RedNote} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, DroneBed} from './style/Sound';

const START = 652.803;
export const C3P15_DURATION = Math.round(31.4 * FPS);
const f = (s: number) => Math.round(s * FPS);
const DRONE = 0.06, STAMP = 0.5;
const LIGHT = '#f3efe4';
const GREEN = '#3f9d5a';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 6, show[1] - 7, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Full-screen colour photo with a dark left-gradient for text legibility. */
const Shot: React.FC<{src: string; from: number; dur: number; pos?: string}> = ({src, from, dur, pos = 'center'}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <ShotInner src={src} dur={dur} pos={pos} />
  </Sequence>
);
const ShotInner: React.FC<{src: string; dur: number; pos: string}> = ({src, dur, pos}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 6, dur - 7, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.05, 1.13]);
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <Img src={staticFile(`photos/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, transform: `scale(${scale})`, filter: 'saturate(1.05) contrast(1.04)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(100deg, rgba(10,12,16,0.82) 0%, rgba(10,12,16,0.45) 42%, rgba(10,12,16,0.08) 70%)'}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 240px rgba(0,0,0,0.6)'}} />
    </AbsoluteFill>
  );
};
const Tag: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>{text}</div>
);
const Big: React.FC<{lines: string[]; y?: number; at: number; hl?: number; color?: string; size?: number}> = ({lines, y = 280, at, hl = -1, color = LIGHT, size = 74}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame - at, [0, 7], [-22, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 80, top: y, opacity: o, transform: `translateX(${tx}px)`}}>
      {lines.map((l, i) => (
        <div key={i} style={{fontFamily: cond, fontWeight: 700, fontSize: size, lineHeight: 1.0, textTransform: 'uppercase', color: i === hl ? color : LIGHT, textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>{l}</div>
      ))}
    </div>
  );
};
const Cap: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', left: 84, bottom: 60, fontFamily: mono, fontSize: 22, color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>{text}</div>
);

/** A grid of parcels filling in — thousands of properties. */
const ParcelGrid: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const cols = 16, rows = 7, s = 34;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: cols * s, height: rows * s}}>
      {Array.from({length: cols * rows}).map((_, i) => {
        const appear = from + i * 0.7;
        const o = interpolate(frame - appear, [0, 5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return <div key={i} style={{position: 'absolute', left: (i % cols) * s, top: Math.floor(i / cols) * s, width: s - 4, height: s - 4, border: `2px solid ${EV.red}`, background: 'rgba(179,39,28,0.25)', opacity: o}} />;
      })}
    </div>
  );
};

export const Ch3P15Ev: React.FC = () => {
  const frame = useCurrentFrame();
  const isoP = interpolate(frame, [f(19.0), f(21.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* photos */}
      <Shot src="cahsr_bridge.jpg" from={0} dur={f(4.8)} />
      <Shot src="valley.jpg" from={f(4.6)} dur={f(4.0)} />
      <Shot src="gavel.jpg" from={f(8.3)} dur={f(6.5)} />
      <Shot src="valley.jpg" from={f(14.5)} dur={f(11.5)} pos="center" />
      <Shot src="trump.jpg" from={f(25.7)} dur={C3P15_DURATION - f(25.7)} pos="top" />
      <Halftone opacity={0.06} size={7} />

      {/* 173 — they're doing it right (a real new line) */}
      <Group show={[0, f(4.8)]}>
        <Tag text="CALIFORNIA HIGH-SPEED RAIL" />
        <Big lines={['Diesmal macht', 'Kalifornien vieles richtig']} at={f(0.4)} y={250} size={64} />
        <div style={{position: 'absolute', left: 84, top: 440, fontFamily: cond, fontWeight: 700, fontSize: 56, color: GREEN, textShadow: '0 2px 14px rgba(0,0,0,0.8)', opacity: interpolate(frame, [f(2.4), f(3.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>✓ eine eigene, neue Trasse</div>
        <Cap text="Neubau im Central Valley" />
      </Group>

      {/* 174 — but thousands of properties */}
      <Group show={[f(4.6), f(8.6)]}>
        <Tag text="DER PREIS DAFÜR" />
        <Big lines={['Doch dafür:', 'tausende Grundstücke']} at={f(4.9)} y={230} hl={1} color={EV.yellow} size={68} />
        <ParcelGrid x={84} y={470} from={f(5.6)} />
      </Group>

      {/* 175-176 — a legal nightmare */}
      <Group show={[f(8.3), f(14.6)]}>
        <Tag text="DIE FOLGE" />
        <Big lines={['Ein juristischer', 'Albtraum']} at={f(8.6)} y={250} hl={1} color={EV.red} size={88} />
        <div style={{position: 'absolute', left: 84, top: 520, fontFamily: mono, fontSize: 30, color: LIGHT, textShadow: '0 2px 12px rgba(0,0,0,0.85)', opacity: interpolate(frame, [f(11.4), f(12.1)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>Jeder Eigentümer kann über Jahre klagen.</div>
        <Stamp text="Stillstand" x={1450} y={760} size={56} at={f(12.8)} rot={-7} />
      </Group>

      {/* 177-178 — the home-made error: built in the empty middle */}
      <Group show={[f(14.5), f(26.0)]}>
        <Tag text="DER HAUSGEMACHTE FEHLER" />
        <Big lines={['Baustart im leeren', 'Central Valley —', 'nicht in SF oder LA']} at={f(15.0)} y={170} hl={2} color={EV.yellow} size={60} />
        {/* isolation schematic */}
        <svg style={{position: 'absolute', left: 80, top: 560}} width={1760} height={200}>
          <line x1={20} y1={90} x2={1740} y2={90} stroke={LIGHT} strokeWidth={4} />
          <circle cx={60} cy={90} r={16} fill={LIGHT} /><text x={60} y={150} fontFamily={cond} fontWeight={700} fontSize={40} fill={LIGHT} textAnchor="middle">SF</text>
          <circle cx={1700} cy={90} r={16} fill={LIGHT} /><text x={1700} y={150} fontFamily={cond} fontWeight={700} fontSize={40} fill={LIGHT} textAnchor="middle">LA</text>
          <rect x={760} y={66} width={240 * isoP} height={48} fill={EV.yellow} />
          {isoP > 0.5 && <text x={880} y={50} fontFamily={cond} fontWeight={700} fontSize={34} fill={EV.yellow} textAnchor="middle">gebaut</text>}
          <text x={400} y={50} fontFamily={mono} fontSize={24} fill={EV.red} textAnchor="middle" opacity={isoP}>leer</text>
          <text x={1300} y={50} fontFamily={mono} fontSize={24} fill={EV.red} textAnchor="middle" opacity={isoP}>leer</text>
        </svg>
        <RedNote text="ein Zug, der kaum jemanden irgendwo hinbringt" x={760} y={830} size={36} at={f(22.6)} rot={-2} />
      </Group>

      {/* 179 — Trump pulls the funding */}
      <Group show={[f(25.7), C3P15_DURATION]}>
        <Tag text="2025 — DER NÄCHSTE SCHLAG" />
        <Big lines={['Washington streicht', 'die Förderung']} at={f(26.1)} y={250} hl={1} color={EV.red} size={76} />
        <div style={{position: 'absolute', left: 84, top: 470}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 150, lineHeight: 0.9, color: EV.red, textShadow: '0 2px 16px rgba(0,0,0,0.85)', opacity: interpolate(frame, [f(28.0), f(28.7)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>− $4 Mrd.</div>
          <div style={{fontFamily: mono, fontWeight: 700, fontSize: 26, letterSpacing: '0.12em', color: LIGHT, marginTop: 6, opacity: interpolate(frame, [f(28.4), f(29.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>Bundesförderung, 2025</div>
        </div>
        <Cap text="Trump-Administration zieht Mittel zurück" />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P15_DURATION} volume={DRONE} />
      <Sfx src="whoosh.mp3" at={f(4.6)} volume={0.32} />
      <Sfx src="whoosh.mp3" at={f(8.3)} volume={0.32} />
      <Sfx src="sfx_stamp.mp3" at={f(12.8)} volume={STAMP} />
      <Sfx src="whoosh.mp3" at={f(14.5)} volume={0.32} />
      <Sfx src="whoosh.mp3" at={f(25.7)} volume={0.35} />
      <Sfx src="impact.mp3" at={f(28.0)} volume={0.5} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
