import {AbsoluteFill, Audio, interpolate, Loop, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {TypeHeading, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, DroneBed} from './style/Sound';

const START = 425.960;
export const C3P8_DURATION = Math.round(23.15 * FPS);
const f = (s: number) => Math.round(s * FPS);
const STAMP = 0.5, DRONE = 0.06;
const LIGHT = '#f3efe4';

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 7, show[1] - 8, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Full-bleed archival video with B/W grain, scanlines, vignette and in/out fade. */
const FB: React.FC<{src: string; from: number; dur: number; loopFrames: number}> = ({src, from, dur, loopFrames}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <FBInner src={src} dur={dur} loopFrames={loopFrames} />
  </Sequence>
);
const FBInner: React.FC<{src: string; dur: number; loopFrames: number}> = ({src, dur, loopFrames}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 8, dur - 8, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.06, 1.14]);
  const flick = 0.94 + 0.06 * Math.abs(Math.sin(frame * 1.6));
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <Loop durationInFrames={loopFrames} layout="none">
        <OffthreadVideo src={staticFile(`clips/${src}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: `grayscale(1) contrast(1.16) brightness(${flick})`}} />
      </Loop>
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.16) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.4}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 300px rgba(0,0,0,0.9)'}} />
    </AbsoluteFill>
  );
};

const Cap: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', left: 70, bottom: 60, fontFamily: mono, fontSize: 24, letterSpacing: '0.06em', color: LIGHT, borderLeft: `4px solid ${EV.red}`, paddingLeft: 16}}>{text}</div>
);
const Big: React.FC<{text: string; x: number; y: number; size: number; at: number; color?: string}> = ({text, x, y, size, at, color = LIGHT}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame - at, [0, 7], [-26, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `translateX(${tx}px)`, fontFamily: cond, fontWeight: 700, fontSize: size, lineHeight: 0.95, letterSpacing: '0.01em', textTransform: 'uppercase', color, textShadow: '0 2px 18px rgba(0,0,0,0.85)'}}>{text}</div>;
};

export const Ch3P8Ev: React.FC = () => {
  const frame = useCurrentFrame();

  // big speed slam (240)
  const slam = interpolate(frame, [f(9.0), f(9.5)], [1.6, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const slamO = interpolate(frame, [f(9.0), f(9.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* ── full-bleed footage, phase by phase ── */}
      <FB src="acela1.mp4" from={0} dur={f(6.4)} loopFrames={f(5.7)} />
      <FB src="acela2.mp4" from={f(6.2)} dur={f(2.6)} loopFrames={f(7.9)} />
      <FB src="acela3.mp4" from={f(8.6)} dur={f(5.0)} loopFrames={f(3.4)} />
      <FB src="shinkansen_new.mp4" from={f(13.4)} dur={f(3.6)} loopFrames={f(7)} />
      <FB src="freight_us.mp4" from={f(16.8)} dur={C3P8_DURATION - f(16.8)} loopFrames={f(8.9)} />

      {/* persistent dossier marks */}
      <div style={{position: 'absolute', left: 70, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85}}>AKTE 03 — DER METROLINER</div>
      <Crosshair x={1840} y={70} at={f(0.4)} />

      {/* A · naming (120–121) */}
      <Group show={[0, f(6.3)]}>
        <TypeHeading text="Ein Name, der nach Zukunft klingt" x={72} y={150} size={28} at={f(0.6)} color={LIGHT} />
        <Cap text="Nord-Ost-Korridor · Hochgeschwindigkeit" />
        <div style={{position: 'absolute', left: 72, top: 360, opacity: interpolate(frame, [f(4.0), f(4.7)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
          <div style={{position: 'absolute', left: -4, top: 92, height: 44, width: 612, background: EV.yellow, transform: 'skewX(-7deg)'}} />
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 150, lineHeight: 0.9, color: LIGHT, textTransform: 'uppercase', textShadow: '0 3px 22px rgba(0,0,0,0.9)'}}>Metroliner</div>
        </div>
      </Group>

      {/* B · the drama (122) */}
      <Group show={[f(6.1), f(8.7)]}>
        <Big text="Hier beginnt" x={72} y={300} size={92} at={f(6.4)} />
        <Big text="das Drama" x={72} y={400} size={92} at={f(6.7)} color={EV.yellow} />
      </Group>

      {/* C · the demand: ≥240 km/h (123) */}
      <Group show={[f(8.5), f(13.6)]}>
        <TypeHeading text="Die Regierung verlangt" x={72} y={170} size={28} at={f(8.7)} color={LIGHT} />
        <Cap text="mindestens — keine Kompromisse" />
        <div style={{position: 'absolute', left: '50%', top: 470, transform: `translate(-50%,-50%) scale(${slam})`, opacity: slamO, textAlign: 'center'}}>
          <div style={{background: EV.yellow, padding: '6px 30px', boxShadow: '4px 6px 16px rgba(0,0,0,0.6)'}}>
            <span style={{fontFamily: cond, fontWeight: 700, fontSize: 200, lineHeight: 0.9, color: EV.ink}}>≥240</span>
          </div>
          <div style={{fontFamily: mono, fontWeight: 700, fontSize: 40, letterSpacing: '0.3em', color: LIGHT, marginTop: 14, textShadow: '0 2px 14px rgba(0,0,0,0.9)'}}>KM / H</div>
        </div>
      </Group>

      {/* D · the Shinkansen benchmark (124) */}
      <Group show={[f(13.4), f(16.9)]}>
        <TypeHeading text="Der Maßstab: der Shinkansen" x={72} y={150} size={28} at={f(13.7)} color={LIGHT} highlight />
        <Cap text="Shinkansen, Japan — ~210 km/h" />
        <Big text="Alles darunter" x={72} y={340} size={74} at={f(14.2)} />
        <Big text="zählt nicht" x={72} y={430} size={74} at={f(14.6)} color={EV.yellow} />
      </Group>

      {/* E · the railroad balks (125) */}
      <Group show={[f(16.7), C3P8_DURATION]}>
        <Big text="Pennsylvania Railroad:" x={72} y={300} size={70} at={f(17.4)} />
        <Big text="lieber billig & langsam" x={72} y={392} size={86} at={f(18.6)} color={EV.yellow} />
        <Cap text="aus Kostengründen — gegen das Tempo-Ziel" />
        <div style={{position: 'absolute', left: 1330, top: 720, transform: 'translate(-50%,-50%) rotate(-8deg)', opacity: interpolate(frame, [f(20.4), f(20.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 56, color: EV.red, border: `5px solid ${EV.red}`, padding: '6px 24px', borderRadius: 6, background: 'rgba(243,239,228,0.9)'}}>KOSTEN VOR TEMPO</div>
        </div>
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P8_DURATION} volume={DRONE} />
      <Sfx src="whoosh.mp3" at={f(6.1)} volume={0.4} />
      <Sfx src="whoosh.mp3" at={f(8.5)} volume={0.35} />
      <Sfx src="impact.mp3" at={f(9.0)} volume={0.5} />
      <Sfx src="whoosh.mp3" at={f(13.4)} volume={0.4} />
      <Sfx src="whoosh.mp3" at={f(16.7)} volume={0.35} />
      <Sfx src="sfx_stamp.mp3" at={f(20.4)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
