import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, TapedPhoto, RouteLine, Circle, FullScreenVideo, Stamp, RedNote, Crosshair, Redaction} from './style/Evidence';
import {Cutout} from './style/Cutout';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 74.48;
export const P4EV_DURATION = Math.round(13.4 * FPS);
const f = (s: number) => Math.round(s * FPS);

const PAPER = 0.3, DRAW = 0.3, STAMP = 0.5, TYPE = 0.22, DRONE = 0.06;
const VIDEO_AT = f(7.3);
const VIDEO_LEN = P4EV_DURATION - VIDEO_AT;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/**
 * Chapter 1 · Part 4 (74.48–87.88) — the railroad empires.
 * A dense baron "conspiracy board" (portraits, bond, stock certificate, net
 * worth, red string) contrasted with a modern Silicon-Valley HQ (Apple Park):
 * the tech giants then & now. Then a long full-screen 1896 archival insert.
 */
export const Ch1P4Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 01 — Das goldene Zeitalter" x={110} y={70} size={26} at={f(0.2)} />
      <TypeHeading text="Die Eisenbahn-Imperien" x={110} y={124} size={22} at={f(0.8)} highlight />

      {/* ── Phase 1 · dense baron board + Silicon Valley contrast ── */}
      <Group show={[0, VIDEO_AT + 4]}>
        {/* financial documents pinned behind */}
        <TapedPhoto src="bond.jpg" cx={640} cy={330} w={440} rot={-4} at={f(1.0)} caption="Gold Bond, 1867" />
        <TapedPhoto src="stock.jpg" cx={300} cy={360} w={300} rot={6} at={f(2.4)} caption="Aktie, 1887" />

        {/* the barons */}
        <Cutout src="vanderbilt.png" cx={360} cy={720} width={270} entrance="pop" delay={f(0.6)} rot={-2} />
        <Cutout src="gould.png" cx={680} cy={750} width={270} entrance="pop" delay={f(1.2)} rot={2} />
        <Cutout src="stanford.png" cx={1000} cy={720} width={250} entrance="pop" delay={f(1.8)} rot={-2} />
        <Circle x={360} y={665} rx={108} ry={138} at={f(1.4)} />
        <Circle x={680} y={695} rx={108} ry={138} at={f(2.0)} rot={4} />
        <Circle x={1000} y={665} rx={100} ry={135} at={f(2.6)} />
        <TypeHeading text="Vanderbilt" x={300} y={865} size={19} at={f(1.6)} />
        <TypeHeading text="Gould" x={648} y={892} size={19} at={f(2.2)} />
        <TypeHeading text="Stanford" x={948} y={865} size={19} at={f(2.8)} />
        <RedNote text="$105 Mio." x={360} y={560} size={30} at={f(2.0)} rot={-4} />
        <RedNote text="Wall St." x={680} y={590} size={28} at={f(2.6)} rot={3} />
        <RouteLine points={[[470, 690], [600, 720]]} at={f(3.0)} drawFrames={12} arrow={false} width={3} />
        <RouteLine points={[[810, 720], [920, 700]]} at={f(3.3)} drawFrames={12} arrow={false} width={3} />
        <Redaction x={300} y={760} w={150} at={f(3.4)} h={16} />

        <Headline text="Die Tech-Giganten" x={120} y={190} size={70} at={f(0.7)} />

        {/* Silicon Valley contrast — colour, longer on screen */}
        <Stamp text="Damals = Heute" x={1480} y={210} size={42} at={f(3.6)} rot={6} />
        <TapedPhoto src="applepark.jpg" cx={1500} cy={620} w={760} rot={2} at={f(3.9)} caption="Apple Park, Cupertino — 2017" gray={false} />
        <RouteLine points={[[1120, 700], [1220, 640]]} at={f(5.0)} drawFrames={18} />
        <RedNote text="Die Big-Tech ihrer Zeit" x={1500} y={300} size={34} at={f(5.4)} rot={-3} />
        <Crosshair x={1850} y={70} at={f(1.0)} />
      </Group>

      {/* ── Phase 2 · long full-screen archival insert ── */}
      <Sequence from={VIDEO_AT} durationInFrames={VIDEO_LEN} layout="none">
        <FullScreenVideo src="archive_train.mp4" caption="Bahnhof, um 1896" stamp="Das Imperium" durationFrames={VIDEO_LEN} />
      </Sequence>

      {/* ── sound (quiet) ── */}
      <DroneBed durationInFrames={P4EV_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(1.0)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(0.6)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(1.2)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(1.8)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(2.4)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(1.4)} volume={DRAW} />
      <Sfx src="sfx_draw.mp3" at={f(2.0)} volume={DRAW} />
      <Sfx src="sfx_draw.mp3" at={f(2.6)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(3.6)} volume={STAMP} />
      <Sfx src="sfx_paper.mp3" at={f(3.9)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(5.0)} volume={DRAW} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
