import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, TapedPhoto, Highlight, RedNote, Crosshair} from './style/Evidence';
import {cond, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 129.96;
export const C2P3_DURATION = Math.round(6.4 * FPS);
const f = (s: number) => Math.round(s * FPS);
const PAPER = 0.3, STAMP = 0.5, TYPE = 0.2, DRONE = 0.06;

/** Big price drop $850 -> $260, counting down with a red arrow. */
const PriceDrop: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  const v = Math.round(interpolate(frame - at, [0, 36], [850, 260], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const o = interpolate(frame - at, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 600, top: 740, opacity: o, display: 'flex', alignItems: 'center', gap: 24}}>
      <span style={{fontFamily: cond, fontWeight: 700, fontSize: 150, color: EV.ink}}>${v}</span>
      <span style={{fontFamily: cond, fontWeight: 700, fontSize: 90, color: EV.red}}>▼</span>
    </div>
  );
};

export const Ch2P3Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 02 — Der Herausforderer" x={110} y={70} size={26} at={f(0.2)} />
      <TypeHeading text="Die Revolution" x={110} y={124} size={22} at={f(0.5)} highlight />
      <Crosshair x={1850} y={70} at={f(0.8)} />

      {/* the assembly line */}
      <TapedPhoto src="assembly.jpg" cx={1300} cy={430} w={900} rot={-1} at={f(0.5)} caption="Highland Park, 1913" />

      {/* the word */}
      <Highlight x={150} y={320} w={520} at={f(2.3)} h={30} />
      <Headline text="Das Fließband" x={150} y={300} size={92} at={f(2.2)} />
      <TypeHeading text="Montagezeit: 12 h → 93 min" x={155} y={420} size={24} at={f(2.7)} />

      {/* price collapses */}
      <TypeHeading text="Massenproduktion drückt den Preis —" x={155} y={690} size={26} at={f(4.0)} />
      <PriceDrop at={f(4.3)} />

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P3_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(0.5)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(2.2)} volume={STAMP} />
      <TypeClicks at={f(2.7)} n={6} gap={5} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(4.3)} volume={0.4} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
