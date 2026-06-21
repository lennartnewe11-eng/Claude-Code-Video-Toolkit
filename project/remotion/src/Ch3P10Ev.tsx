import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, BodyBlock, Dossier, QuoteBox, Stamp, Highlight, RedNote, FileTag, Seal, CornerMarks, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 482.161;
export const C3P10_DURATION = Math.round(30.5 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const Tape: React.FC<{x: number; y: number; w?: number; rot?: number}> = ({x, y, w = 110, rot = -4}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: 28, background: EV.tape, transform: `rotate(${rot}deg)`}} />
);
const Scrap: React.FC<{text: string; x: number; y: number; at?: number; rot?: number; w?: number}> = ({text, x, y, at = 0, rot = -2, w = 320}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, opacity: o, transform: `rotate(${rot}deg)`, background: '#fbf8ef', padding: '10px 14px', boxShadow: '3px 5px 9px rgba(20,16,10,0.28)', fontFamily: mono, fontSize: 18, color: EV.ink, lineHeight: 1.3}}>
      <Tape x={w / 2 - 40} y={-14} w={80} rot={3} />{text}
    </div>
  );
};

/** Built-up speed comparison: test (240) vs real-world (177). */
const SpeedCompare: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const maxW = 760, scaleMax = 260;
  const p = interpolate(frame, [from, from + f(2.4)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const testW = maxW * (240 / scaleMax) * p, realW = maxW * (177 / scaleMax) * p;
  const goal = maxW * (240 / scaleMax);
  const Bar: React.FC<{w: number; col: string; label: string; n: number; top: number}> = ({w, col, label, n, top}) => (
    <>
      <div style={{position: 'absolute', left: 0, top, width: w, height: 64, background: col, border: `3px solid ${EV.ink}`}} />
      <div style={{position: 'absolute', left: 12, top: top + 16, fontFamily: cond, fontWeight: 700, fontSize: 28, color: EV.ink, textTransform: 'uppercase'}}>{label}</div>
      <div style={{position: 'absolute', left: w + 16, top: top + 4, fontFamily: cond, fontWeight: 700, fontSize: 54, color: col === EV.yellow ? EV.ink : EV.red}}>{Math.round(n * p)}<span style={{fontSize: 22, fontFamily: mono}}> km/h</span></div>
    </>
  );
  return (
    <div style={{position: 'absolute', left: x, top: y, width: maxW + 220, height: 200}}>
      <Bar w={testW} col={EV.yellow} label="Test · gerade" n={240} top={0} />
      <Bar w={realW} col="#cf6a60" label="Alltag · kurvig" n={177} top={92} />
      {/* goal line */}
      <div style={{position: 'absolute', left: goal, top: -12, width: 0, height: 180, borderLeft: `3px dashed ${EV.ink}`}} />
      <div style={{position: 'absolute', left: goal - 30, top: -36, fontFamily: mono, fontWeight: 700, fontSize: 18, color: EV.ink}}>Ziel 240</div>
    </div>
  );
};

/** Accumulating defect log. */
const DefectLog: React.FC<{x: number; y: number; from: number; rows: string[]}> = ({x, y, from, rows}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: x, top: y, width: 520}}>
      {rows.map((r, i) => {
        const o = interpolate(frame - from - i * 7, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (
          <div key={i} style={{display: 'flex', alignItems: 'center', opacity: o, marginBottom: 10, fontFamily: mono, fontSize: 20, color: EV.ink}}>
            <span style={{color: EV.red, fontWeight: 700, fontSize: 26, marginRight: 12}}>✗</span>{r}
          </div>
        );
      })}
    </div>
  );
};

