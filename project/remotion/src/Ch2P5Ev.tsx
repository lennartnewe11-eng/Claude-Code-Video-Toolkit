import {AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Typewriter, Highlight, Stamp, BigX, DashedBox, RouteLine, Crosshair} from './style/Evidence';
import {mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 141.22;
export const C2P5_DURATION = Math.round(19.7 * FPS);
const f = (s: number) => Math.round(s * FPS);
const STAMP = 0.5, TYPE = 0.2, DRONE = 0.06, DRAW = 0.3;

// phase windows (frames)
const BLEED_IN = f(7.0), BLEED_OUT = f(11.5);

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const TIMETABLE = ['06:14   Chicago', '09:40   St. Louis', '14:05   Kansas City', '19:30   Denver'];

export const Ch2P5Ev: React.FC = () => {
  const frame = useCurrentFrame();
  const kb = interpolate(frame, [BLEED_IN, BLEED_OUT], [1.06, 1.16]);

  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 02 — Die Freiheit" x={110} y={70} size={26} at={f(0.2)} />
      <Crosshair x={1850} y={70} at={f(0.8)} />

      {/* ── Board 1: what rail never could ── */}
      <Group show={[0, BLEED_IN + 4]}>
        <Typewriter text="Was die Eisenbahn niemals konnte:" x={110} y={130} size={26} at={f(0.4)} cps={30} />
        <Highlight x={150} y={330} w={760} at={f(3.6)} h={34} />
        <Headline text="Totale Freiheit" x={150} y={300} size={104} at={f(3.45)} />

        {/* crossed-out timetable */}
        <DashedBox x={1180} y={250} w={500} h={300} at={f(4.6)} />
        <TypeHeading text="Fahrplan" x={1205} y={275} size={20} at={f(4.7)} />
        {TIMETABLE.map((r, i) => (
          <TypeHeading key={i} text={r} x={1205} y={335 + i * 46} size={24} at={f(4.7 + i * 0.12)} color="#5d574c" />
        ))}
        <BigX x={1180} y={250} w={500} h={300} at={f(5.0)} />
        <Stamp text="Kein Fahrplan" x={1430} y={620} size={44} at={f(5.4)} rot={-6} />

        {/* fixed track struck out */}
        <TypeHeading text="Keine feste Strecke" x={150} y={620} size={28} at={f(5.9)} />
        <div style={{position: 'absolute', left: 150, top: 690, width: 620, height: 26, borderTop: `4px solid ${EV.ink}`, borderBottom: `4px solid ${EV.ink}`}} />
        <BigX x={350} y={665} w={240} h={78} at={f(6.2)} />
      </Group>

      {/* ── Full-bleed open road ── */}
      {frame >= BLEED_IN - 1 && frame <= BLEED_OUT + 2 && (
        <AbsoluteFill style={{opacity: interpolate(frame, [BLEED_IN, BLEED_IN + 5, BLEED_OUT - 5, BLEED_OUT], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
          <Img src={staticFile('photos/openroad.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${kb})`, filter: 'contrast(1.06) saturate(0.9) brightness(1.02)'}} />
          <AbsoluteFill style={{boxShadow: 'inset 0 0 260px rgba(20,16,10,0.6)'}} />
          <div style={{position: 'absolute', left: 90, bottom: 110, fontFamily: mono, fontSize: 40, color: '#fff', borderLeft: `4px solid ${EV.yellow}`, paddingLeft: 20}}>
            Wann du willst. Wohin du willst.
          </div>
          <div style={{position: 'absolute', left: 90, bottom: 60, fontFamily: mono, fontSize: 28, color: '#e9e4d6', opacity: interpolate(frame, [f(9.4), f(9.9)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
            Von der Haustür bis zum Ziel.
          </div>
        </AbsoluteFill>
      )}

      {/* ── Board 2: a promise ── */}
      <Group show={[BLEED_OUT - 4, C2P5_DURATION]}>
        <AbsoluteFill style={{opacity: 0.14}}>
          <Img src={staticFile('photos/openroad.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(1) contrast(1.1)', transform: 'scale(1.15)'}} />
        </AbsoluteFill>
        <Typewriter text="Diese Freiheit wird zum Kern" x={150} y={250} size={40} at={f(11.7)} cps={28} />
        <Typewriter text="der amerikanischen Identität." x={150} y={310} size={40} at={f(13.2)} cps={28} />
        <TypeHeading text="Das Auto ist nicht nur Transport —" x={150} y={640} size={30} at={f(16.1)} />
        <Highlight x={150} y={760} w={760} at={f(18.0)} h={36} />
        <Headline text="Es ist ein Versprechen" x={150} y={735} size={104} at={f(18.0)} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P5_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.4)} n={7} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(3.45)} volume={STAMP} />
      <TypeClicks at={f(4.7)} n={10} gap={4} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(5.0)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(5.4)} volume={STAMP} />
      <Sfx src="sfx_draw.mp3" at={f(6.2)} volume={DRAW} />
      <TypeClicks at={f(11.7)} n={8} gap={5} volume={TYPE} />
      <TypeClicks at={f(13.2)} n={8} gap={5} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(18.0)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
