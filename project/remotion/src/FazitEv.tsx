import {AbsoluteFill, Audio, Img, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {cond, mono, EV} from './style/evidence';
import {Sfx, DroneBed} from './style/Sound';

const START = 777.5;
export const FAZIT_DURATION = Math.round((881.96 - START) * FPS);
const f = (s: number) => Math.round(s * FPS);
const DRONE = 0.05;
const LIGHT = '#f3efe4';
const CYAN = '#7df9ff';

const isImg = (s: string) => /\.(jpg|jpeg|png)$/i.test(s);

/** Shared synthwave / retro-cyber overlay stack (duotone, bloom, scanlines, grid). */
const CyberGrade: React.FC<{bw?: boolean; frame: number}> = ({bw, frame}) => {
  const flick = 0.92 + 0.08 * Math.sin(frame * 0.7);
  return (
    <>
      <AbsoluteFill style={{background: 'linear-gradient(135deg, rgba(255,28,170,0.55) 0%, rgba(120,30,220,0.30) 45%, rgba(0,210,255,0.50) 100%)', mixBlendMode: 'overlay', opacity: (bw ? 0.62 : 0.42) * flick}} />
      <AbsoluteFill style={{background: 'radial-gradient(120% 80% at 50% 55%, transparent 40%, rgba(170,0,220,0.45) 100%)', mixBlendMode: 'screen', opacity: 0.5 * flick}} />
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.28) 0px, rgba(0,0,0,0.28) 1px, transparent 1px, transparent 3px)', mixBlendMode: 'multiply', opacity: 0.55}} />
      <AbsoluteFill style={{top: 'auto', bottom: 0, height: 260, backgroundImage: 'repeating-linear-gradient(90deg, rgba(0,235,255,0.5) 0px, rgba(0,235,255,0.5) 2px, transparent 2px, transparent 64px)', maskImage: 'linear-gradient(to top, black, transparent)', WebkitMaskImage: 'linear-gradient(to top, black, transparent)', mixBlendMode: 'screen', opacity: 0.18}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 300px rgba(5,1,15,0.85)'}} />
    </>
  );
};

const NEON_TEXT = '0 0 22px rgba(255,40,170,0.55), 0 0 8px rgba(0,220,255,0.5), 0 3px 18px rgba(0,0,0,0.9)';

