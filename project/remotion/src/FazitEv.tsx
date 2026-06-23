import {AbsoluteFill, Audio, Img, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig, spring} from 'remotion';
import {FPS} from './timeline';
import {cond, mono, EV} from './style/evidence';
import {GraphPaper, TapedPhoto, Stamp, Seal, Crosshair, Halftone, Highlight} from './style/Evidence';
import {Sfx, DroneBed, TypeClicks} from './style/Sound';

const START = 777.5;
export const FAZIT_DURATION = Math.round((881.96 - START) * FPS);
const f = (s: number) => Math.round(s * FPS);
const DRONE = 0.05;
const YEL = EV.yellow;

const isImg = (s: string) => /\.(jpg|jpeg|png)$/i.test(s);

/** Shared synthwave / retro-cyber overlay — tuned darker so it reads on night footage. */
const CyberGrade: React.FC<{bw?: boolean; frame: number}> = ({bw, frame}) => {
  const flick = 0.92 + 0.08 * Math.sin(frame * 0.7);
  return (
    <>
      <AbsoluteFill style={{background: 'linear-gradient(135deg, rgba(255,28,170,0.6) 0%, rgba(120,30,220,0.34) 45%, rgba(0,210,255,0.55) 100%)', mixBlendMode: 'overlay', opacity: (bw ? 0.66 : 0.5) * flick}} />
      <AbsoluteFill style={{background: 'radial-gradient(120% 80% at 50% 55%, transparent 32%, rgba(150,0,210,0.6) 100%)', mixBlendMode: 'screen', opacity: 0.55 * flick}} />
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.32) 0px, rgba(0,0,0,0.32) 1px, transparent 1px, transparent 3px)', mixBlendMode: 'multiply', opacity: 0.6}} />
      <AbsoluteFill style={{top: 'auto', bottom: 0, height: 280, backgroundImage: 'repeating-linear-gradient(90deg, rgba(0,235,255,0.5) 0px, rgba(0,235,255,0.5) 2px, transparent 2px, transparent 64px)', maskImage: 'linear-gradient(to top, black, transparent)', WebkitMaskImage: 'linear-gradient(to top, black, transparent)', mixBlendMode: 'screen', opacity: 0.2}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 360px rgba(4,1,12,0.95)'}} />
    </>
  );
};

const NEON_TEXT = '0 0 22px rgba(255,40,170,0.6), 0 0 8px rgba(0,220,255,0.55), 0 3px 18px rgba(0,0,0,0.95)';

