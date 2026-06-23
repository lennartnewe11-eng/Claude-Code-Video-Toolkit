import {AbsoluteFill, Audio, Img, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig, spring} from 'remotion';
import {FPS} from './timeline';
import {cond, mono, EV} from './style/evidence';
import {GraphPaper, TapedPhoto, Stamp, Seal, Crosshair, Halftone} from './style/Evidence';
import {Sfx, DroneBed, TypeClicks} from './style/Sound';

const START = 777.5;
export const FAZIT_DURATION = Math.round((881.96 - START) * FPS);
const f = (s: number) => Math.round(s * FPS);
const DRONE = 0.05;
const YEL = EV.yellow;

const isImg = (s: string) => /\.(jpg|jpeg|png)$/i.test(s);

/** Synthwave / retro-cyber overlay on the FOOTAGE (tuned darker for night clips). */
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

/** Full-bleed shot — video (default) or image — graded + optional cause number. No baked-in caption. */
const Shot: React.FC<{src: string; from: number; dur: number; bw?: boolean; num?: string; trim?: number}> = ({src, from, dur, bw, num, trim}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <ShotInner src={src} dur={dur} bw={bw} num={num} trim={trim} />
  </Sequence>
);
const ShotInner: React.FC<{src: string; dur: number; bw?: boolean; num?: string; trim?: number}> = ({src, dur, bw, num, trim}) => {
  const frame = useCurrentFrame();
  const io = interpolate(frame, [0, 4, dur - 4, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const img = isImg(src);
  const scale = img ? interpolate(frame, [0, dur], [1.1, 1.22]) : interpolate(frame, [0, dur], [1.06, 1.12]);
  const pan = img ? interpolate(frame, [0, dur], [-22, 22]) : 0;
  const to = interpolate(frame, [2, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
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
          <div style={{fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.28em', color: '#7df9ff', textShadow: '0 2px 8px rgba(0,0,0,0.85)'}}>URSACHE</div>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 150, lineHeight: 0.8, color: YEL, textShadow: '0 3px 14px rgba(0,0,0,0.9)'}}>{num}</div>
        </div>
      )}
    </AbsoluteFill>
  );
};

/** Decision montage — cross-cycles VIDEO clips (subtitles run globally on top). */
const Cycler: React.FC<{srcs: {src: string; trim?: number}[]; from: number; dur: number}> = ({srcs, from, dur}) => {
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

/** ── Classic centered subtitles — words fade in one by one, synced to the VO ── */
const OUTLINE = '-2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000, 0 0 4px #000, 0 3px 8px rgba(0,0,0,0.95)';
const SUBS: [number, number, string][] = [
  [778.96, 781.0, 'Warum fährt die Bahn in Europa,'],
  [781.0, 782.9, 'Japan und China — aber nicht in den USA?'],
  [783.6, 784.9, 'Auf diese Frage gibt es'],
  [784.9, 785.96, 'nicht die eine Antwort.'],
  [786.28, 787.96, 'Es ist die Summe vieler Ursachen.'],
  [788.24, 789.68, 'Die erste ist die Geografie.'],
  [790.2, 791.5, 'Europa und Japan sind kompakt'],
  [791.5, 792.7, 'und dicht besiedelt —'],
  [792.7, 793.94, 'wie geschaffen für die Bahn.'],
  [794.6, 795.9, 'Amerika dagegen ist riesig'],
  [795.9, 796.96, 'und weit zersiedelt.'],
  [797.67, 798.96, 'Die zweite ist das Timing.'],
  [799.64, 800.9, 'Als das Auto aufkam,'],
  [800.9, 802.3, 'war es in den USA sofort'],
  [802.3, 803.9, 'für die breite Masse erschwinglich —'],
  [803.9, 805.0, 'und die Städte wurden'],
  [805.0, 806.96, 'ganz um das Auto herum gebaut.'],
  [807.56, 808.9, 'Europa besaß seine dichten Städte'],
  [808.9, 809.96, 'schon lange vorher.'],
  [810.91, 811.96, 'Die dritte ist das Geld.'],
  [812.66, 814.6, 'Über Jahrzehnte flossen Milliarden'],
  [814.6, 816.2, 'in Straßen und Flughäfen,'],
  [816.2, 818.4, 'während die Schiene fast leer ausging.'],
  [819.18, 820.6, 'Andere Länder verstanden ihre Bahn'],
  [820.6, 821.92, 'als öffentliche Aufgabe.'],
  [822.54, 824.96, 'In den USA sollte sie Gewinn abwerfen.'],
  [824.96, 826.96, 'Die vierte ist die Eigentumsfrage.'],
  [827.22, 829.2, 'Die Gleise gehören dem Güterverkehr —'],
  [829.2, 830.9, 'und der Personenzug bleibt'],
  [830.9, 832.96, 'der ungebetene Gast auf fremdem Grund.'],
  [833.04, 834.92, 'Und die fünfte ist der moderne Faktor.'],
  [835.36, 837.0, 'Wer es heute noch einmal versucht:'],
  [837.0, 838.5, 'teures Land,'],
  [838.5, 839.96, 'endlose Klagen,'],
  [840.26, 841.7, 'zersplitterte Zuständigkeit'],
  [841.7, 843.2, 'und Fördergelder, die nie'],
  [843.2, 844.96, 'lange genug fließen.'],
  [846.05, 847.0, 'Amerika hat seine Züge nicht'],
  [847.0, 847.96, 'durch einen Unfall verloren.'],
  [848.56, 850.1, 'Dahinter steht eine lange Kette'],
  [850.1, 851.6, 'von Entscheidungen, die meist'],
  [851.6, 853.2, 'bequem waren, kurzfristig logisch —'],
  [853.2, 854.4, 'und manchmal schlecht'],
  [854.4, 855.96, 'im Eigennutz dienten.'],
  [856.2, 857.6, 'Jeder einzelne davon war'],
  [857.6, 858.96, 'für sich genommen nachvollziehbar.'],
  [859.26, 860.8, 'Zusammen haben sie das beste'],
  [860.8, 861.96, 'Bahnnetz der Welt demontiert.'],
  [863.09, 864.96, 'Immerhin gibt es einen Hoffnungsschimmer.'],
  [865.08, 866.6, 'Private wie Brightline'],
  [866.6, 867.96, 'bauen neue Strecken.'],
  [868.16, 869.5, 'In den Nordost-Korridor'],
  [869.5, 870.7, 'fließt wieder Geld —'],
  [870.7, 871.96, 'das Umweltbewusstsein wächst.'],
  [872.54, 873.9, 'Doch 70 Jahre Rückstand'],
  [873.9, 875.3, 'und eine ganz aufs Auto'],
  [875.3, 876.5, 'ausgerichtete Gesellschaft'],
  [876.5, 877.96, 'kehrt man nicht über Nacht um.'],
  [878.62, 879.7, 'Der Weg zurück'],
  [879.7, 880.8, 'ist viel länger als der Weg'],
  [880.8, 881.96, 'nach unten es je war.'],
];
const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS + START;
  const cue = SUBS.find(([s, e]) => t >= s && t < e);
  if (!cue) return null;
  const [s, e, text] = cue;
  const words = text.split(' ');
  const span = (e - s) * 0.6;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 82, textAlign: 'center', padding: '0 240px'}}>
      <span style={{fontFamily: 'Inter, system-ui, sans-serif', fontWeight: 800, fontSize: 50, lineHeight: 1.22, color: YEL, textShadow: OUTLINE}}>
        {words.map((w, i) => {
          const wt = s + (i / words.length) * span;
          const o = interpolate(t, [wt, wt + 0.12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return <span key={i} style={{opacity: o}}>{w}{i < words.length - 1 ? ' ' : ''}</span>;
        })}
      </span>
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
  <div style={{position: 'absolute', left: 80, top: 60, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.2em', color: '#7df9ff', opacity: 0.85, textShadow: '0 2px 8px rgba(0,0,0,0.85)'}}>FAZIT — DIE SUMME VIELER URSACHEN</div>
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

type ShotDef = {at: number; src?: string; num?: string; bw?: boolean; trim?: number; cyc?: {src: string; trim?: number}[]};
const SHOTS: ShotDef[] = [
  {at: 6.1, src: 'clips/citynight.mp4'},
  // CAUSE 1 — geography
  {at: 10.74, src: 'clips/hknight.mp4', num: '01'},
  {at: 17.1, src: 'clips/air.mp4', bw: true},
  // CAUSE 2 — timing
  {at: 20.17, src: 'clips/carad.mp4', num: '02', bw: true},
  {at: 26.0, src: 'clips/carcity.mp4'},
  {at: 30.06, src: 'clips/brussels.mp4'},
  // CAUSE 3 — money
  {at: 33.41, src: 'clips/vegas.mp4', num: '03'},
  {at: 35.16, src: 'clips/highway.mp4'},
  {at: 38.0, src: 'clips/airport.mp4'},
  {at: 41.68, src: 'clips/shinkansen2.mp4'},
  {at: 45.04, src: 'clips/tokyo.mp4'},
  // CAUSE 4 — ownership
  {at: 47.46, src: 'clips/freight_us.mp4', num: '04', bw: true},
  {at: 50.46, src: 'clips/station_night.mp4'},
  // CAUSE 5 — the modern factor
  {at: 55.54, src: 'clips/shinkansen_new.mp4', num: '05'},
  {at: 57.86, src: 'clips/harvest.mp4', bw: true},
  {at: 60.26, src: 'clips/oldline.mp4', bw: true},
  {at: 62.66, src: 'clips/subway.mp4', bw: true},
  {at: 65.06, src: 'clips/usrail_station.mp4', bw: true},
  // synthesis
  {at: 68.55, src: 'clips/archive_train.mp4', bw: true},
  {at: 71.06, cyc: [{src: 'clips/tgv.mp4'}, {src: 'clips/china.mp4'}, {src: 'clips/acela1.mp4'}, {src: 'clips/ice.mp4'}]},
  {at: 78.7, src: 'clips/usrail_approach.mp4', bw: true},
  {at: 81.76, src: 'clips/usrail_mountain.mp4', bw: true},
  // hope
  {at: 85.59, src: 'clips/sunrise.mp4'},
  {at: 87.58, src: 'clips/brightline_run.mp4'},
  {at: 90.66, src: 'clips/acela3.mp4'},
  {at: 92.56, src: 'clips/wind.mp4'},
  // reality check
  {at: 95.04, src: 'clips/traffic.mp4'},
  // closer
  {at: 101.12, src: 'clips/platform_pass.mp4', bw: true},
];

export const FazitEv: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#05010f'}}>
      <CollageTitle from={0} dur={f(6.1)} />

      {/* Each shot runs until the next one starts — contiguous, no gaps. */}
      {SHOTS.map((sh, i) => {
        const from = f(sh.at);
        const end = i < SHOTS.length - 1 ? f(SHOTS[i + 1].at) : FAZIT_DURATION;
        const dur = end - from;
        return sh.cyc
          ? <Cycler key={i} srcs={sh.cyc} from={from} dur={dur} />
          : <Shot key={i} src={sh.src!} from={from} dur={dur} num={sh.num} bw={sh.bw} trim={sh.trim} />;
      })}

      <Tag />
      <Subtitles />

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
