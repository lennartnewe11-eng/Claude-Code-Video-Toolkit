import {AbsoluteFill, Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, Highlight, RedNote, BigX, Stamp, FileTag, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, DroneBed} from './style/Sound';

const START = 581.505;
export const C3P13_DURATION = Math.round(38.6 * FPS);
const f = (s: number) => Math.round(s * FPS);
const DRONE = 0.06, STAMP = 0.5;
const LIGHT = '#f3efe4';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 5, show[1] - 6, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Fast full-screen photo: quick fade, Ken-Burns, B/W grain + vignette. */
const Shot: React.FC<{src: string; folder?: string; from: number; dur: number}> = ({src, folder = 'photos', from, dur}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <ShotInner src={src} folder={folder} dur={dur} />
  </Sequence>
);
const ShotInner: React.FC<{src: string; folder: string; dur: number}> = ({src, folder, dur}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 5, dur - 6, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.08, 1.18]);
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <Img src={staticFile(`${folder}/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: 'grayscale(1) contrast(1.15) brightness(0.98)'}} />
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.35}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 300px rgba(0,0,0,0.9)'}} />
    </AbsoluteFill>
  );
};
const Punch: React.FC<{lines: string[]; at: number; yellow?: number}> = ({lines, at, yellow = -1}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame - at, [0, 6], [-20, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 72, top: 320, opacity: o, transform: `translateX(${tx}px)`}}>
      {lines.map((l, i) => (
        <div key={i} style={{fontFamily: cond, fontWeight: 700, fontSize: 76, lineHeight: 1.0, textTransform: 'uppercase', color: i === yellow ? EV.yellow : LIGHT, textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>{l}</div>
      ))}
    </div>
  );
};
const Tag: React.FC = () => (
  <div style={{position: 'absolute', left: 72, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 03 — DIE LEKTION</div>
);
const Clock: React.FC<{x: number; y: number; r: number; at: number}> = ({x, y, r, at}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const mh = (frame - at) * 11, hh = (frame - at) * 1.1;
  return (
    <svg style={{position: 'absolute', left: x - r - 14, top: y - r - 14, opacity: o}} width={(r + 14) * 2} height={(r + 14) * 2}>
      <g transform={`translate(${r + 14} ${r + 14})`}>
        <circle r={r} fill="#fbf8ef" stroke={EV.ink} strokeWidth={5} />
        {Array.from({length: 12}).map((_, i) => <line key={i} x1={0} y1={-r + 6} x2={0} y2={-r + 15} stroke={EV.ink} strokeWidth={3} transform={`rotate(${i * 30})`} />)}
        <line x1={0} y1={0} x2={0} y2={-r * 0.55} stroke={EV.ink} strokeWidth={6} transform={`rotate(${hh})`} />
        <line x1={0} y1={0} x2={0} y2={-r * 0.8} stroke={EV.red} strokeWidth={4} transform={`rotate(${mh})`} />
        <circle r={6} fill={EV.ink} />
      </g>
    </svg>
  );
};

export const Ch3P13Ev: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />

      {/* full-screen photo cuts */}
      <Shot src="oldtracks.jpg" from={f(1.4)} dur={f(3.9)} />
      <Shot src="usrail70s.jpg" from={f(5.1)} dur={f(2.8)} />
      <Shot src="spfreight.jpg" from={f(7.6)} dur={f(5.4)} />
      <Shot src="metroliner.jpg" from={f(27.1)} dur={f(4.7)} />
      <Shot src="shinkansen0.jpg" from={f(31.5)} dur={f(4.5)} />
      <Shot src="squandered.jpg" folder="footage" from={f(35.7)} dur={C3P13_DURATION - f(35.7)} />

      {/* 157 — title */}
      <Group show={[0, f(1.5)]}>
        <Headline text="Die Lektion" x={120} y={420} size={140} at={f(0.1)} />
      </Group>

      {/* 158 — the structural hook (oldtracks) */}
      <Group show={[f(1.4), f(5.3)]}>
        <Tag />
        <Punch lines={['Der strukturelle Haken —', 'er erklärt bis heute alles']} at={f(1.7)} yellow={1} />
      </Group>

      {/* 159 — Amtrak owns almost no track */}
      <Group show={[f(5.1), f(7.9)]}>
        <Tag />
        <Punch lines={['Amtrak besitzt', 'kaum eigene Gleise']} at={f(5.4)} yellow={1} />
      </Group>

      {/* 160 — runs on freight railroads' tracks */}
      <Group show={[f(7.6), f(13.0)]}>
        <Tag />
        <Punch lines={['Es fährt auf den Schienen', 'der privaten Güterbahn']} at={f(7.9)} yellow={1} />
        <div style={{position: 'absolute', left: 72, bottom: 60, fontFamily: mono, fontSize: 22, color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>außerhalb des Nord-Ost-Korridors</div>
      </Group>

      {/* 161 — freight has priority (collage) */}
      <Group show={[f(12.8), f(17.6)]}>
        <Headline text="Güterzug = Vorrang" x={120} y={210} size={78} at={f(13.0)} />
        <Highlight x={120} y={330} w={620} at={f(13.4)} h={46} />
        {/* two lanes */}
        <div style={{position: 'absolute', left: 120, top: 470, width: 1680, height: 8, background: EV.ink}} />
        <div style={{position: 'absolute', left: interpolate(frame, [f(13.2), f(16.8)], [120, 1500], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}), top: 432, fontFamily: cond, fontWeight: 700, fontSize: 44, color: EV.ink}}>▮▬▬▬ ▶</div>
        <div style={{position: 'absolute', left: 120, top: 600, width: 1680, height: 8, background: '#b9b099'}} />
        <div style={{position: 'absolute', left: 420, top: 562, fontFamily: cond, fontWeight: 700, fontSize: 44, color: EV.red}}>▮▬ ✕</div>
        <RedNote text="Personenzug muss warten" x={760} y={720} size={48} at={f(15.0)} rot={-3} />
      </Group>

      {/* 162 — delay is built in (collage) */}
      <Group show={[f(17.5), f(21.1)]}>
        <Headline text="Verspätung —" x={120} y={300} size={92} at={f(17.7)} />
        <Highlight x={120} y={440} w={760} at={f(18.4)} h={50} />
        <Headline text="fest ins System eingebaut" x={120} y={420} size={70} at={f(18.3)} />
        <Clock x={1500} y={460} r={150} at={f(17.8)} />
      </Group>

      {/* 163 — can't put fast trains on old tracks (collage) */}
      <Group show={[f(21.0), f(27.3)]}>
        <Headline text="Schnelle Züge" x={120} y={250} size={88} at={f(21.2)} />
        <Headline text="auf alten Gleisen?" x={120} y={345} size={88} at={f(21.5)} />
        <BigX x={150} y={470} w={420} h={260} at={f(23.2)} />
        <TypeHeading text="Es geht schlicht nicht" x={650} y={560} size={34} at={f(24.2)} highlight />
      </Group>

      {/* 164 — the Metroliner lesson repeats (metroliner photo) */}
      <Group show={[f(27.1), f(31.8)]}>
        <Tag />
        <Punch lines={['Die Lektion des Metroliners —', 'sie wiederholt sich']} at={f(27.4)} yellow={1} />
      </Group>

      {/* 165 — you need your own new straight line (shinkansen) */}
      <Group show={[f(31.5), f(36.0)]}>
        <Tag />
        <Punch lines={['Wer Tempo will, braucht', 'eine eigene, gerade Strecke']} at={f(31.8)} yellow={1} />
        <div style={{position: 'absolute', left: 72, bottom: 60, fontFamily: mono, fontSize: 22, color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>Vorbild: der Shinkansen</div>
      </Group>

      {/* 166 — and here America keeps failing (squandered) */}
      <Group show={[f(35.7), C3P13_DURATION]}>
        <Tag />
        <Punch lines={['Genau hier scheitert', 'Amerika bis heute']} at={f(36.0)} yellow={1} />
        <Stamp text="bis heute ungelöst" x={520} y={760} size={48} at={f(37.4)} rot={-6} />
      </Group>

      {/* ── sound: faster cuts ── */}
      <DroneBed durationInFrames={C3P13_DURATION} volume={DRONE} />
      <Sfx src="impact.mp3" at={f(0.1)} volume={0.45} />
      {[1.4, 5.1, 7.6, 12.8, 17.5, 21.0, 27.1, 31.5, 35.7].map((t, i) => (
        <Sfx key={i} src="whoosh.mp3" at={f(t)} volume={0.32} />
      ))}
      <Sfx src="sfx_stamp.mp3" at={f(37.4)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
