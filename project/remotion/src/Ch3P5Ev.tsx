import {AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, Dossier, Stamp, Highlight, RedNote, FileTag, Seal, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 357.463;
export const C3P5_DURATION = Math.round(24.9 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** A small strip of tape (collage detail). */
const Tape: React.FC<{x: number; y: number; w?: number; rot?: number}> = ({x, y, w = 120, rot = -4}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: 30, background: EV.tape, transform: `rotate(${rot}deg)`, boxShadow: '0 1px 2px rgba(0,0,0,0.12)'}} />
);

/** A handwritten-style marginalia scrap. */
const Scrap: React.FC<{text: string; x: number; y: number; at?: number; rot?: number; w?: number}> = ({text, x, y, at = 0, rot = -2, w = 280}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, opacity: o, transform: `rotate(${rot}deg)`, background: '#fbf8ef', padding: '10px 14px', boxShadow: '3px 5px 9px rgba(20,16,10,0.28)', fontFamily: mono, fontSize: 19, color: EV.ink, lineHeight: 1.3}}>
      <Tape x={w / 2 - 40} y={-14} w={80} rot={3} />
      {text}
    </div>
  );
};

/** A rotating cog (engineering motif). */
const Gear: React.FC<{x: number; y: number; r: number; teeth?: number; at?: number; speed?: number; color?: string}> = ({
  x, y, r, teeth = 12, at = 0, speed = 1.4, color = EV.ink,
}) => {
  const frame = useCurrentFrame();
  const rot = (frame - at) * speed;
  const o = interpolate(frame - at, [0, 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tw = r * 0.28, th = r * 0.34;
  return (
    <svg style={{position: 'absolute', left: x - r * 1.6, top: y - r * 1.6, opacity: o}} width={r * 3.2} height={r * 3.2}>
      <g transform={`translate(${r * 1.6} ${r * 1.6}) rotate(${rot})`}>
        {Array.from({length: teeth}).map((_, i) => {
          const a = (i / teeth) * 360;
          return <rect key={i} x={-tw / 2} y={-r - th} width={tw} height={th} fill={color} transform={`rotate(${a})`} rx={2} />;
        })}
        <circle r={r} fill={color} />
        <circle r={r * 0.42} fill={EV.paper} />
      </g>
    </svg>
  );
};

/** Concentric sound waves blasting to the right (engine noise). */
const SoundWaves: React.FC<{x: number; y: number; at?: number; color?: string}> = ({x, y, at = 0, color = EV.red}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <svg style={{position: 'absolute', left: x, top: y - 130, opacity: o}} width={260} height={260}>
      {[0, 1, 2, 3].map((i) => {
        const t = (((frame - at) / 24) + i / 4) % 1;
        const rr = 18 + t * 120;
        const op = (1 - t) * 0.85;
        return <path key={i} d={`M ${rr * 0.5} ${130 - rr * 0.86} A ${rr} ${rr} 0 0 1 ${rr * 0.5} ${130 + rr * 0.86}`} fill="none" stroke={color} strokeWidth={5} opacity={op} />;
      })}
    </svg>
  );
};

/** A mountain of stacked dollar bills that builds up from the ground. */
const MoneyMountain: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const cols = [3, 6, 10, 15, 21, 15, 10, 6, 3];
  const colW = 92, billW = 140, billH = Math.round((billW * 390) / 905), layer = 11, H = 340;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: cols.length * colW + billW, height: H}}>
      {cols.map((maxN, ci) =>
        Array.from({length: maxN}).map((_, j) => {
          const appear = from + ci * 1.4 + j * 1.1;
          const o = interpolate(frame - appear, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const ty = interpolate(frame - appear, [0, 6], [18, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const jitter = ((ci * 7 + j * 13) % 5) - 2;
          const rot = (((ci * 3 + j) % 3) - 1) * 1.4;
          return (
            <div key={`${ci}-${j}`} style={{position: 'absolute', left: ci * colW + jitter, top: H - billH - j * layer + ty, width: billW, height: billH, opacity: o, backgroundImage: `url(${staticFile('photos/bill.jpg')})`, backgroundSize: 'cover', transform: `rotate(${rot}deg)`, boxShadow: '0 1px 2px rgba(0,0,0,0.35)', outline: '1px solid rgba(0,0,0,0.12)', filter: 'grayscale(1) contrast(1.06) brightness(1.02)'}} />
          );
        })
      )}
    </div>
  );
};

export const Ch3P5Ev: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />
      {/* red accent block (collage) */}
      <div style={{position: 'absolute', left: 0, top: 0, width: 150, height: 360, background: EV.red, opacity: 0.14, transform: 'skewX(-8deg) translateX(-60px)'}} />

      {/* persistent header */}
      <FileTag text="3·c" x={150} y={92} at={f(0.4)} size={62} />
      <TypeHeading text="Akte — Spielerei oder Strategie?" x={210} y={78} size={26} at={f(0.2)} />
      <Crosshair x={1500} y={70} at={f(0.8)} />
      <Seal text={'BEFUND\nKEIN\nKONZEPT'} x={1810} y={120} at={f(2.0)} size={150} rot={-10} />

      {/* ── Board A: it was never a serious concept ── */}
      <Group show={[0, f(8.9)]}>
        <Headline text="Reine Spielerei" x={120} y={210} size={84} at={f(0.6)} />

        <TapedPhoto src="m497run.jpg" cx={520} cy={650} w={520} rot={-2} at={f(1.2)} caption="M-497 — der Düsen-Stunt" />
        <Stamp text="kein ernsthaftes Konzept" x={560} y={560} size={40} at={f(1.8)} rot={-7} />
        <RedNote text="1966" x={250} y={420} size={48} at={f(1.4)} rot={-6} />

        {/* the roaring engines / commuters absurdity */}
        <Headline text="Brüllende Triebwerke" x={1080} y={330} size={58} at={f(3.4)} />
        <SoundWaves x={1560} y={520} at={f(3.8)} />
        <SoundWaves x={1640} y={520} at={f(4.0)} />
        <Dossier x={1080} y={470} w={520} at={f(4.2)} title="Realitätscheck"
          rows={[
            {label: 'Lärm', value: 'ohrenbetäubend', hl: true},
            {label: 'Pendler dahinter?', value: 'niemals'},
            {label: 'Alltagstauglich', value: 'nein', hl: true},
          ]} />
        <Scrap text="Niemand fährt freiwillig hinter einem Triebwerk." x={1180} y={760} at={f(5.6)} rot={2} w={420} />
      </Group>

      {/* ── Board B: the mindset & the flawed equation ── */}
      <Group show={[f(8.4), f(20.0)]}>
        <Highlight x={120} y={290} w={1060} at={f(9.0)} h={48} />
        <Headline text="Die amerikanische Denkweise" x={120} y={200} size={78} at={f(8.8)} />
        <TypeHeading text="Was der Stunt über diese Jahre verrät" x={125} y={300} size={26} at={f(9.6)} color="#5d574c" />

        {/* the flawed equation: speed = engineering problem */}
        <div style={{position: 'absolute', left: 150, top: 520, fontFamily: cond, fontWeight: 700, fontSize: 96, color: EV.ink, textTransform: 'uppercase', opacity: interpolate(frame, [f(13.0), f(13.6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>Geschwindigkeit</div>
        <div style={{position: 'absolute', left: 970, top: 510, fontFamily: cond, fontWeight: 700, fontSize: 110, color: EV.ink, opacity: interpolate(frame, [f(13.4), f(14.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>=</div>
        <Gear x={1230} y={595} r={70} at={f(13.6)} speed={1.6} />
        <Gear x={1340} y={680} r={48} at={f(13.9)} speed={-2.2} color={EV.inkSoft} />
        <div style={{position: 'absolute', left: 1430, top: 540, fontFamily: cond, fontWeight: 700, fontSize: 72, color: EV.ink, textTransform: 'uppercase', lineHeight: 0.95, opacity: interpolate(frame, [f(13.8), f(14.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>Ingenieurs-<br />problem</div>

        <Scrap text="Mehr Erfindergeist → Problem gelöst. So die Annahme." x={170} y={690} at={f(16.2)} rot={-2} w={520} />
        <RedNote text="ein technisches Spielzeug" x={560} y={870} size={40} at={f(17.0)} rot={-3} />
      </Group>

      {/* ── Board C: the costly error ── */}
      <Group show={[f(19.5), C3P5_DURATION]}>
        <Highlight x={120} y={210} w={780} at={f(20.4)} h={48} />
        <Headline text="Ein teurer Irrtum" x={120} y={150} size={92} at={f(20.0)} />

        <MoneyMountain x={560} y={560} from={f(21.0)} />
        <Img src={staticFile('cutouts/coin.png')} style={{position: 'absolute', left: 520, top: 850, width: 120, opacity: interpolate(frame, [f(22.0), f(22.6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
        <Img src={staticFile('cutouts/coin.png')} style={{position: 'absolute', left: 1430, top: 858, width: 96, opacity: interpolate(frame, [f(22.4), f(23.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />

        {/* rising-cost arrow + label */}
        <div style={{position: 'absolute', left: 1010, top: 360, fontFamily: cond, fontWeight: 700, fontSize: 130, color: EV.red, opacity: interpolate(frame, [f(22.2), f(22.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>↑</div>
        <RedNote text="Milliarden $" x={1180} y={430} size={56} at={f(22.6)} rot={-6} />
        <TypeHeading text="…kostete das Land teuer" x={150} y={300} size={32} at={f(22.4)} highlight />
        <Stamp text="teuer bezahlt" x={400} y={470} size={56} at={f(23.4)} rot={-7} />
        <Scrap text="Geld + Jahre + Glaubwürdigkeit" x={150} y={560} at={f(23.8)} rot={-2} w={360} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P5_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(1.2)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(1.8)} volume={STAMP} />
      <TypeClicks at={f(4.2)} n={6} gap={5} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(5.6)} volume={PAPER} />
      <TypeClicks at={f(13.0)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(16.2)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(21.0)} volume={0.22} />
      <Sfx src="sfx_paper.mp3" at={f(21.8)} volume={0.22} />
      <Sfx src="sfx_stamp.mp3" at={f(23.4)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
