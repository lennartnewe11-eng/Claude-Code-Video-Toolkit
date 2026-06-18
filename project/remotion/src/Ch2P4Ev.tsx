import {AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, TapedPhoto, Highlight, RouteLine, RedNote, DashedBox, Crosshair} from './style/Evidence';
import {CUTOUT_SHADOW} from './style/theme';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 136.54;
export const C2P4_DURATION = Math.round(4.7 * FPS);
const f = (s: number) => Math.round(s * FPS);
const PAPER = 0.3, STAMP = 0.5, TYPE = 0.2, DRONE = 0.06;

/** A small Model T that pops into the "fleet" row. */
const MiniCar: React.FC<{x: number; y: number; w: number; at: number}> = ({x, y, w, at}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Img src={staticFile('cutouts/modelt.png')} style={{position: 'absolute', left: x, top: y, width: w, transform: `translate(-50%,-50%) translateY(${(1 - p) * 30}px) scale(${0.7 + p * 0.3})`, opacity: p, filter: CUTOUT_SHADOW}} />
  );
};

export const Ch2P4Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 02 — Der Herausforderer" x={110} y={70} size={26} at={f(0.2)} />
      <TypeHeading text="Vom Luxus zur Masse" x={110} y={124} size={22} at={f(0.5)} highlight />
      <Crosshair x={1850} y={70} at={f(0.8)} />

      {/* Oberschicht — the few */}
      <Img src={staticFile('cutouts/tophat.png')} style={{position: 'absolute', left: 320, top: 380, width: 180, transform: 'translate(-50%,-50%)', filter: CUTOUT_SHADOW}} />
      <DashedBox x={210} y={300} w={230} h={210} at={f(0.7)} />
      <TypeHeading text="nur die Oberschicht" x={210} y={540} size={22} at={f(0.9)} />
      <RedNote text="nicht nur" x={330} y={250} size={34} at={f(1.0)} rot={-6} />

      {/* arrow to the many */}
      <RouteLine points={[[470, 410], [760, 430], [980, 430]]} at={f(2.0)} drawFrames={20} />

      {/* Mittelschicht — the many */}
      <TapedPhoto src="family.jpg" cx={1330} cy={420} w={560} rot={2} at={f(1.4)} caption="Familie mit Auto, ca. 1921" />
      <Highlight x={1090} y={250} w={520} at={f(2.4)} h={26} />
      <TypeHeading text="die breite Mittelschicht" x={1095} y={250} size={26} at={f(2.5)} />

      {/* a fleet rolls out */}
      {[0, 1, 2, 3, 4].map((i) => (
        <MiniCar key={i} x={260 + i * 350} y={840} w={300} at={f(3.0 + i * 0.18)} />
      ))}
      <Headline text="Ein Auto für alle" x={150} y={650} size={84} at={f(3.0)} />

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P4_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(1.4)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(2.5)} volume={STAMP} />
      {[0, 1, 2, 3, 4].map((i) => <Sfx key={i} src="sfx_paper.mp3" at={f(3.0 + i * 0.18)} volume={0.18} dur={12} />)}

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