/** Full-bleed shot — video or image — graded + a line of text + optional cause number. */
const Shot: React.FC<{src: string; from: number; dur: number; text?: string; color?: string; center?: boolean; bw?: boolean; num?: string}> = ({src, from, dur, text, color = LIGHT, center, bw, num}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <ShotInner src={src} dur={dur} text={text} color={color} center={center} bw={bw} num={num} />
  </Sequence>
);
const ShotInner: React.FC<{src: string; dur: number; text?: string; color: string; center?: boolean; bw?: boolean; num?: string}> = ({src, dur, text, color, center, bw, num}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 4, dur - 4, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const img = isImg(src);
  const scale = img ? interpolate(frame, [0, dur], [1.1, 1.22]) : interpolate(frame, [0, dur], [1.06, 1.12]);
  const pan = img ? interpolate(frame, [0, dur], [-22, 22]) : 0;
  const to = interpolate(frame, [2, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame, [2, 9], [-18, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const vidFilter = bw ? 'grayscale(1) contrast(1.18) brightness(1.08)' : 'saturate(1.38) contrast(1.12) hue-rotate(-6deg) brightness(1.03)';
  const imgFilter = bw ? 'grayscale(1) contrast(1.12) brightness(1.05)' : 'sepia(0.15) saturate(1.3) contrast(1.08) brightness(1.04)';
  const media = {width: '100%', height: '100%', objectFit: 'cover' as const, transform: `scale(${scale}) translateX(${pan}px)`, filter: img ? imgFilter : vidFilter};
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f', opacity: io}}>
      {img
        ? <Img src={staticFile(src)} style={media} />
        : <OffthreadVideo src={staticFile(src)} muted style={media} />}
      <CyberGrade bw={bw} frame={frame} />
      {num && (
        <div style={{position: 'absolute', right: 70, top: 70, textAlign: 'right', opacity: to}}>
          <div style={{fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.28em', color: CYAN, textShadow: '0 0 10px rgba(0,220,255,0.8)'}}>URSACHE</div>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 150, lineHeight: 0.8, color: EV.yellow, textShadow: '0 0 30px rgba(255,40,170,0.7), 0 0 12px rgba(0,220,255,0.6)'}}>{num}</div>
        </div>
      )}
      {text && (
        <div style={{position: 'absolute', left: 80, ...(center ? {top: 420} : {bottom: 90}), opacity: to, transform: `translateX(${tx}px)`, maxWidth: 1280}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: center ? 100 : 76, lineHeight: 0.98, textTransform: 'uppercase', color, textShadow: NEON_TEXT}}>{text}</div>
        </div>
      )}
    </AbsoluteFill>
  );
};

/** Decision montage — cross-cycles images with one persistent caption. */
const Cycler: React.FC<{srcs: string[]; from: number; dur: number; text: string}> = ({srcs, from, dur, text}) => {
  const each = Math.floor(dur / srcs.length);
  return (
    <Sequence from={from} durationInFrames={dur} layout="none">
      {srcs.map((s, i) => (
        <Sequence key={i} from={i * each} durationInFrames={i === srcs.length - 1 ? dur - i * each : each} layout="none">
          <CycImg src={s} dur={i === srcs.length - 1 ? dur - i * each : each} />
        </Sequence>
      ))}
      <CycCaption text={text} dur={dur} />
    </Sequence>
  );
};
const CycImg: React.FC<{src: string; dur: number}> = ({src, dur}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 5, dur - 5, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.12, 1.2]);
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f', opacity: io}}>
      <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: 'grayscale(1) contrast(1.16) brightness(1.06)'}} />
      <CyberGrade bw frame={frame} />
    </AbsoluteFill>
  );
};
const CycCaption: React.FC<{text: string; dur: number}> = ({text, dur}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [2, 10, dur - 6, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 80, bottom: 90, opacity: o, maxWidth: 1280}}>
      <div style={{fontFamily: cond, fontWeight: 700, fontSize: 76, lineHeight: 0.98, textTransform: 'uppercase', color: LIGHT, textShadow: NEON_TEXT}}>{text}</div>
    </div>
  );
};