export const Ch3P10Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <Halftone opacity={0.11} size={7} />
      <div style={{position: 'absolute', left: 0, top: 0, width: 150, height: 380, background: EV.red, opacity: 0.13, transform: 'skewX(-8deg) translateX(-60px)'}} />

      {/* persistent header */}
      <FileTag text="3·g" x={150} y={92} at={f(0.4)} size={62} />
      <TypeHeading text="Akte — Prüfbericht: Metroliner" x={210} y={78} size={26} at={f(0.2)} />
      <Crosshair x={1500} y={70} at={f(0.8)} />
      <Seal text={'PRÜF-\nBERICHT\n1969'} x={1810} y={120} at={f(1.2)} size={150} rot={-10} />

      {/* ── Board A: the test result ── */}
      <Group show={[0, f(11.9)]}>
        <Highlight x={120} y={250} w={720} at={f(0.9)} h={46} />
        <Headline text="Auf dem Papier ein Erfolg" x={120} y={165} size={68} at={f(0.6)} />

        <TapedPhoto src="metroliner.jpg" cx={420} cy={620} w={640} rot={-2} at={f(1.6)} caption="Penn Central Metroliner, 1971" />
        <CornerMarks x={108} y={330} w={624} h={420} at={f(2.0)} />

        <BodyBlock x={870} y={330} w={520} at={f(3.0)} size={20}
          lines={[
            'Befund: Auf der alten Trasse ließ',
            'sich kaum etwas nachrüsten — nur',
            'notdürftig. Doch im Testbetrieb,',
            'auf einem idealen, geraden',
            'Abschnitt, lief der Zug frei.',
          ]} />
        <div style={{position: 'absolute', left: 870, top: 540}}>
          <RedNote text="240 km/h geknackt ✓" x={1140} y={40} size={48} at={f(7.4)} rot={-4} />
        </div>
        <Dossier x={870} y={600} w={620} at={f(8.0)} title="Testlauf — Idealstrecke"
          rows={[
            {label: 'Strecke', value: 'gerade & frei'},
            {label: 'Spitze', value: '240 km/h', hl: true},
            {label: 'Vorgabe', value: 'erfüllt', hl: true},
          ]} />
        <Scrap text="… aber nur unter Laborbedingungen." x={150} y={840} at={f(9.6)} rot={2} w={400} />
      </Group>

      {/* ── Board B: the real-world gap + defects ── */}
      <Group show={[f(11.5), f(22.9)]}>
        <TypeHeading text="Akte — Im Alltag" x={150} y={150} size={26} at={f(11.8)} />
        <Highlight x={120} y={290} w={680} at={f(12.2)} h={46} />
        <Headline text="In der Realität" x={120} y={200} size={78} at={f(11.9)} />

        <SpeedCompare x={120} y={420} from={f(12.4)} />
        <Scrap text="kurvige Bestandsstrecke = ständiges Bremsen" x={150} y={690} at={f(15.0)} rot={-2} w={520} />

        {/* defects (line 136) */}
        <TypeHeading text="Dazu: ständige Defekte" x={1180} y={300} size={26} at={f(17.9)} highlight />
        <DefectLog x={1180} y={370} from={f(18.4)} rows={['Unter Zeitdruck zusammengebaut', 'Anfällig für Defekte', 'Fiel immer wieder aus', 'Häufige Zwangspausen']} />
        <Stamp text="unzuverlässig" x={1400} y={720} size={48} at={f(21.4)} rot={-7} />
      </Group>

      {/* ── Board C: the verdict / the lesson ── */}
      <Group show={[f(22.5), C3P10_DURATION]}>
        <TapedPhoto src="metroliner_board.jpg" cx={1480} cy={560} w={560} rot={2} at={f(23.0)} caption="Fahrgäste am Metroliner, 1970er" />
        <CornerMarks x={1190} y={360} w={580} h={420} at={f(23.4)} />

        <TypeHeading text="Akte — Das Fazit" x={150} y={160} size={26} at={f(22.9)} />
        <Headline text="Keine technische" x={150} y={250} size={74} at={f(23.2)} />
        <Headline text="Niederlage —" x={150} y={330} size={74} at={f(23.5)} />
        <Highlight x={150} y={520} w={760} at={f(26.4)} h={50} />
        <Headline text="sondern eine Lehre" x={150} y={430} size={92} at={f(26.2)} />

        <QuoteBox text="Hochgeschwindigkeit war nie nur ein Zug-Problem." x={150} y={640} w={620} at={f(27.6)} rot={-2} size={24} cite="Prüfbericht-Fazit" />
        <Stamp text="Lehre verpasst" x={520} y={840} size={50} at={f(28.8)} rot={-6} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P10_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(1.6)} volume={PAPER} />
      <TypeClicks at={f(3.0)} n={9} gap={5} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(7.4)} volume={0.4} />
      <Sfx src="sfx_stamp.mp3" at={f(21.4)} volume={STAMP} />
      <Sfx src="sfx_paper.mp3" at={f(23.0)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(28.8)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
