import {AbsoluteFill, Audio, Easing, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Typewriter, Stamp, Circle, Crosshair} from './style/Evidence';
import {Sfx, DroneBed} from './style/Sound';
import {CUTOUT_SHADOW} from './style/theme';

export const C2P1_DURATION = Math.round(4.0 * FPS);
const f = (s: number) => Math.round(s * FPS);

const ENTER = f(0.6);   // car starts entering
const REST = f(2.0);    // car has braked to rest

/**
 * Chapter 2 · opening shot. The Chapter-1 closing board ("...so DOMINANT...
 * nobody believed it could ever change") still holds — then a car slides in
 * from the side, brakes, and nearly covers the whole frame: the automobile
 * arrives.
 */
export const Ch2P1Ev: React.FC = () => {
  const frame = useCurrentFrame();

  const p = interpolate(frame, [ENTER, REST], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
  });
  const x = interpolate(p, [0, 1], [2500, 40]); // off-right -> ~centred
  const blur = interpolate(frame, [ENTER, REST - 6], [16, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // suspension bob on stop
  const t = frame - REST;
  const bob = t > 0 ? Math.sin(t / 3) * Math.max(0, 7 - t * 0.5) : 0;
  // the railroad world dims as the car takes over
  const dim = interpolate(frame, [REST - 14, REST + 8], [0, 0.45], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill>
      {/* ── static Chapter-1 end frame ── */}
      <GraphPaper />
      <AbsoluteFill style={{opacity: 0.16}}>
        <Img src={staticFile('photos/goldenspike.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(1) contrast(1.1)', transform: 'scale(1.12)'}} />
      </AbsoluteFill>
      <AbsoluteFill style={{boxShadow: 'inset 0 0 320px rgba(40,34,22,0.55)'}} />
      <TypeHeading text="Akte 01 — Das goldene Zeitalter" x={110} y={70} size={26} at={-30} />
      <Crosshair x={1850} y={70} at={-30} />
      <Typewriter text="Die Eisenbahn war so" x={560} y={320} size={46} at={-120} />
      <Stamp text="Dominant" x={770} y={485} size={120} at={-30} rot={-4} />
      <Typewriter text="dass niemand glaubte," x={560} y={650} size={44} at={-120} />
      <Typewriter text="es könne sich jemals ändern." x={560} y={725} size={44} at={-120} />
      <Circle x={870} y={747} rx={215} ry={40} at={-30} rot={-3} />

      {/* darken as the car barges in */}
      <AbsoluteFill style={{backgroundColor: '#0d0b08', opacity: dim}} />

      {/* ── the car ── */}
      {frame >= ENTER - 1 && (
        <Img
          src={staticFile('cutouts/car.png')}
          style={{
            position: 'absolute',
            left: '50%',
            top: '58%',
            width: 2400,
            transform: `translate(-50%, -50%) translate(${x}px, ${bob}px)`,
            filter: `${CUTOUT_SHADOW} blur(${blur}px)`,
          }}
        />
      )}

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P1_DURATION} volume={0.06} />
      <Sfx src="sfx_skid.mp3" at={ENTER} volume={0.45} dur={f(2.2)} />
      <Sfx src="sfx_stamp.mp3" at={REST} volume={0.5} />
    </AbsoluteFill>
  );
};
