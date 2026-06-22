import {AbsoluteFill, Audio, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {cond, mono, EV} from './style/evidence';
import {Sfx, DroneBed} from './style/Sound';

const START = 754.423;
export const C3P18_DURATION = Math.round(22.6 * FPS);
const f = (s: number) => Math.round(s * FPS);
const DRONE = 0.06;
const LIGHT = '#f3efe4';

/** Fast full-bleed video cut with grade, vignette, quick fade + a line of text. */
const Seg: React.FC<{src: string; from: number; dur: number; text?: string; color?: string; center?: boolean; bw?: boolean}> = ({src, from, dur, text, color = LIGHT, center, bw}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <SegInner src={src} dur={dur} text={text} color={color} center={center} bw={bw} />
  </Sequence>
);
const SegInner: React.FC<{src: string; dur: number; text?: string; color: string; center?: boolean; bw?: boolean}> = ({src, dur, text, color, center, bw}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 4, dur - 4, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.06, 1.12]);
  const to = interpolate(frame, [2, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame, [2, 9], [-18, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#000', opacity: io}}>
      <OffthreadVideo src={staticFile(`clips/${src}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: bw ? 'grayscale(1) contrast(1.14)' : 'saturate(1.08) contrast(1.06)'}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 280px rgba(0,0,0,0.7)'}} />
      {text && (
        <div style={{position: 'absolute', left: 80, ...(center ? {top: 430} : {bottom: 90}), opacity: to, transform: `translateX(${tx}px)`, maxWidth: 1200}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: center ? 96 : 78, lineHeight: 0.98, textTransform: 'uppercase', color, textShadow: '0 3px 20px rgba(0,0,0,0.9)'}}>{text}</div>
        </div>
      )}
    </AbsoluteFill>
  );
};
const Tag: React.FC = () => (
  <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: LIGHT, opacity: 0.85, mixBlendMode: 'screen'}}>DER KERN DER SACHE</div>
);

export const Ch3P18Ev: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* 198 — the core */}
      <Seg src="china.mp4" from={0} dur={f(2.8)} text="Der Kern der Sache" color={EV.yellow} center />

      {/* 199 — not the technology */}
      <Seg src="japan.mp4" from={f(2.7)} dur={f(1.5)} text="Die Technik? Längst gelöst." />
      <Seg src="ice.mp4" from={f(4.1)} dur={f(1.8)} text="Die Technik? Längst gelöst." />

      {/* 200 — land · money · politics · bureaucracy */}
      <Seg src="oldline.mp4" from={f(5.8)} dur={f(2.3)} text="Teures Land" color={EV.yellow} bw />
      <Seg src="freight_us.mp4" from={f(8.0)} dur={f(2.2)} text="Fehlendes Geld" color={EV.yellow} bw />
      <Seg src="acela2.mp4" from={f(10.1)} dur={f(2.3)} text="Zersplitterte Politik" color={EV.yellow} bw />
      <Seg src="railpax.mp4" from={f(12.3)} dur={f(2.5)} text="Lähmende Bürokratie" color={EV.yellow} bw />

      {/* 201 — Japan proved it 60 years ago */}
      <Seg src="olympics64.mp4" from={f(14.7)} dur={f(2.9)} text="Japan bewies es —" bw />
      <Seg src="shinkansen2.mp4" from={f(17.55)} dur={f(3.0)} text="… schon vor 60 Jahren" />

      {/* 202 — a triumph of patience */}
      <Seg src="tgv.mp4" from={f(20.5)} dur={C3P18_DURATION - f(20.5)} text="Ein Triumph der Geduld" color={EV.yellow} center />

      <Tag />

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P18_DURATION} volume={DRONE} />
      <Sfx src="impact.mp3" at={f(0.1)} volume={0.45} />
      {[2.7, 4.1, 5.8, 8.0, 10.1, 12.3, 14.7, 17.55, 20.5].map((t, i) => (
        <Sfx key={i} src="whoosh.mp3" at={f(t)} volume={0.33} />
      ))}

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
