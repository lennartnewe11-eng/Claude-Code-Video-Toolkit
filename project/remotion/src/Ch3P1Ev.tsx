import {AbsoluteFill, Audio, interpolate, Loop, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Stamp, Highlight, RedNote, Crosshair, CornerMarks} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 275.52;
export const C3P1_DURATION = Math.round(15.0 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, DRAW = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Looping archival video panel (B/W, grain, vignette). */
const VideoPanel: React.FC<{src: string; left: number; top: number; w: number; h: number; loopFrames: number}> = ({src, left, top, w, h, loopFrames}) => (
  <div style={{position: 'absolute', left, top, width: w, height: h, overflow: 'hidden', border: '8px solid #1b1812', boxShadow: '6px 10px 18px rgba(20,16,10,0.36)'}}>
    <Loop durationInFrames={loopFrames} layout="none">
      <OffthreadVideo src={staticFile(`clips/${src}`)} muted style={{width: w, height: h, objectFit: 'cover', filter: 'grayscale(1) contrast(1.16) brightness(1.0)'}} />
    </Loop>
    <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.16) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.4}} />
    <AbsoluteFill style={{boxShadow: 'inset 0 0 130px rgba(0,0,0,0.6)'}} />
  </div>
);

/** Diverging chart: freight revenue rises (ink), passenger revenue falls (red). */
const DivergingChart: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const W = 840, H = 380, ax = 70, ay = 40, bot = H - 40, right = W - 20;
  const p = interpolate(frame, [from, from + f(5.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // line endpoints
  const fr0 = [ax, 250], fr1 = [right, ay + 30];   // Güter rises
  const pa0 = [ax, 130], pa1 = [right, bot - 10];  // Personen falls
  const lerp = (a: number[], b: number[], t: number) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  const frNow = lerp(fr0, fr1, p), paNow = lerp(pa0, pa1, p);
  const clipW = ax + (right - ax) * p;
  return (
    <svg style={{position: 'absolute', left: x, top: y}} width={W} height={H}>
      <defs>
        <clipPath id="reveal"><rect x={0} y={0} width={clipW} height={H} /></clipPath>
      </defs>
      {/* axes */}
      <line x1={ax} y1={ay} x2={ax} y2={bot} stroke={EV.ink} strokeWidth={3} />
      <line x1={ax} y1={bot} x2={right} y2={bot} stroke={EV.ink} strokeWidth={3} />
      {/* gridlines */}
      {[0.25, 0.5, 0.75].map((g) => (
        <line key={g} x1={ax} y1={ay + (bot - ay) * g} x2={right} y2={ay + (bot - ay) * g} stroke="rgba(60,54,42,0.18)" strokeWidth={1} />
      ))}
      <g clipPath="url(#reveal)">
        <line x1={fr0[0]} y1={fr0[1]} x2={fr1[0]} y2={fr1[1]} stroke={EV.ink} strokeWidth={5} />
        <line x1={pa0[0]} y1={pa0[1]} x2={pa1[0]} y2={pa1[1]} stroke={EV.red} strokeWidth={5} />
      </g>
      {/* leading dots */}
      <circle cx={frNow[0]} cy={frNow[1]} r={7} fill={EV.ink} />
      <circle cx={paNow[0]} cy={paNow[1]} r={7} fill={EV.red} />
      {/* labels */}
      <text x={ax + 14} y={bot - 8} fontFamily={mono} fontSize={20} fill={EV.ink}>Güterverkehr ▲</text>
      <text x={ax + 14} y={ay + 26} fontFamily={mono} fontSize={20} fill={EV.red}>Personenverkehr ▼</text>
    </svg>
  );
};

export const Ch3P1Ev: React.FC = () => {
  const RAIL = f(14); // railpax loop length

  return (
    <AbsoluteFill>
      <GraphPaper />

      {/* title */}
      <Group show={[0, f(3.9)]}>
        <TypeHeading text="Kapitel 3" x={110} y={300} size={28} at={f(0.2)} highlight />
        <Headline text="Der verpasste Schnellzug" x={110} y={360} size={120} at={f(0.5)} />
        <TypeHeading text="Die Geschichte des Hochgeschwindigkeitszugs" x={115} y={520} size={28} at={f(1.4)} color="#5d574c" />
      </Group>

      {/* US rail dying — evidence board */}
      <Group show={[f(3.7), C3P1_DURATION]}>
        <TypeHeading text="Akte 03 — USA, Anfang 1960er" x={110} y={70} size={26} at={f(3.8)} />
        <Crosshair x={1850} y={70} at={f(4.2)} />

        {/* archival passenger-rail panel (looped period footage) */}
        <VideoPanel src="railpax.mp4" left={110} top={250} w={780} h={560} loopFrames={RAIL} />
        <CornerMarks x={98} y={238} w={804} h={584} at={f(4.4)} />
        <div style={{position: 'absolute', left: 120, top: 824, fontFamily: mono, fontSize: 20, color: EV.inkSoft, letterSpacing: '0.05em'}}>US-Personenverkehr · Mitte der 1950er (Archiv)</div>

        {/* verdict headline */}
        <Headline text="Personenverkehr" x={950} y={150} size={64} at={f(4.0)} />
        <Highlight x={950} y={268} w={620} at={f(4.8)} h={42} />
        <Headline text="= Verlustgeschäft" x={960} y={246} size={74} at={f(4.7)} />

        {/* diverging chart: freight up, passengers down */}
        <DivergingChart x={945} y={350} from={f(5.4)} />
        <TypeHeading text="Das Geld kommt aus dem Güterverkehr" x={950} y={760} size={22} at={f(9.4)} color="#5d574c" />

        {/* burden stamp */}
        <RedNote text="↓↓↓" x={1210} y={330} size={52} at={f(8.0)} rot={0} />
        <Stamp text="Fahrgäste = Last" x={560} y={720} size={44} at={f(12.4)} rot={-6} />
      </Group>

      {/* sound */}
      <DroneBed durationInFrames={C3P1_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(0.5)} volume={STAMP} />
      <Sfx src="sfx_draw.mp3" at={f(5.4)} volume={DRAW} />
      <TypeClicks at={f(9.4)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(12.4)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
