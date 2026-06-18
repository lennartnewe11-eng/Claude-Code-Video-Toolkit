import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Typewriter, TapedPhoto, CornerMarks, DashedBox, Stamp, Highlight, RedNote, Crosshair} from './style/Evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 189.96;
export const C2P7_DURATION = Math.round(36.0 * FPS);
const f = (s: number) => Math.round(s * FPS);
const PAPER = 0.3, STAMP = 0.5, TYPE = 0.2, DRONE = 0.06;

const SWAP = f(18.6);

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

export const Ch2P7Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 02 — Die größte Subvention" x={110} y={70} size={26} at={f(0.2)} highlight />
      <Crosshair x={1850} y={70} at={f(0.8)} />

      {/* ── Phase A: Eisenhower / 1956 / Autobahn ── */}
      <Group show={[0, SWAP + 4]}>
        <Headline text="Die größte Subvention der Geschichte" x={110} y={150} size={58} at={f(0.7)} />

        <TapedPhoto src="eisenhower.jpg" cx={330} cy={560} w={360} rot={-3} at={f(4.2)} caption="Präsident D. D. Eisenhower" />
        <CornerMarks x={170} y={400} w={320} h={330} at={f(4.6)} />
        <RedNote text="1956" x={330} y={330} size={70} at={f(4.4)} rot={-5} />

        <DashedBox x={620} y={440} w={520} h={170} at={f(6.6)} />
        <TypeHeading text="Federal Aid" x={650} y={470} size={30} at={f(6.7)} />
        <TypeHeading text="Highway Act" x={650} y={515} size={30} at={f(6.9)} />
        <TypeHeading text="unterzeichnet 1956" x={650} y={565} size={22} at={f(7.3)} color="#5d574c" />

        <TapedPhoto src="autobahn.jpg" cx={1500} cy={560} w={520} rot={3} at={f(9.4)} caption="Vorbild: deutsche Autobahn, 1936" />
        <Stamp text="auch: Truppen verlegen" x={900} y={760} size={34} at={f(14.8)} rot={-4} />
      </Group>

      {/* ── Phase B: the Interstate result + nothing for rail ── */}
      <Group show={[SWAP, C2P7_DURATION]}>
        <TapedPhoto src="interchange.jpg" cx={1330} cy={470} w={1000} rot={-1} at={f(19.2)} caption="Interstate Highway System" />
        <Headline text="Das größte öffentliche Bauprojekt der USA" x={110} y={250} size={50} at={f(22.5)} />
        <TypeHeading text="Zehntausende Kilometer Autobahn" x={115} y={360} size={26} at={f(26.4)} />
        <Highlight x={110} y={470} w={520} at={f(26.8)} h={70} />
        <Headline text="~90% vom Staat" x={120} y={430} size={92} at={f(26.7)} />

        <TypeHeading text="Für die Bahn:" x={120} y={720} size={36} at={f(33.0)} />
        <Stamp text="Null" x={420} y={830} size={120} at={f(35.0)} rot={-7} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P7_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(0.7)} volume={STAMP} />
      <Sfx src="sfx_paper.mp3" at={f(4.2)} volume={PAPER} />
      <TypeClicks at={f(6.7)} n={8} gap={5} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(9.4)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(14.8)} volume={0.4} />
      <Sfx src="sfx_paper.mp3" at={f(19.2)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(26.7)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(35.0)} volume={0.6} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
