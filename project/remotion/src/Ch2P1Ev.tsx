import {AbsoluteFill, Audio, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Typewriter, Highlight, Crosshair, RedNote, Redaction} from './style/Evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';
import {CUTOUT_SHADOW} from './style/theme';

const START = 109.24;
export const C2P1_DURATION = Math.round(6.8 * FPS);
const f = (s: number) => Math.round(s * FPS);

const DROP = f(4.3);        // car starts falling
const FALL = 13;            // frames to hit the ground
const LAND = DROP + FALL;

const TYPE = 0.2, STAMP = 0.55, DRONE = 0.06;

export const Ch2P1Ev: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // fall: accelerate down, then settle with a damped bounce
  const fallP = interpolate(frame, [DROP, LAND], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad)});
  const settle = spring({frame: frame - LAND, fps, config: {damping: 9, stiffness: 200, mass: 1.1}});
  const restY = 430;
  const tensionFade = interpolate(frame, [LAND, LAND + 10], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const carY = frame < LAND
    ? interpolate(fallP, [0, 1], [-1250, restY])
    : restY - interpolate(settle, [0, 1], [60, 0]) * Math.cos(Math.min(1, (frame - LAND) / 18) * Math.PI); // tiny overshoot
  const fallBlur = interpolate(frame, [DROP, LAND - 2], [0, 22], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) * (frame < LAND ? 1 : 0);

  // impact screen shake
  const sh = frame >= LAND ? Math.max(0, 1 - (frame - LAND) / 12) : 0;
  const shake = sh * 14 * Math.sin((frame - LAND) * 3.1);
  const dust = interpolate(frame, [LAND, LAND + 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{transform: `translate(${shake}px, ${shake * 0.5}px)`}}>
      <GraphPaper />

      <TypeHeading text="Akte 02 — Der Herausforderer" x={110} y={70} size={26} at={f(0.2)} highlight />
      <Crosshair x={1850} y={70} at={f(0.6)} />

      {/* tension build (fades out on impact) */}
      <AbsoluteFill style={{opacity: tensionFade}}>
        <Typewriter text="Auf dem absoluten Höhepunkt —" x={150} y={210} size={40} at={f(0.5)} cps={26} />
        <Headline text="taucht ein Konkurrent auf" x={150} y={290} size={66} at={f(1.8)} />
        <Highlight x={150} y={300} w={760} at={f(2.2)} h={26} />
        <RedNote text="?" x={1180} y={300} size={140} at={f(2.6)} rot={6} />
      </AbsoluteFill>

      {/* dust puffs on impact */}
      {frame >= LAND && (
        <>
          <div style={{position: 'absolute', left: 430, top: 820, width: 360, height: 360, borderRadius: '50%', background: 'rgba(90,80,60,0.35)', transform: `translate(-50%,-50%) scale(${dust * 1.6})`, opacity: (1 - dust) * 0.6, filter: 'blur(24px)'}} />
          <div style={{position: 'absolute', left: 1320, top: 820, width: 360, height: 360, borderRadius: '50%', background: 'rgba(90,80,60,0.35)', transform: `translate(-50%,-50%) scale(${dust * 1.6})`, opacity: (1 - dust) * 0.6, filter: 'blur(24px)'}} />
        </>
      )}

      {/* the car falls in at "Das Auto" */}
      {frame >= DROP - 1 && (
        <Img
          src={staticFile('cutouts/modelt.png')}
          style={{position: 'absolute', left: '50%', top: 0, width: 1320, transform: `translate(-50%, ${carY}px)`, filter: `${CUTOUT_SHADOW} blur(${fallBlur}px)`}}
        />
      )}

      {/* the reveal — big, on a yellow block in the clear upper area */}
      {frame >= LAND - 1 && (
        <>
          <div style={{position: 'absolute', left: 600, top: 200, width: 720, height: 120, background: '#ffd83a', transform: 'skewX(-6deg)', opacity: interpolate(frame, [LAND, LAND + 6], [0, 0.95], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
          <Headline text="Das Auto" x={630} y={210} size={120} at={LAND} />
        </>
      )}

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P1_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.5)} n={8} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(2.2)} volume={0.4} />
      <Sfx src="sfx_stamp.mp3" at={LAND} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={LAND + 1} volume={0.4} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