/** Full-bleed shot — video (default) or image — graded + a YELLOW caption + optional cause number. */
const Shot: React.FC<{src: string; from: number; dur: number; text?: string; center?: boolean; bw?: boolean; num?: string; trim?: number}> = ({src, from, dur, text, center, bw, num, trim}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <ShotInner src={src} dur={dur} text={text} center={center} bw={bw} num={num} trim={trim} />
  </Sequence>
);
const ShotInner: React.FC<{src: string; dur: number; text?: string; center?: boolean; bw?: boolean; num?: string; trim?: number}> = ({src, dur, text, center, bw, num, trim}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 4, dur - 4, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const img = isImg(src);
  const scale = img ? interpolate(frame, [0, dur], [1.1, 1.22]) : interpolate(frame, [0, dur], [1.06, 1.12]);
  const pan = img ? interpolate(frame, [0, dur], [-22, 22]) : 0;
  const to = interpolate(frame, [2, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tx = interpolate(frame, [2, 9], [-18, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const vidFilter = bw ? 'grayscale(1) contrast(1.2) brightness(0.82)' : 'saturate(1.42) contrast(1.16) hue-rotate(-6deg) brightness(0.82)';
  const imgFilter = bw ? 'grayscale(1) contrast(1.16) brightness(0.8)' : 'sepia(0.15) saturate(1.35) contrast(1.12) brightness(0.82)';
  const media = {width: '100%', height: '100%', objectFit: 'cover' as const, transform: `scale(${scale}) translateX(${pan}px)`, filter: img ? imgFilter : vidFilter};
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f', opacity: io}}>
      {img
        ? <Img src={staticFile(src)} style={media} />
        : <OffthreadVideo src={staticFile(src)} muted trimBefore={trim ? Math.round(trim * FPS) : undefined} style={media} />}
      <CyberGrade bw={bw} frame={frame} />
      {num && (
        <div style={{position: 'absolute', right: 70, top: 70, textAlign: 'right', opacity: to}}>
          <div style={{fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.28em', color: '#7df9ff', textShadow: '0 0 10px rgba(0,220,255,0.8)'}}>URSACHE</div>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 150, lineHeight: 0.8, color: YEL, textShadow: '0 0 30px rgba(255,40,170,0.7), 0 0 12px rgba(0,220,255,0.6)'}}>{num}</div>
        </div>
      )}
      {text && (
        <div style={{position: 'absolute', left: 80, ...(center ? {top: 420} : {bottom: 90}), opacity: to, transform: `translateX(${tx}px)`, maxWidth: 1280}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: center ? 100 : 76, lineHeight: 0.98, textTransform: 'uppercase', color: YEL, textShadow: NEON_TEXT}}>{text}</div>
        </div>
      )}
    </AbsoluteFill>
  );
};

/** Decision montage — cross-cycles VIDEO clips with one persistent yellow caption. */
const Cycler: React.FC<{srcs: {src: string; trim?: number}[]; from: number; dur: number; text: string}> = ({srcs, from, dur, text}) => {
  const each = Math.floor(dur / srcs.length);
  return (
    <Sequence from={from} durationInFrames={dur} layout="none">
      {srcs.map((s, i) => {
        const d = i === srcs.length - 1 ? dur - i * each : each;
        return (
          <Sequence key={i} from={i * each} durationInFrames={d} layout="none">
            <CycClip src={s.src} trim={s.trim} dur={d} />
          </Sequence>
        );
      })}
      <CycCaption text={text} dur={dur} />
    </Sequence>
  );
};
const CycClip: React.FC<{src: string; trim?: number; dur: number}> = ({src, trim, dur}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 5, dur - 5, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, dur], [1.08, 1.16]);
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f', opacity: io}}>
      <OffthreadVideo src={staticFile(src)} muted trimBefore={trim ? Math.round(trim * FPS) : undefined} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`, filter: 'saturate(1.4) contrast(1.16) hue-rotate(-6deg) brightness(0.8)'}} />
      <CyberGrade frame={frame} />
    </AbsoluteFill>
  );
};
const CycCaption: React.FC<{text: string; dur: number}> = ({text, dur}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [2, 10, dur - 6, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 80, bottom: 90, opacity: o, maxWidth: 1280}}>
      <div style={{fontFamily: cond, fontWeight: 700, fontSize: 76, lineHeight: 0.98, textTransform: 'uppercase', color: YEL, textShadow: NEON_TEXT}}>{text}</div>
    </div>
  );
};

/** ── Collage title card — evidence board of American rail-history symbols ── */
type P = {src: string; cx: number; cy: number; w: number; rot: number; cap: string};
const PHOTOS: P[] = [
  {src: 'goldenspike.jpg', cx: 290, cy: 200, w: 330, rot: -5, cap: '1869 · GOLDEN SPIKE'},
  {src: 'pullman.jpg', cx: 720, cy: 172, w: 300, rot: 3, cap: 'PULLMAN-ÄRA'},
  {src: 'gg1.jpg', cx: 1180, cy: 180, w: 320, rot: -3, cap: 'PRR GG1'},
  {src: 'metroliner.jpg', cx: 1645, cy: 250, w: 320, rot: 4, cap: '1969 · METROLINER'},
  {src: 'm497.jpg', cx: 1705, cy: 625, w: 300, rot: -4, cap: '1966 · JET-ZUG'},
  {src: 'penncentral.jpg', cx: 235, cy: 520, w: 300, rot: 4, cap: '1970 · KOLLAPS'},
  {src: 'amtrak70s.jpg', cx: 300, cy: 850, w: 320, rot: -4, cap: '1971 · AMTRAK'},
  {src: 'spfreight.jpg', cx: 740, cy: 905, w: 300, rot: 3, cap: 'GÜTER ZUERST'},
  {src: 'cahsr_cedar.jpg', cx: 1230, cy: 900, w: 330, rot: -3, cap: 'CAHSR'},
  {src: 'blwest.jpg', cx: 1680, cy: 930, w: 300, rot: 4, cap: 'BRIGHTLINE'},
];

const Thread: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  const pts = PHOTOS.map((p) => [p.cx, p.cy] as const);
  const d = 'M ' + pts.map(([x, y]) => `${x} ${y}`).join(' L ');
  const len = 9000;
  const p = interpolate(frame - at, [0, 40], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <svg style={{position: 'absolute', inset: 0, zIndex: 5}} width={1920} height={1080}>
      <path d={d} fill="none" stroke={EV.red} strokeWidth={2.5} strokeOpacity={0.8} strokeDasharray={len} strokeDashoffset={len * (1 - p)} />
      {pts.map(([x, y], i) => {
        const po = interpolate(frame - at - i * 2, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return <circle key={i} cx={x} cy={y} r={6} fill={EV.red} opacity={po} />;
      })}
    </svg>
  );
};

const CollageTitle: React.FC<{from: number; dur: number}> = ({from, dur}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <CollageInner dur={dur} />
  </Sequence>
);
const CollageInner: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const out = interpolate(frame, [dur - 6, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const cardS = spring({frame: frame - f(2.4), fps, config: {damping: 14, stiffness: 140}});
  const cardSc = interpolate(cardS, [0, 1], [0.8, 1]);
  const cardO = interpolate(frame - f(2.4), [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const qO = interpolate(frame - f(3.6), [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: out}}>
      <GraphPaper />
      <Crosshair x={70} y={70} />
      <Crosshair x={1816} y={70} at={3} />
      <Crosshair x={70} y={980} at={6} />
      <Crosshair x={1816} y={980} at={9} />
      {PHOTOS.map((p, i) => (
        <TapedPhoto key={i} src={p.src} cx={p.cx} cy={p.cy} w={p.w} rot={p.rot} at={i * 2} caption={p.cap} />
      ))}
      <Thread at={f(0.9)} />
      {/* central verdict sheet pinned over the board */}
      <div style={{position: 'absolute', left: '50%', top: 540, width: 880, transform: `translate(-50%,-50%) rotate(-1deg) scale(${cardSc})`, opacity: cardO, background: '#f5f1e6', padding: '40px 56px 48px', boxShadow: '8px 14px 26px rgba(20,16,10,0.45)', zIndex: 10}}>
        <div style={{position: 'absolute', top: -16, left: '50%', transform: 'translateX(-50%) rotate(-3deg)', width: 150, height: 34, background: EV.tape}} />
        <div style={{position: 'absolute', top: -14, left: 60, transform: 'rotate(6deg)', width: 110, height: 30, background: EV.tape}} />
        <div style={{position: 'absolute', top: -14, right: 60, transform: 'rotate(-7deg)', width: 110, height: 30, background: EV.tape}} />
        <div style={{fontFamily: mono, fontWeight: 700, fontSize: 24, letterSpacing: '0.32em', color: EV.inkSoft, textTransform: 'uppercase'}}>Abschlussbericht · Akte USA-Bahn</div>
        <div style={{position: 'relative', display: 'inline-block', marginTop: 4}}>
          <div style={{position: 'absolute', left: -8, top: '20%', height: '64%', width: '104%', background: EV.yellow, transform: 'skewX(-6deg)', zIndex: 0}} />
          <div style={{position: 'relative', zIndex: 1, fontFamily: cond, fontWeight: 700, fontSize: 196, lineHeight: 0.88, letterSpacing: '0.02em', color: EV.ink, textTransform: 'uppercase'}}>Fazit</div>
        </div>
        <div style={{opacity: qO, marginTop: 14, fontFamily: mono, fontSize: 27, lineHeight: 1.35, color: EV.ink}}>
          Warum fährt die Bahn in Europa, Japan &amp; China —<br />aber nicht in den USA?
        </div>
      </div>
      <Seal text={'U.S. RAIL\n1869 – 2026'} x={300} y={560} at={f(3.2)} size={150} rot={-12} />
      <Stamp text="Akte geschlossen" x={1360} y={760} at={f(4.0)} size={52} rot={-9} />
      <Halftone opacity={0.12} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 320px rgba(70,60,42,0.5)'}} />
    </AbsoluteFill>
  );
};

const Tag: React.FC = () => (
  <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: '#7df9ff', opacity: 0.9, mixBlendMode: 'screen', textShadow: '0 0 10px rgba(0,220,255,0.8)'}}>FAZIT — DIE SUMME VIELER URSACHEN</div>
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
      {/* collage title + question */}
      <CollageTitle from={0} dur={f(6.1)} />

      {/* no single answer */}
      <Shot src="clips/citynight.mp4" from={f(6.1)} dur={f(4.64)} text="Keine einzelne Antwort" />

      {/* CAUSE 1 — geography */}
      <Shot src="clips/citynight.mp4" from={f(10.74)} dur={f(6.36)} trim={6} num="01" text="Kompakt. Dicht besiedelt." />
      <Shot src="clips/highway.mp4" from={f(17.1)} dur={f(3.07)} text="Riesig. Weit zersiedelt." />

      {/* CAUSE 2 — timing */}
      <Shot src="clips/carad.mp4" from={f(20.17)} dur={f(5.83)} num="02" text="Das Auto kam zuerst" bw />
      <Shot src="clips/carcity.mp4" from={f(26.0)} dur={f(4.06)} text="Städte um das Auto gebaut" />
      <Shot src="clips/station_night.mp4" from={f(30.06)} dur={f(3.35)} text="Europas Städte: längst dicht" />

      {/* CAUSE 3 — money */}
      <Shot src="clips/citynight.mp4" from={f(33.41)} dur={f(1.75)} trim={10} num="03" text="Das Geld" />
      <Shot src="clips/highway.mp4" from={f(35.16)} dur={f(2.84)} trim={4} text="Milliarden für Straßen" />
      <Shot src="clips/airport.mp4" from={f(38.0)} dur={f(3.68)} text="… und Flughäfen" />
      <Shot src="clips/station_night.mp4" from={f(41.68)} dur={f(2.74)} trim={5} text="Anderswo: öffentliche Aufgabe" />
      <Shot src="clips/vegas.mp4" from={f(45.04)} dur={f(2.42)} text="In den USA: muss Gewinn bringen" />

      {/* CAUSE 4 — ownership */}
      <Shot src="clips/freight_us.mp4" from={f(47.46)} dur={f(3.0)} num="04" text="Die Eigentumsfrage" bw />
      <Shot src="clips/station_night.mp4" from={f(50.46)} dur={f(5.0)} trim={8} text="Personenzug: Gast auf fremdem Grund" />

      {/* CAUSE 5 — the modern factor */}
      <Shot src="clips/citynight.mp4" from={f(55.54)} dur={f(2.32)} trim={2} num="05" text="Der moderne Faktor" />
      <Shot src="clips/air.mp4" from={f(57.86)} dur={f(2.4)} text="Teures Land" bw />
      <Shot src="clips/citynight.mp4" from={f(60.26)} dur={f(2.4)} trim={12} text="Endlose Klagen" />
      <Shot src="clips/subway.mp4" from={f(62.66)} dur={f(2.4)} text="Zersplitterte Zuständigkeit" bw />
      <Shot src="clips/highway.mp4" from={f(65.06)} dur={f(2.4)} trim={8} text="Versiegende Fördergelder" />

      {/* synthesis */}
      <Shot src="clips/station_night.mp4" from={f(68.55)} dur={f(2.5)} trim={11} text="Kein Unfall" />
      <Cycler srcs={[{src: 'clips/citynight.mp4', trim: 3}, {src: 'clips/highway.mp4', trim: 2}, {src: 'clips/subway.mp4'}, {src: 'clips/vegas.mp4', trim: 1}]} from={f(71.06)} dur={f(7.4)} text="Eine Kette von Entscheidungen" />
      <Shot src="clips/carcity.mp4" from={f(78.7)} dur={f(3.06)} trim={2} text="Einzeln nachvollziehbar" />
      <Shot src="clips/station_night.mp4" from={f(81.76)} dur={f(3.83)} trim={1} text="Zusammen: das beste Netz demontiert" bw />

      {/* hope */}
      <Shot src="clips/vegas.mp4" from={f(85.59)} dur={f(1.99)} text="Ein Hoffnungsschimmer" />
      <Shot src="clips/brightline_run.mp4" from={f(87.58)} dur={f(3.08)} text="Brightline baut" />
      <Shot src="clips/acela3.mp4" from={f(90.66)} dur={f(1.9)} text="Geld für den Korridor" />
      <Shot src="clips/wind.mp4" from={f(92.56)} dur={f(2.48)} text="Umweltbewusstsein wächst" />

      {/* reality check */}
      <Shot src="clips/highway.mp4" from={f(95.04)} dur={f(6.08)} trim={2} text="70 Jahre Rückstand" />

      {/* closer */}
      <Shot src="clips/station_night.mp4" from={f(101.12)} dur={FAZIT_DURATION - f(101.12)} trim={3} text="Der Weg zurück ist länger." center bw />

      <Tag />

      {/* ── driving sound design ── */}
      <MusicBed />
      <DroneBed durationInFrames={FAZIT_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.4)} n={5} gap={6} volume={0.4} />
      <Sfx src="impact.mp3" at={f(2.4)} volume={0.45} />
      {[10.74, 20.17, 33.41, 47.46, 55.54].map((t, i) => (
        <Sfx key={`imp${i}`} src="impact.mp3" at={f(t)} volume={0.34} />
      ))}
      <Sfx src="riser.mp3" at={f(83.0)} volume={0.34} dur={f(3.0)} />
      <Sfx src="riser.mp3" at={f(99.0)} volume={0.32} dur={f(2.5)} />
      {[6.1, 10.74, 17.1, 20.17, 26.0, 30.06, 33.41, 35.16, 38.0, 41.68, 45.04, 47.46, 50.46, 55.54, 57.86, 60.26, 62.66, 65.06, 68.55, 71.06, 78.7, 81.76, 85.59, 87.58, 90.66, 92.56, 95.04, 101.12].map((t, i) => (
        <Sfx key={`wh${i}`} src="whoosh.mp3" at={f(t)} volume={0.28} />
      ))}

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
