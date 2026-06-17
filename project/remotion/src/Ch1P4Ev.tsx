import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, BodyBlock, RouteLine, Circle, FullScreenVideo, Stamp, RedNote, Crosshair, Highlight} from './style/Evidence';
import {Cutout} from './style/Cutout';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 74.48;
export const P4EV_DURATION = Math.round(13.4 * FPS);
const f = (s: number) => Math.round(s * FPS);

const PAPER = 0.3, DRAW = 0.3, STAMP = 0.5, TYPE = 0.22, DRONE = 0.06;

const VIDEO_AT = f(6.4), VIDEO_LEN = 80;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/**
 * Chapter 1 · Part 4 (74.48–87.88) — the railroad empires.
 * A conspiracy-board of the rail barons ("the tech giants of the 19th c.") ->
 * a full-screen 1896 archival insert -> the colossal 254,000-mile network.
 */
export const Ch1P4Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 01 — Das goldene Zeitalter" x={110} y={78} size={26} at={f(0.2)} />
      <TypeHeading text="Die Eisenbahn-Imperien" x={110} y={132} size={22} at={f(0.8)} highlight />
      <Crosshair x={1850} y={70} at={f(1.6)} />

      {/* ── Phase 1 · the barons ── */}
      <Group show={[0, VIDEO_AT + 4]}>
        <Cutout src="vanderbilt.png" cx={470} cy={660} width={300} entrance="pop" delay={f(0.6)} rot={-2} />
        <Cutout src="gould.png" cx={880} cy={690} width={300} entrance="pop" delay={f(1.2)} rot={2} />
        <Cutout src="stanford.png" cx={1270} cy={660} width={280} entrance="pop" delay={f(1.8)} rot={-2} />
        <Circle x={470} y={600} rx={120} ry={150} at={f(1.4)} />
        <Circle x={880} y={630} rx={120} ry={150} at={f(2.0)} rot={4} />
        <Circle x={1270} y={600} rx={115} ry={150} at={f(2.6)} />
        <TypeHeading text="Vanderbilt" x={400} y={820} size={20} at={f(1.6)} />
        <TypeHeading text="Gould" x={835} y={850} size={20} at={f(2.2)} />
        <TypeHeading text="Stanford" x={1205} y={820} size={20} at={f(2.8)} />
        <RouteLine points={[[600, 620], [740, 650]]} at={f(3.0)} drawFrames={14} arrow={false} width={3} />
        <RouteLine points={[[1010, 660], [1140, 640]]} at={f(3.3)} drawFrames={14} arrow={false} width={3} />
        <Headline text="Die Tech-Giganten" x={560} y={240} size={92} at={f(3.9)} />
        <TypeHeading text="des 19. Jahrhunderts" x={566} y={330} size={26} at={f(4.6)} />
        <Stamp text="Monopol" x={1480} y={350} size={48} at={f(5.2)} rot={8} />
      </Group>

      {/* ── Phase 2 · full-screen archival insert ── */}
      <Sequence from={VIDEO_AT} durationInFrames={VIDEO_LEN} layout="none">
        <FullScreenVideo src="archive_train.mp4" caption="Bahnhof, um 1896" stamp="Höhepunkt" durationFrames={VIDEO_LEN} />
      </Sequence>

      {/* ── Phase 3 · the colossal network ── */}
      <Group show={[VIDEO_AT + VIDEO_LEN - 6, P4EV_DURATION]}>
        <TypeHeading text="Auf dem Höhepunkt · um 1916" x={600} y={250} size={28} at={f(9.2)} highlight />
        <Headline text="254.000 Meilen" x={520} y={460} size={170} at={f(9.9)} />
        <TypeHeading text="Schienennetz der U.S.A." x={600} y={690} size={30} at={f(10.6)} />
        <BodyBlock
          x={600} y={760} w={760} at={f(10.9)} size={20}
          lines={[
            'Genug Gleis, um die Erde zehnmal zu',
            'umrunden — gebaut in wenigen Jahrzehnten.',
          ]}
        />
        <Crosshair x={1780} y={300} at={f(10.0)} />
      </Group>

      {/* ── sound (quiet) ── */}
      <DroneBed durationInFrames={P4EV_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(0.6)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(1.2)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(1.8)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(1.4)} volume={DRAW} />
      <Sfx src="sfx_draw.mp3" at={f(2.0)} volume={DRAW} />
      <Sfx src="sfx_draw.mp3" at={f(2.6)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(3.9)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(5.2)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(9.9)} volume={STAMP} />
      <TypeClicks at={f(10.9)} n={5} gap={5} volume={TYPE} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
