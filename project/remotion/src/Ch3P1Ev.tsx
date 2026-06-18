import {AbsoluteFill, Audio, interpolate, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Typewriter, Stamp, Highlight, RedNote, Crosshair} from './style/Evidence';
import {EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 275.52;
export const C3P1_DURATION = Math.round(15.0 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

export const Ch3P1Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />

      {/* title */}
      <Group show={[0, f(3.9)]}>
        <TypeHeading text="Kapitel 3" x={110} y={300} size={28} at={f(0.2)} highlight />
        <Headline text="Der verpasste Schnellzug" x={110} y={360} size={120} at={f(0.5)} />
        <TypeHeading text="Die Geschichte des Hochgeschwindigkeitszugs" x={115} y={520} size={28} at={f(1.4)} color="#5d574c" />
      </Group>

      {/* US rail dying */}
      <Group show={[f(3.7), C3P1_DURATION]}>
        <TypeHeading text="Akte 03 — USA, Anfang 1960er" x={110} y={70} size={26} at={f(3.8)} />
        <Crosshair x={1850} y={70} at={f(4.2)} />

        {/* freight video panel */}
        <div style={{position: 'absolute', left: 1010, top: 250, width: 840, height: 520, overflow: 'hidden', border: `8px solid #1b1812`, boxShadow: '6px 10px 16px rgba(20,16,10,0.34)'}}>
          <OffthreadVideo src={staticFile('clips/freight.mp4')} muted style={{width: 840, height: 520, objectFit: 'cover'}} />
        </div>
        <TypeHeading text="Güterverkehr: das Geschäft" x={1020} y={800} size={22} at={f(10.0)} />

        <Headline text="Personenverkehr" x={120} y={300} size={64} at={f(4.0)} />
        <Highlight x={120} y={420} w={560} at={f(4.6)} h={40} />
        <Headline text="= Verlustgeschäft" x={130} y={400} size={70} at={f(4.5)} />
        <RedNote text="↓↓↓" x={300} y={540} size={70} at={f(5.6)} rot={0} />
        <Stamp text="Fahrgäste = Last" x={460} y={760} size={44} at={f(12.6)} rot={-6} />
      </Group>

      {/* sound */}
      <DroneBed durationInFrames={C3P1_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(0.5)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(4.5)} volume={0.4} />
      <Sfx src="sfx_stamp.mp3" at={f(12.6)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