/** Neon synthwave title card. */
const TitleCard: React.FC<{from: number; dur: number}> = ({from, dur}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <TitleInner dur={dur} />
  </Sequence>
);
const TitleInner: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 8, dur - 6, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const titleY = interpolate(frame, [0, 18], [40, 0], {extrapolateRight: 'clamp'});
  const qO = interpolate(frame, [f(1.3), f(2.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sun = interpolate(frame, [0, dur], [0, -40]);
  return (
    <AbsoluteFill style={{backgroundColor: '#0a0118', opacity: io, overflow: 'hidden'}}>
      {/* sky glow */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, #1a0533 0%, #3a0a4a 45%, #ff2e7e 72%, #ff7a3d 100%)', opacity: 0.85}} />
      {/* sun */}
      <div style={{position: 'absolute', left: '50%', top: 360 + sun, width: 360, height: 360, marginLeft: -180, borderRadius: '50%', background: 'radial-gradient(circle, #ffe14d 0%, #ff5ea8 70%, transparent 72%)', filter: 'blur(2px)'}} />
      {/* perspective grid floor */}
      <AbsoluteFill style={{top: '62%', background: 'repeating-linear-gradient(0deg, rgba(0,235,255,0.0) 0px, rgba(0,235,255,0.0) 38px, rgba(0,235,255,0.7) 39px, rgba(0,235,255,0.7) 41px), repeating-linear-gradient(90deg, transparent 0px, transparent 78px, rgba(255,40,170,0.55) 79px, rgba(255,40,170,0.55) 81px)', transform: 'perspective(420px) rotateX(68deg)', transformOrigin: 'top', maskImage: 'linear-gradient(to bottom, black, transparent 80%)', WebkitMaskImage: 'linear-gradient(to bottom, black, transparent 80%)'}} />
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0px, rgba(0,0,0,0.25) 1px, transparent 1px, transparent 3px)', mixBlendMode: 'multiply', opacity: 0.5}} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{textAlign: 'center', transform: `translateY(${titleY}px)`}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 200, lineHeight: 0.9, letterSpacing: '0.04em', textTransform: 'uppercase', color: '#fff', textShadow: '0 0 40px rgba(255,40,170,0.9), 0 0 18px rgba(0,220,255,0.8), 0 0 90px rgba(255,40,170,0.6)'}}>Fazit</div>
          <div style={{marginTop: 26, opacity: qO, maxWidth: 1300, marginLeft: 'auto', marginRight: 'auto', fontFamily: cond, fontWeight: 700, fontSize: 54, lineHeight: 1.04, textTransform: 'uppercase', color: EV.yellow, textShadow: NEON_TEXT}}>
            Warum fährt die Bahn in Europa, Japan &amp; China — aber nicht in den USA?
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Tag: React.FC = () => (
  <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: CYAN, opacity: 0.9, mixBlendMode: 'screen', textShadow: '0 0 10px rgba(0,220,255,0.8)'}}>FAZIT — DIE SUMME VIELER URSACHEN</div>
);

const MusicBed: React.FC = () => {
  const total = FAZIT_DURATION;
  return (
    <Audio
      src={staticFile('audio/musicBed.mp3')}
      volume={(fr) => interpolate(fr, [0, f(3), total - f(3), total], [0.08, 0.19, 0.19, 0.04], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}
    />
  );
};

export const FazitEv: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f'}}>
      {/* title + question */}
      <TitleCard from={0} dur={f(6.1)} />

      {/* no single answer — the sum of many causes */}
      <Shot src="maps/railmap1871.jpg" from={f(6.1)} dur={f(4.64)} text="Keine einzelne Antwort" color={LIGHT} />

      {/* CAUSE 1 — geography */}
      <Shot src="maps/europe1852.jpg" from={f(10.74)} dur={f(6.36)} num="01" text="Kompakt. Dicht besiedelt." color={EV.yellow} />
      <Shot src="maps/america1852.jpg" from={f(17.1)} dur={f(3.07)} text="Riesig. Weit zersiedelt." />

      {/* CAUSE 2 — timing */}
      <Shot src="clips/carad.mp4" from={f(20.17)} dur={f(5.83)} num="02" text="Das Auto kam zuerst" color={EV.yellow} />
      <Shot src="clips/carcity.mp4" from={f(26.0)} dur={f(4.06)} text="Städte um das Auto gebaut" />
      <Shot src="maps/europe1852.jpg" from={f(30.06)} dur={f(3.35)} text="Europas Städte: längst dicht" />

      {/* CAUSE 3 — money */}
      <Shot src="photos/bill.jpg" from={f(33.41)} dur={f(1.75)} num="03" text="Das Geld" color={EV.yellow} />
      <Shot src="photos/interchange.jpg" from={f(35.16)} dur={f(2.84)} text="Milliarden für Straßen" bw />
      <Shot src="clips/airport.mp4" from={f(38.0)} dur={f(3.68)} text="… und Flughäfen" />
      <Shot src="photos/shinkansen0.jpg" from={f(41.68)} dur={f(2.74)} text="Anderswo: öffentliche Aufgabe" />
      <Shot src="photos/stock.jpg" from={f(45.04)} dur={f(2.42)} text="In den USA: muss Gewinn bringen" bw />

      {/* CAUSE 4 — ownership */}
      <Shot src="clips/freight_us.mp4" from={f(47.46)} dur={f(3.0)} num="04" text="Die Eigentumsfrage" color={EV.yellow} bw />
      <Shot src="photos/passengertrain.jpg" from={f(50.46)} dur={f(5.0)} text="Personenzug: Gast auf fremdem Grund" bw />

      {/* CAUSE 5 — the modern factor */}
      <Shot src="photos/cahsr_drone.jpg" from={f(55.54)} dur={f(2.32)} num="05" text="Der moderne Faktor" color={EV.yellow} />
      <Shot src="photos/valley.jpg" from={f(57.86)} dur={f(2.4)} text="Teures Land" />
      <Shot src="photos/gavel.jpg" from={f(60.26)} dur={f(2.4)} text="Endlose Klagen" bw />
      <Shot src="photos/capitol.jpg" from={f(62.66)} dur={f(2.4)} text="Zersplitterte Zuständigkeit" bw />
      <Shot src="photos/bond.jpg" from={f(65.06)} dur={f(2.4)} text="Versiegende Fördergelder" bw />

      {/* synthesis */}
      <Shot src="photos/usrail70s.jpg" from={f(68.55)} dur={f(2.5)} text="Kein Unfall" bw />
      <Cycler srcs={['photos/eisenhower.jpg', 'photos/ford.jpg', 'photos/lbjsign.jpg', 'photos/trump.jpg']} from={f(71.06)} dur={f(7.4)} text="Eine Kette von Entscheidungen" />
      <Shot src="photos/lbjsign.jpg" from={f(78.7)} dur={f(3.06)} text="Einzeln nachvollziehbar" bw />
      <Shot src="photos/oldtracks.jpg" from={f(81.76)} dur={f(3.83)} text="Zusammen: das beste Netz demontiert" color={EV.yellow} bw />

      {/* hope */}
      <Shot src="photos/cahsr_cedar.jpg" from={f(85.59)} dur={f(1.99)} text="Ein Hoffnungsschimmer" color={CYAN} />
      <Shot src="clips/brightline_run.mp4" from={f(87.58)} dur={f(3.08)} text="Brightline baut" />
      <Shot src="clips/acela3.mp4" from={f(90.66)} dur={f(1.9)} text="Geld für den Korridor" />
      <Shot src="clips/wind.mp4" from={f(92.56)} dur={f(2.48)} text="Umweltbewusstsein wächst" color={CYAN} />

      {/* reality check */}
      <Shot src="clips/traffic.mp4" from={f(95.04)} dur={f(6.08)} text="70 Jahre Rückstand" color={EV.yellow} />

      {/* closer */}
      <Shot src="photos/oldtracks.jpg" from={f(101.12)} dur={FAZIT_DURATION - f(101.12)} text="Der Weg zurück ist länger." color={EV.yellow} center bw />

      <Tag />

      {/* ── driving sound design ── */}
      <MusicBed />
      <DroneBed durationInFrames={FAZIT_DURATION} volume={DRONE} />
      <Sfx src="impact.mp3" at={f(0.1)} volume={0.5} />
      {/* heavy hits on each cause marker */}
      {[10.74, 20.17, 33.41, 47.46, 55.54].map((t, i) => (
        <Sfx key={`imp${i}`} src="impact.mp3" at={f(t)} volume={0.34} />
      ))}
      {/* riser into the hopeful turn + into the closer */}
      <Sfx src="riser.mp3" at={f(83.0)} volume={0.34} dur={f(3.0)} />
      <Sfx src="riser.mp3" at={f(99.0)} volume={0.32} dur={f(2.5)} />
      {/* cut whooshes */}
      {[6.1, 10.74, 17.1, 20.17, 26.0, 30.06, 33.41, 35.16, 38.0, 41.68, 45.04, 47.46, 50.46, 55.54, 57.86, 60.26, 62.66, 65.06, 68.55, 71.06, 78.7, 81.76, 85.59, 87.58, 90.66, 92.56, 95.04, 101.12].map((t, i) => (
        <Sfx key={`wh${i}`} src="whoosh.mp3" at={f(t)} volume={0.28} />
      ))}

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
