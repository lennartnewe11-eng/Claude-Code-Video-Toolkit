import {AbsoluteFill, Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Stamp, Highlight, RedNote, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 314.28;
export const C3P3_DURATION = Math.round(8.4 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 6, show[1] - 8, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** A pole-position starting grid; the front slot lights up as USA. */
const Grid: React.FC<{from: number}> = ({from}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // slots: front (pole) + others
  const slots = [
    {x: 1180, y: 360, w: 280, h: 120, pole: true},
    {x: 1500, y: 300, w: 180, h: 90, label: '?'},
    {x: 1500, y: 430, w: 180, h: 90, label: '?'},
    {x: 1720, y: 360, w: 160, h: 80, label: '?'},
    {x: 1500, y: 560, w: 180, h: 90, label: '?'},
  ];
  return (
    <AbsoluteFill>
      {slots.map((s, i) => {
        const sp = spring({frame: frame - from - i * 4, fps, config: {damping: 16, stiffness: 160}});
        const lit = s.pole && frame >= f(5.2);
        return (
          <div key={i} style={{position: 'absolute', left: s.x, top: s.y, width: s.w, height: s.h, transform: `translate(-50%,-50%) scale(${sp})`, border: `3px ${s.pole ? 'solid' : 'dashed'} ${EV.ink}`, background: lit ? EV.yellow : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: lit ? '4px 6px 12px rgba(0,0,0,0.35)' : 'none'}}>
            {s.label && <span style={{fontFamily: cond, fontWeight: 700, fontSize: 44, color: EV.ink}}>{s.label}</span>}
            {s.pole && lit && <span style={{fontFamily: cond, fontWeight: 700, fontSize: 70, color: EV.ink, letterSpacing: '0.04em'}}>USA</span>}
            {s.pole && !lit && <span style={{fontFamily: mono, fontWeight: 700, fontSize: 24, letterSpacing: '0.2em', color: EV.inkSoft}}>POLE</span>}
          </div>
        );
      })}
      {/* start line */}
      <div style={{position: 'absolute', left: 1060, top: 240, width: 14, height: 420, backgroundImage: 'repeating-linear-gradient(0deg, #1b1812 0 18px, #fff 18px 36px)'}} />
    </AbsoluteFill>
  );
};

export const Ch3P3Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 03 — Das Wettrennen" x={110} y={70} size={26} at={f(0.2)} />
      <Crosshair x={1850} y={70} at={f(0.8)} />

      {/* ── Phase A: the question ── */}
      <Group show={[0, f(4.6)]}>
        <TypeHeading text="Überall dieselbe Frage" x={120} y={300} size={30} at={f(0.4)} highlight />
        <Headline text="Welches Land baut" x={120} y={400} size={92} at={f(2.3)} />
        <Headline text="den nächsten Schnellzug?" x={120} y={520} size={92} at={f(2.7)} />
        <RedNote text="?" x={1500} y={460} size={420} at={f(3.0)} rot={-6} />
      </Group>

      {/* ── Phase B: pole position → USA ── */}
      <Group show={[f(4.4), C3P3_DURATION]}>
        <TypeHeading text="In der Pole Position:" x={120} y={300} size={32} at={f(4.6)} />
        <Headline text="Die größte" x={120} y={380} size={88} at={f(4.9)} />
        <Headline text="Technologiemacht" x={120} y={470} size={88} at={f(5.1)} />
        <Headline text="der Welt" x={120} y={560} size={88} at={f(5.3)} />
        <Grid from={f(4.8)} />
        <Stamp text="Die USA" x={420} y={760} size={80} at={f(6.6)} rot={-6} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P3_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.4)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(3.0)} volume={0.45} />
      <Sfx src="sfx_stamp.mp3" at={f(5.2)} volume={0.4} />
      <Sfx src="sfx_stamp.mp3" at={f(6.6)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
