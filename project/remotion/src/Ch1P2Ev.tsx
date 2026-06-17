import {AbsoluteFill, Audio, staticFile} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, TapedPhoto, BodyBlock, RouteLine, Crosshair, Highlight, Stamp, RedNote, CircleLabel} from './style/Evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 49.73;
export const P2EV_DURATION = Math.round(13.35 * FPS);
const f = (s: number) => Math.round(s * FPS);

/**
 * Chapter 1 · Part 2 (49.73–63.08) — evidence board.
 * "It was THE means of transport" -> the continent shrinks: months by wagon
 * vs. days by rail. Centerpiece is a before/after comparison of two taped
 * photos joined by a red marker arrow.
 */
export const Ch1P2Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />

      <TypeHeading text="Akte 01 — Das goldene Zeitalter" x={110} y={78} size={26} at={f(0.2)} />
      <TypeHeading text="Der Kontinent schrumpft" x={110} y={132} size={22} at={f(0.8)} highlight />
      <Crosshair x={1850} y={70} at={f(2.0)} />

      {/* payoff stamp: "the" means of transport */}
      <Stamp text="Das Verkehrsmittel" x={960} y={235} size={66} at={f(0.3)} rot={-5} />

      {/* construction-era evidence photo, top-right */}
      <TapedPhoto src="workers.jpg" cx={1560} cy={250} w={300} rot={5} at={f(3.0)} caption="Erbauer der Strecke" />

      {/* ── before: wagon (months) ── */}
      <TapedPhoto src="wagontrain.jpg" cx={470} cy={620} w={470} rot={-3} at={f(2.8)} caption="Siedler im Planwagen" />
      <RedNote text="MONATE" x={470} y={370} size={70} at={f(3.4)} rot={-4} />

      {/* ── after: rail (days) ── */}
      <TapedPhoto src="passengertrain.jpg" cx={1450} cy={640} w={520} rot={3} at={f(4.6)} caption="Transkontinentale Bahn, 1869" />
      <RedNote text="TAGE" x={1450} y={380} size={70} at={f(5.2)} rot={3} />

      {/* red arrow: months -> days */}
      <RouteLine points={[[720, 600], [960, 560], [1180, 600]]} at={f(6.0)} drawFrames={26} />
      <RedNote text="≈ 6 Monate → 7 Tage" x={960} y={500} size={48} at={f(6.6)} rot={-2} />

      {/* case notes */}
      <BodyBlock
        x={700} y={720} w={520} at={f(7.4)} size={19}
        lines={[
          'Wofür ein Siedlertreck Monate auf',
          'gefährlichen Trails brauchte, genügen',
          'nun wenige Tage im Zug. Ein ganzer',
          'Kontinent rückt zusammen.',
        ]}
      />

      {/* the line */}
      <Highlight x={620} y={918} w={700} at={f(9.6)} h={26} />
      <Headline text="Monate wurden zu Tagen" x={620} y={905} size={78} at={f(9.7)} />

      {/* ── sound design, synced to the animations ── */}
      <DroneBed durationInFrames={P2EV_DURATION} />
      <TypeClicks at={f(0.2)} n={5} gap={4} />
      <Sfx src="sfx_stamp.mp3" at={f(0.3)} volume={0.75} />
      <Sfx src="sfx_paper.mp3" at={f(2.8)} volume={0.5} />
      <Sfx src="sfx_paper.mp3" at={f(3.0)} volume={0.4} />
      <Sfx src="sfx_draw.mp3" at={f(3.4)} volume={0.5} />
      <Sfx src="sfx_paper.mp3" at={f(4.6)} volume={0.5} />
      <Sfx src="sfx_draw.mp3" at={f(5.2)} volume={0.5} />
      <Sfx src="sfx_draw.mp3" at={f(6.0)} volume={0.6} />
      <Sfx src="sfx_draw.mp3" at={f(6.6)} volume={0.5} />
      <TypeClicks at={f(7.4)} n={6} gap={5} />
      <Sfx src="sfx_stamp.mp3" at={f(9.7)} volume={0.7} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
