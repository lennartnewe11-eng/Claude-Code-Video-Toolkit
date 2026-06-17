import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, TapedPhoto, RouteLine, Circle, RedNote, Crosshair, Highlight, MapDot} from './style/Evidence';
import {CompareBars} from './style/DataViz';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 87.88;
export const P5EV_DURATION = Math.round(16.0 * FPS);
const f = (s: number) => Math.round(s * FPS);

const PAPER = 0.3, DRAW = 0.3, STAMP = 0.5, TYPE = 0.22, DRONE = 0.06;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const TOWNS = ['Galesburg', 'Cheyenne', 'Topeka', 'Sedalia', 'Laramie', 'Winslow', 'Truckee', 'Ogden'];

/**
 * Chapter 1 · Part 5 (87.88–103.9). Bigger than all of Europe -> a station in
 * every small town -> the LUXURY of rail travel (Pullman palace sleeper,
 * dining car with waiters, observation car), shown large with callouts.
 */
export const Ch1P5Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 01 — Das goldene Zeitalter" x={110} y={70} size={26} at={f(0.2)} />
      <Crosshair x={1850} y={70} at={f(1.0)} />

      {/* ── A · more than all of Europe ── */}
      <Group show={[0, f(4.9)]}>
        <TypeHeading text="Größer als ein Kontinent" x={110} y={124} size={22} at={f(0.6)} highlight />
        <CompareBars cx={920} cy={520} width={1000} a={{label: 'USA', frac: 1.0}} b={{label: 'Europa', frac: 0.6}} delay={f(0.8)} />
        <RedNote text="Mehr als GANZ Europa" x={960} y={300} size={56} at={f(1.6)} rot={-2} />
      </Group>

      {/* ── B · a station in every town ── */}
      <Group show={[f(4.6), f(7.7)]}>
        <Headline text="Jede Kleinstadt — ein Bahnhof" x={300} y={250} size={70} at={f(4.8)} />
        {TOWNS.map((t, i) => (
          <MapDot key={t} x={300 + (i % 4) * 360} y={520 + Math.floor(i / 4) * 150} label={t} at={f(5.1 + i * 0.18)} below={i % 2 === 0} />
        ))}
      </Group>

      {/* ── C · LUXURY (the focus) ── */}
      <Group show={[f(7.4), P5EV_DURATION]}>
        <TypeHeading text="An Bord · Erste Klasse" x={110} y={124} size={22} at={f(7.6)} highlight />
        <Headline text="Reisen wie im Grand Hotel" x={110} y={185} size={62} at={f(7.8)} />

        {/* Pullman palace sleeper — large hero */}
        <TapedPhoto src="lux_sleeper.jpg" cx={560} cy={620} w={720} rot={-2} at={f(9.0)} caption="Pullman-Schlafwagen · Palace Car" />
        <Circle x={560} y={420} rx={90} ry={70} at={f(9.8)} />
        <RedNote text="Kristalllüster" x={300} y={330} size={32} at={f(10.0)} rot={-4} />
        <RedNote text="Mahagoni · Samt" x={820} y={905} size={30} at={f(10.3)} rot={3} />

        {/* dining car with waiters */}
        <TapedPhoto src="lux_dining.jpg" cx={1420} cy={520} w={640} rot={3} at={f(11.0)} caption="Speisewagen · mit Kellnern" />
        <Circle x={1430} y={470} rx={70} ry={90} at={f(11.8)} rot={6} />
        <RedNote text="Kellner in Livree" x={1640} y={330} size={30} at={f(12.0)} rot={4} />

        {/* observation car */}
        <TapedPhoto src="lux_parlor.jpg" cx={1380} cy={840} w={480} rot={-3} at={f(12.7)} caption="Aussichts- & Salonwagen" gray={false} />
        <RedNote text="Frischblumen an Bord" x={1080} y={880} size={26} at={f(13.2)} rot={-2} />
      </Group>

      {/* ── sound (quiet) ── */}
      <DroneBed durationInFrames={P5EV_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(1.6)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(4.8)} volume={STAMP} />
      {TOWNS.map((t, i) => <Sfx key={t} src="sfx_draw.mp3" at={f(5.1 + i * 0.18)} volume={0.18} dur={14} />)}
      <Sfx src="sfx_stamp.mp3" at={f(7.8)} volume={STAMP} />
      <Sfx src="sfx_paper.mp3" at={f(9.0)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(9.8)} volume={DRAW} />
      <Sfx src="sfx_paper.mp3" at={f(11.0)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(11.8)} volume={DRAW} />
      <Sfx src="sfx_paper.mp3" at={f(12.7)} volume={PAPER} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
