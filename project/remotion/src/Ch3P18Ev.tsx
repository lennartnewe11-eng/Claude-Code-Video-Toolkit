import {AbsoluteFill, Audio, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {cond, mono, EV} from './style/evidence';
import {Sfx, DroneBed} from './style/Sound';

const START = 754.423;
export const C3P18_DURATION = Math.round(22.6 * FPS);
const f = (s: number) => Math.round(s * FPS);
const DRONE = 0.05;
const LIGHT = '#f3efe4';

/** Fast full-bleed video cut with a synthwave / retro-cyber grade, vignette, quick fade + a line of text. */
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
  // gentle neon flicker on the synthwave overlays
  const flick = 0.92 + 0.08 * Math.sin(frame * 0.7);
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f', opacity: io}}>
      <OffthreadVideo
        src={staticFile(`clips/${src}`)}
        muted
        style={{
          width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`,
          filter: bw
            ? 'grayscale(1) contrast(1.18) brightness(1.08)'
            : 'saturate(1.38) contrast(1.12) hue-rotate(-6deg) brightness(1.03)',
        }}
      />
      {/* duotone magenta→cyan wash — turns every shot into a synthwave palette */}
      <AbsoluteFill style={{background: 'linear-gradient(135deg, rgba(255,28,170,0.55) 0%, rgba(120,30,220,0.30) 45%, rgba(0,210,255,0.50) 100%)', mixBlendMode: 'overlay', opacity: (bw ? 0.62 : 0.42) * flick}} />
      {/* neon edge bloom */}
      <AbsoluteFill style={{background: 'radial-gradient(120% 80% at 50% 55%, transparent 40%, rgba(170,0,220,0.45) 100%)', mixBlendMode: 'screen', opacity: 0.5 * flick}} />
      {/* CRT scanlines */}
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.28) 0px, rgba(0,0,0,0.28) 1px, transparent 1px, transparent 3px)', mixBlendMode: 'multiply', opacity: 0.55}} />
      {/* faint synth horizon grid, bottom */}
      <AbsoluteFill style={{top: 'auto', bottom: 0, height: 260, backgroundImage: 'repeating-linear-gradient(90deg, rgba(0,235,255,0.5) 0px, rgba(0,235,255,0.5) 2px, transparent 2px, transparent 64px)', maskImage: 'linear-gradient(to top, black, transparent)', WebkitMaskImage: 'linear-gradient(to top, black, transparent)', mixBlendMode: 'screen', opacity: 0.18}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 300px rgba(5,1,15,0.85)'}} />
      {text && (
        <div style={{position: 'absolute', left: 80, ...(center ? {top: 430} : {bottom: 90}), opacity: to, transform: `translateX(${tx}px)`, maxWidth: 1200}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: center ? 96 : 78, lineHeight: 0.98, textTransform: 'uppercase', color, textShadow: '0 0 22px rgba(255,40,170,0.55), 0 0 8px rgba(0,220,255,0.5), 0 3px 18px rgba(0,0,0,0.9)'}}>{text}</div>
        </div>
      )}
    </AbsoluteFill>
  );
};
const Tag: React.FC = () => (
  <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: '#7df9ff', opacity: 0.9, mixBlendMode: 'screen', textShadow: '0 0 10px rgba(0,220,255,0.8)'}}>DER KERN DER SACHE</div>
);

/** Driving synth bed that swells across the part. */
const MusicBed: React.FC = () => {
  const total = C3P18_DURATION;
  return (
    <Audio
      src={staticFile('audio/musicBed.mp3')}
      volume={(fr) => interpolate(fr, [0, f(2), total - f(2.5), total], [0.1, 0.2, 0.2, 0.05], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}
    />
  );
};

export const Ch3P18Ev: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f'}}>
      {/* 198 — the core */}
      <Seg src="china.mp4" from={0} dur={f(2.8)} text="Der Kern der Sache" color={EV.yellow} center />

      {/* 199 — not the technology */}
      <Seg src="japan.mp4" from={f(2.7)} dur={f(1.5)} text="Die Technik? Längst gelöst." />
      <Seg src="ice.mp4" from={f(4.1)} dur={f(1.8)} text="Die Technik? Längst gelöst." />

      {/* 200 — land · money · politics · bureaucracy (varied, non-train where it fits) */}
      <Seg src="air.mp4" from={f(5.8)} dur={f(2.3)} text="Teures Land" color={EV.yellow} />
      <Seg src="freight_us.mp4" from={f(8.0)} dur={f(2.2)} text="Fehlendes Geld" color={EV.yellow} bw />
      <Seg src="highway.mp4" from={f(10.1)} dur={f(2.3)} text="Zersplitterte Politik" color={EV.yellow} />
      <Seg src="railpax.mp4" from={f(12.3)} dur={f(2.5)} text="Lähmende Bürokratie" color={EV.yellow} bw />

      {/* 201 — Japan proved it 60 years ago (symbolic Tokyo, not a train) */}
      <Seg src="tokyo.mp4" from={f(14.7)} dur={f(2.9)} text="Japan bewies es —" />
      <Seg src="shinkansen2.mp4" from={f(17.55)} dur={f(3.0)} text="… schon vor 60 Jahren" />

      {/* 202 — a triumph of patience */}
      <Seg src="tgv.mp4" from={f(20.5)} dur={C3P18_DURATION - f(20.5)} text="Ein Triumph der Geduld" color={EV.yellow} center />

      <Tag />

      {/* ── driving sound design ── */}
      <MusicBed />
      <DroneBed durationInFrames={C3P18_DURATION} volume={DRONE} />
      <Sfx src="impact.mp3" at={f(0.1)} volume={0.5} />
      {/* heavy hits on the four causes */}
      {[5.8, 8.0, 10.1, 12.3].map((t, i) => (
        <Sfx key={`imp${i}`} src="impact.mp3" at={f(t)} volume={0.3} />
      ))}
      {/* riser into the final line */}
      <Sfx src="riser.mp3" at={f(18.0)} volume={0.4} dur={f(3.0)} />
      {[2.7, 4.1, 5.8, 8.0, 10.1, 12.3, 14.7, 17.55, 20.5].map((t, i) => (
        <Sfx key={`wh${i}`} src="whoosh.mp3" at={f(t)} volume={0.33} />
      ))}

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
