import {AbsoluteFill, Audio, Img, interpolate, Loop, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Crosshair} from './style/Evidence';
import {cond, EV} from './style/evidence';
import {CUTOUT_SHADOW} from './style/theme';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 225.96;
export const C2P8_DURATION = Math.round(19.0 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06;

const VideoBand: React.FC<{src: string; top: number; height: number; label?: boolean}> = ({src, top, height}) => (
  <div style={{position: 'absolute', left: 0, top, width: 1920, height: Math.max(0, height), overflow: 'hidden'}}>
    <Loop durationInFrames={f(13)} layout="none">
      <OffthreadVideo src={staticFile(`clips/${src}`)} muted style={{width: 1920, height: 1080, objectFit: 'cover'}} />
    </Loop>
    <AbsoluteFill style={{boxShadow: 'inset 0 0 160px rgba(0,0,0,0.7)'}} />
  </div>
);

export const Ch2P8Ev: React.FC = () => {
  const frame = useCurrentFrame();

  // bands grow in, then squeeze toward the centre
  const airH = interpolate(frame, [f(0.3), f(3), f(16.4), f(18.6)], [0, 400, 400, 500], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const hwH = interpolate(frame, [f(12.2), f(15), f(16.4), f(18.6)], [0, 400, 400, 500], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const gapTop = airH;
  const gapBot = 1080 - hwH;
  const trainY = (gapTop + gapBot) / 2;
  const gapH = Math.max(40, gapBot - gapTop);
  const trainScaleY = interpolate(gapH, [120, 300], [0.45, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const arrowO = interpolate(frame, [f(16.2), f(17)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: EV.paper}}>
      <GraphPaper />

      {/* air (top) */}
      <VideoBand src="air.mp4" top={0} height={airH} />
      {/* highway (bottom) */}
      <VideoBand src="highway.mp4" top={gapBot} height={hwH} />

      {/* the squeezed railroad in the middle */}
      <Img src={staticFile('cutouts/train.png')} style={{position: 'absolute', left: '50%', top: trainY, width: 1000, transform: `translate(-50%,-50%) scaleY(${trainScaleY})`, filter: CUTOUT_SHADOW}} />
      <div style={{position: 'absolute', left: '50%', top: trainY + 70 * trainScaleY, transform: 'translate(-50%,-50%)', fontFamily: cond, fontWeight: 700, fontSize: 30, color: EV.ink, opacity: interpolate(frame, [f(0.3), f(2)], [0, 1], {extrapolateRight: 'clamp'})}}>DIE BAHN</div>

      {/* pincer arrows */}
      <div style={{position: 'absolute', left: 0, top: gapTop + 6, width: 1920, textAlign: 'center', color: EV.red, fontFamily: cond, fontSize: 50, opacity: arrowO, letterSpacing: 40}}>▼▼▼</div>
      <div style={{position: 'absolute', left: 0, top: gapBot - 56, width: 1920, textAlign: 'center', color: EV.red, fontFamily: cond, fontSize: 50, opacity: arrowO, letterSpacing: 40}}>▲▲▲</div>

      {/* labels */}
      <TypeHeading text="Akte 02 — In die Zange" x={110} y={40} size={24} at={f(0.2)} />
      <TypeHeading text="Der Staat fördert die Luftfahrt" x={110} y={120} size={30} at={f(2.4)} highlight />
      <TypeHeading text="Flughäfen · Flugsicherung · Förderung" x={115} y={170} size={20} at={f(3.0)} color="#d8d2c2" />

      <TypeHeading text="Gratis-Autobahn" x={110} y={1000} size={30} at={f(12.4)} highlight />
      <Crosshair x={1850} y={1000} at={f(13)} />

      {/* the verdict — centred on a yellow block, over the squeeze */}
      {frame >= f(16.4) && (
        <div style={{position: 'absolute', left: '50%', top: 540, transform: `translate(-50%,-50%) scale(${interpolate(frame, [f(16.5), f(16.9)], [0.8, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})})`, background: EV.yellow, padding: '8px 28px', boxShadow: '3px 4px 10px rgba(0,0,0,0.4)'}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 66, color: EV.ink, whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '0.01em'}}>In die Zange genommen</div>
        </div>
      )}

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P8_DURATION} volume={DRONE} />
      <TypeClicks at={f(2.4)} n={7} gap={4} volume={TYPE} />
      <TypeClicks at={f(12.4)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(16.6)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(17.0)} volume={0.4} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};

