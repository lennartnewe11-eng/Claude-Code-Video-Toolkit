import {AbsoluteFill, Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Stamp, Highlight, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 245.26;
export const C2P9_DURATION = Math.round(29.7 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const FullPhoto: React.FC<{src: string; from: number; to: number}> = ({src, from, to}) => {
  const frame = useCurrentFrame();
  const kb = interpolate(frame, [from, to], [1.04, 1.16]);
  return (
    <>
      <Img src={staticFile(`photos/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${kb})`, filter: 'grayscale(1) contrast(1.12) brightness(1.02)'}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 280px rgba(20,16,10,0.6)'}} />
    </>
  );
};

/** Density diagram: dense line of stations (rail works) vs scattered sprawl. */
const Density: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // dense stations along a line (left panel)
  const dense = [0.06, 0.16, 0.24, 0.31, 0.37, 0.44].map((d) => 200 + d * 1400 / 0.5);
  const lineP = interpolate(frame, [f(16.4), f(18)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // moving train marker on the dense line
  const tp = interpolate(frame, [f(18), f(23)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // scattered sprawl dots (right panel)
  const sprawl = [[1180, 360], [1380, 520], [1620, 410], [1760, 600], [1280, 640], [1520, 760], [1700, 300]];
  return (
    <AbsoluteFill>
      {/* LEFT: dense */}
      <TypeHeading text="Ein Zug braucht DICHTE" x={140} y={300} size={34} at={f(16.4)} highlight />
      <div style={{position: 'absolute', left: 180, top: 470, width: 720 * lineP, height: 8, background: EV.ink}} />
      {dense.map((x, i) => {
        const s = spring({frame: frame - f(16.6) - i * 3, fps, config: {damping: 12, stiffness: 200}});
        return <div key={i} style={{position: 'absolute', left: x, top: 470, width: 26, height: 26, borderRadius: '50%', background: EV.ink, border: `3px solid ${EV.paper}`, transform: `translate(-50%,-50%) scale(${s})`}} />;
      })}
      {/* moving train marker */}
      <div style={{position: 'absolute', left: 180 + tp * 720, top: 470, transform: 'translate(-50%,-50%)', color: EV.red, fontFamily: cond, fontSize: 40}}>▮▬</div>
      <div style={{position: 'absolute', left: 180, top: 520, fontFamily: mono, fontSize: 22, color: EV.ink}}>viele Menschen, ein Ziel → Bahn ✓</div>

      {/* RIGHT: sprawl */}
      <TypeHeading text="Die Vorstadt = Gegenteil" x={1180} y={210} size={30} at={f(20.4)} />
      {sprawl.map(([x, y], i) => {
        const s = spring({frame: frame - f(20.6) - i * 3, fps, config: {damping: 12, stiffness: 200}});
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: 22, height: 22, background: '#5d574c', border: `3px solid ${EV.paper}`, transform: `translate(-50%,-50%) scale(${s}) rotate(45deg)`}} />;
      })}
      <Stamp text="Bahn unmöglich" x={1470} y={560} size={38} at={f(22.2)} rot={-6} />

      {/* divider */}
      <div style={{position: 'absolute', left: 1060, top: 220, width: 3, height: 560, background: 'rgba(60,54,42,0.4)'}} />
    </AbsoluteFill>
  );
};

export const Ch2P9Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />

      {/* A · sprawl explodes (full-bleed) */}
      <Group show={[0, f(8.6)]}>
        <FullPhoto src="sprawl.jpg" from={0} to={f(8.6)} />
        <Highlight x={90} y={150} w={620} at={f(3.2)} h={30} />
        <Headline text="Die Vororte explodieren" x={90} y={130} size={66} at={f(3.3)} />
        <div style={{position: 'absolute', left: 94, bottom: 90, fontFamily: mono, fontSize: 30, color: '#fff', borderLeft: `4px solid ${EV.yellow}`, paddingLeft: 18}}>Weit verstreut — nur mit dem Auto erreichbar.</div>
      </Group>

      {/* B · parking / drive-thru (full-bleed) */}
      <Group show={[f(8.4), f(12.9)]}>
        <FullPhoto src="parking.jpg" from={f(8.4)} to={f(13)} />
        <div style={{position: 'absolute', left: 94, top: 120, fontFamily: cond, fontWeight: 700, fontSize: 64, color: '#fff', textTransform: 'uppercase'}}>Riesige Parkplätze</div>
        <Stamp text="Drive-Thru" x={1500} y={820} size={56} at={f(11.3)} rot={6} />
      </Group>

      {/* C · density diagram */}
      <Group show={[f(12.9), f(24.4)]}>
        <TypeHeading text="Akte 02 — Zersiedelung" x={110} y={70} size={26} at={f(13.1)} />
        <Crosshair x={1850} y={70} at={f(13.4)} />
        <Density />
      </Group>

      {/* D · close */}
      <Group show={[f(24.2), C2P9_DURATION]}>
        <AbsoluteFill style={{opacity: 0.14}}><FullPhoto src="sprawl.jpg" from={f(24)} to={C2P9_DURATION} /></AbsoluteFill>
        <TypeHeading text="Nicht nur finanziell abgehängt —" x={150} y={420} size={32} at={f(24.6)} />
        <Highlight x={150} y={560} w={1180} at={f(27.1)} h={36} />
        <Headline text="Sie passt nicht mehr zu Amerika" x={150} y={535} size={78} at={f(27.1)} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P9_DURATION} volume={DRONE} />
      <Sfx src="sfx_stamp.mp3" at={f(3.3)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(11.3)} volume={0.45} />
      <TypeClicks at={f(13.1)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(16.4)} volume={0.4} />
      <Sfx src="sfx_stamp.mp3" at={f(22.2)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(27.1)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
