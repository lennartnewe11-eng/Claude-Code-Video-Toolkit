import {AbsoluteFill, Audio, staticFile} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, TapedPhoto, BodyBlock, MapPlate, RouteLine, XMark, CircleLabel, Crosshair, Highlight} from './style/Evidence';

const START = 36.22;
export const P1EV_DURATION = Math.round(13.4 * FPS);
const f = (s: number) => Math.round(s * FPS);

/**
 * Chapter 1 · Part 1 — evidence-board collage (slower, detail-rich).
 * The board assembles as the narration runs: antique 1867 US map, the drawn
 * transcontinental route (1869), taped period photos, typewriter case notes.
 */
export const Ch1P1Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />

      {/* case-file header */}
      <TypeHeading text="Akte 01 — Das goldene Zeitalter" x={110} y={80} size={32} at={f(0.2)} highlight />
      <TypeHeading text="U.S.A · 1830 – 1916" x={110} y={140} size={22} at={f(0.9)} color="#5d574c" />
      <Crosshair x={1850} y={60} at={f(2.4)} />
      <Crosshair x={70} y={980} at={f(3.0)} />

      {/* the antique map, centre-right */}
      <MapPlate cx={1230} cy={470} w={880} at={f(1.2)} rot={-1} />

      {/* taped photo of the Jupiter locomotive, left */}
      <TapedPhoto src="jupiter.jpg" cx={320} cy={420} w={360} rot={-3} at={f(3.0)} caption="»Jupiter«, Mai 1869" />

      {/* drawn transcontinental route on the map */}
      <RouteLine points={[[1300, 470], [1120, 455], [950, 480]]} at={f(4.2)} drawFrames={34} />
      <XMark x={1300} y={470} at={f(5.0)} />
      <XMark x={950} y={480} at={f(5.4)} />
      <CircleLabel text="1869" x={1120} y={360} at={f(5.6)} />
      <TypeHeading text="Erste transkontinentale Linie" x={980} y={250} size={18} at={f(5.0)} color="#5d574c" />

      {/* arrow connecting the route to the locomotive photo */}
      <RouteLine points={[[930, 490], [700, 450], [510, 430]]} at={f(6.0)} drawFrames={22} />

      {/* case notes */}
      <BodyBlock
        x={110} y={700} w={460} at={f(6.2)} size={20}
        lines={[
          '1869 wird in Promontory, Utah, die',
          'erste transkontinentale Eisenbahn',
          'vollendet. Was Siedler einst Monate',
          'kostete, ist nun in Tagen durchquerbar.',
        ]}
      />

      {/* second taped photo, right — the railroad world */}
      <TapedPhoto src="pullman.jpg" cx={1660} cy={780} w={360} rot={4} at={f(7.6)} caption="Pullman-Wagen" />
      <RouteLine points={[[1500, 690], [1590, 720]]} at={f(8.0)} drawFrames={16} arrow={false} />

      {/* the line: not just any means of transport */}
      <Highlight x={600} y={918} w={760} at={f(9.6)} h={26} />
      <Headline text="Nicht irgendein Verkehrsmittel" x={600} y={905} size={78} at={f(9.7)} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
