import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, Dossier, Stamp, Highlight, BigX, FileTag, Seal, Crosshair} from './style/Evidence';
import {cond, EV} from './style/evidence';
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

export const Ch3P5Ev: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />

      {/* persistent header */}
      <FileTag text="3·c" x={150} y={92} at={f(0.4)} size={62} />
      <TypeHeading text="Akte — Spielerei oder Strategie?" x={210} y={78} size={26} at={f(0.2)} />
      <Crosshair x={1500} y={70} at={f(0.8)} />
      <Seal text={'BEFUND\nKEIN\nKONZEPT'} x={1810} y={120} at={f(2.0)} size={150} rot={-10} />

      {/* ── Board A: it was never a serious concept ── */}
      <Group show={[0, f(8.9)]}>
        <Headline text="Reine Spielerei" x={120} y={210} size={84} at={f(0.6)} />

        <TapedPhoto src="m497run.jpg" cx={520} cy={640} w={520} rot={-2} at={f(1.2)} caption="M-497 — der Düsen-Stunt" />
        <Stamp text="kein ernsthaftes Konzept" x={560} y={560} size={40} at={f(1.8)} rot={-7} />

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
      </Group>

      {/* ── Board B: the mindset & the error ── */}
      <Group show={[f(8.4), C3P5_DURATION]}>
        <Highlight x={120} y={290} w={1060} at={f(9.0)} h={48} />
        <Headline text="Die amerikanische Denkweise" x={120} y={200} size={78} at={f(8.8)} />
        <TypeHeading text="Was der Stunt über diese Jahre verrät" x={125} y={300} size={26} at={f(9.6)} color="#5d574c" />

        {/* the flawed equation: speed = engineering problem */}
        <div style={{position: 'absolute', left: 150, top: 520, fontFamily: cond, fontWeight: 700, fontSize: 96, color: EV.ink, textTransform: 'uppercase', opacity: interpolate(frame, [f(13.0), f(13.6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>Geschwindigkeit</div>
        <div style={{position: 'absolute', left: 970, top: 510, fontFamily: cond, fontWeight: 700, fontSize: 110, color: EV.ink, opacity: interpolate(frame, [f(13.4), f(14.0)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>=</div>
        <Gear x={1230} y={595} r={70} at={f(13.6)} speed={1.6} />
        <Gear x={1340} y={680} r={48} at={f(13.9)} speed={-2.2} color={EV.inkSoft} />
        <div style={{position: 'absolute', left: 1430, top: 540, fontFamily: cond, fontWeight: 700, fontSize: 72, color: EV.ink, textTransform: 'uppercase', lineHeight: 0.95, opacity: interpolate(frame, [f(13.8), f(14.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>Ingenieurs-<br />problem</div>

        <TypeHeading text="ein technisches Spielzeug — einfach zu lösen" x={150} y={700} size={28} at={f(16.2)} />

        {/* the turn: this was an error */}
        <BigX x={955} y={505} w={130} h={130} at={f(21.0)} />
        <Stamp text="Irrtum" x={780} y={600} size={150} at={f(20.9)} rot={-9} />
        <TypeHeading text="…und dieser Irrtum kostete das Land teuer" x={150} y={840} size={30} at={f(22.4)} highlight />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P5_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(1.2)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(1.8)} volume={STAMP} />
      <TypeClicks at={f(4.2)} n={6} gap={5} volume={TYPE} />
      <TypeClicks at={f(13.0)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(20.9)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(21.0)} volume={0.4} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
