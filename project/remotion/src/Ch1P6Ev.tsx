import {AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Typewriter, Stamp, Circle, Crosshair} from './style/Evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 103.9;
export const P6EV_DURATION = Math.round(5.0 * FPS);
const f = (s: number) => Math.round(s * FPS);

const TYPE = 0.18, STAMP = 0.45, DRAW = 0.28, DRONE = 0.06;

/**
 * Chapter 1 · Part 6 (103.9–108.7) — the calm closing frame.
 * "The railroad was so dominant nobody could imagine it ever changing."
 * Typewriter reveal, a stamped "DOMINANT", and a red circle foreshadowing
 * the turn (chapter 2: the automobile).
 */
export const Ch1P6Ev: React.FC = () => {
  const frame = useCurrentFrame();
  // faint golden-spike backdrop, very slow push
  const bgScale = interpolate(frame, [0, P6EV_DURATION], [1.06, 1.12]);
  return (
    <AbsoluteFill>
      <GraphPaper />
      <AbsoluteFill style={{opacity: 0.16}}>
        <Img src={staticFile('photos/goldenspike.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(1) contrast(1.1)', transform: `scale(${bgScale})`}} />
      </AbsoluteFill>
      <AbsoluteFill style={{boxShadow: 'inset 0 0 320px rgba(40,34,22,0.55)'}} />

      <TypeHeading text="Akte 01 — Das goldene Zeitalter" x={110} y={70} size={26} at={f(0.2)} />
      <Crosshair x={1850} y={70} at={f(0.6)} />

      {/* the closing sentence */}
      <Typewriter text="Die Eisenbahn war so" x={560} y={320} size={46} at={f(0.4)} cps={26} />
      <Stamp text="Dominant" x={770} y={485} size={120} at={f(1.6)} rot={-4} />
      <Typewriter text="dass niemand glaubte," x={560} y={650} size={44} at={f(2.4)} cps={30} />
      <Typewriter text="es könne sich jemals ändern." x={560} y={725} size={44} at={f(3.4)} cps={30} />

      {/* foreshadow: circle the doubt */}
      <Circle x={870} y={747} rx={215} ry={40} at={f(4.4)} rot={-3} />

      {/* ── sound (quiet, calm) ── */}
      <DroneBed durationInFrames={P6EV_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.4)} n={9} gap={3} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(1.6)} volume={STAMP} />
      <TypeClicks at={f(2.4)} n={9} gap={3} volume={TYPE} />
      <TypeClicks at={f(3.4)} n={11} gap={3} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(4.4)} volume={DRAW} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
