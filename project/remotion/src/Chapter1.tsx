import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {PaperBackground} from './style/PaperBackground';
import {Cutout} from './style/Cutout';
import {EditorialText, Token} from './style/EditorialText';
import {AccentBlock, Kicker, Rule, PhotoCard} from './style/Bits';
import {RailLine, Counter, CompareBars} from './style/DataViz';
import {COLORS} from './style/theme';

const CH1_START = 36.22;
const CH1_END = 108.9;
export const CH1_DURATION = Math.round((CH1_END - CH1_START) * FPS);

// rel seconds -> comp frames
const F = (relSec: number) => Math.round(relSec * FPS);
// absolute transcript sec -> comp frames (relative to chapter start)
const A = (absSec: number) => Math.round((absSec - CH1_START) * FPS);

/** A scene: lives in a frame window, fades in/out. */
const Scene: React.FC<{from: number; dur: number; children: React.ReactNode}> = ({from, dur, children}) => (
  <Sequence from={from} durationInFrames={dur} layout="none">
    <FadeWrap dur={dur}>{children}</FadeWrap>
  </Sequence>
);

const FadeWrap: React.FC<{dur: number; children: React.ReactNode}> = ({dur, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 8, dur - 10, dur], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

export const Chapter1: React.FC = () => {
  return (
    <AbsoluteFill>
      <PaperBackground />

      {/* chapter-wide furniture */}
      <Kicker text="Kapitel 1 · Das goldene Zeitalter" x={120} y={70} delay={6} />
      <Rule x={120} y={122} w={520} delay={12} />

      {/* ── S1 · TITLE (36.2) ───────────────────────────── */}
      <Scene from={A(36.22)} dur={A(45.5) - A(36.22)}>
        <Cutout src="loco.png" cx={1340} cy={760} width={760} entrance="drive" delay={20} rotate={-2} />
        <EditorialText
          tokens={[
            {t: 'Das', display: true, size: 150, br: true},
            {t: 'goldene', display: true, size: 150, br: true},
            {t: 'Zeitalter', display: true, size: 190, accent: true},
          ]}
          cx={620} cy={430} width={1000} align="left"
        />
        <EditorialText
          tokens={[{t: 'Als'}, {t: 'Amerika'}, {t: 'die', w: 'italic'}, {t: 'Welt', w: 'boldItalic'}, {t: 'bewegte.'}]}
          cx={520} cy={640} width={800} baseSize={40} align="left" delay={70}
        />
      </Scene>

      {/* ── S2 · "DAS Verkehrsmittel" (45.5) ─────────────── */}
      <Scene from={A(45.5)} dur={A(52.46) - A(45.5)}>
        <Cutout src="loco.png" cx={1330} cy={620} width={900} entrance="drive" delay={10} />
        <EditorialText
          tokens={[
            {t: 'Im'}, {t: '19.'}, {t: 'Jahrhundert'}, {t: 'war'}, {t: 'die'}, {t: 'Bahn', w: 'bold', br: true},
            {t: 'nicht'}, {t: 'irgendein', w: 'italic'}, {t: 'Verkehrsmittel.'},
          ]}
          cx={620} cy={300} width={1000} baseSize={52} align="left"
        />
        {/* "Sie war DAS Verkehrsmittel" lands with the VO @ 49.73 */}
        <EditorialText
          tokens={[
            {t: 'Sie'}, {t: 'war'}, {t: 'DAS', display: true, size: 150, accent: true}, {t: 'Verkehrsmittel.'},
          ]}
          cx={560} cy={560} width={900} baseSize={64} align="left" delay={A(49.73) - A(45.5)}
        />
      </Scene>

      {/* ── S3 · 1869 transcontinental (52.46) ───────────── */}
      <Scene from={A(52.46)} dur={A(56.58) - A(52.46)}>
        <PhotoCard src="map1871.jpg" cx={1410} cy={420} width={620} rotate={-3} delay={6} sepia />
        <PhotoCard src="goldenspike.jpg" cx={1230} cy={800} width={460} rotate={4} delay={20} />
        <EditorialText tokens={[{t: '1869', display: true, size: 280}]} cx={330} cy={420} width={760} align="left" />
        <EditorialText
          tokens={[
            {t: 'die'}, {t: 'erste'}, {t: 'transkontinentale', w: 'boldItalic', br: true}, {t: 'Eisenbahn.'},
          ]}
          cx={420} cy={690} width={820} baseSize={50} align="left" delay={14}
        />
      </Scene>

      {/* ── S4 · days not months (56.58) ─────────────────── */}
      <Scene from={A(56.58)} dur={A(63.08) - A(56.58)}>
        <AbsoluteFill style={{background: 'radial-gradient(ellipse 560px 380px at 470px 470px, rgba(239,236,224,0.92) 0%, rgba(239,236,224,0) 100%)'}} />
        <Cutout src="wagon.png" cx={1380} cy={770} width={440} entrance="drop" delay={10} rotate={4} />
        <EditorialText
          tokens={[
            {t: 'was'}, {t: 'vorher', br: true},
            {t: 'MONATE', display: true, size: 140, br: true},
            {t: 'im'}, {t: 'Planwagen', w: 'bold'}, {t: 'dauerte', br: true},
            {t: '—'}, {t: 'nun'}, {t: 'nur'}, {t: 'noch', br: true},
            {t: 'TAGE', display: true, size: 140, accent: true},
          ]}
          cx={470} cy={470} width={720} baseSize={46} align="center" delay={6} stagger={3}
        />
      </Scene>

      {/* ── S5 · opened the West / towns on the line (63.08) ─ */}
      <Scene from={A(63.08)} dur={A(74.48) - A(63.08)}>
        <EditorialText
          tokens={[{t: 'Die'}, {t: 'Bahn'}, {t: 'erschloss', w: 'boldItalic'}, {t: 'den'}, {t: 'Westen.'}]}
          cx={620} cy={170} width={1100} baseSize={56} align="center"
        />
        <RailLine
          cx={960} cy={520} width={1500}
          stations={[
            {x: 0.0, label: 'Omaha'},
            {x: 0.5, label: 'Promontory 1869'},
            {x: 1.0, label: 'Sacramento'},
          ]}
          delay={20} drawFrames={70}
        />
        {/* towns spring up along the line */}
        <Cutout src="depot.png" cx={520} cy={760} width={420} entrance="pop" delay={A(68.35) - A(63.08)} rotate={-2} />
        <EditorialText
          tokens={[{t: 'Ganze'}, {t: 'Städte', w: 'bold'}, {t: 'entstehen', br: true}, {t: 'entlang'}, {t: 'der'}, {t: 'Schiene.'}]}
          cx={560} cy={870} width={760} baseSize={40} align="center" delay={A(68.35) - A(63.08) + 6}
        />
        <EditorialText
          tokens={[{t: 'Wer'}, {t: 'keinen'}, {t: 'Anschluss'}, {t: 'hatte', w: 'italic'}, {t: '—'}, {t: 'verschwand.', w: 'bold', accent: true}]}
          cx={1320} cy={250} width={760} baseSize={40} align="center" delay={A(71.34) - A(63.08)}
        />
      </Scene>

      {/* ── S6 · the tech giants (74.48) ─────────────────── */}
      <Scene from={A(74.48)} dur={A(81.26) - A(74.48)}>
        <EditorialText
          tokens={[{t: 'Die'}, {t: 'mächtigsten'}, {t: 'Konzerne', w: 'boldItalic'}, {t: 'ihrer'}, {t: 'Zeit.'}]}
          cx={960} cy={150} width={1200} baseSize={50} align="center"
        />
        <Cutout src="vanderbilt.png" cx={620} cy={680} width={420} entrance="drop" delay={12} rotate={-3} />
        <Cutout src="gould.png" cx={960} cy={640} width={420} entrance="drop" delay={20} rotate={2} />
        <Cutout src="stanford.png" cx={1300} cy={680} width={400} entrance="drop" delay={28} rotate={-2} />
        <EditorialText
          tokens={[{t: 'die'}, {t: 'TECH-GIGANTEN', display: true, size: 120, accent: true, br: true}, {t: 'des'}, {t: '19.'}, {t: 'Jahrhunderts.'}]}
          cx={960} cy={900} width={1300} baseSize={44} align="center" delay={A(78.32) - A(74.48)}
        />
      </Scene>

      {/* ── S7 · 254,000 miles (81.26) ───────────────────── */}
      <Scene from={A(81.26)} dur={A(87.88) - A(81.26)}>
        <EditorialText
          tokens={[{t: 'Auf'}, {t: 'dem'}, {t: 'Höhepunkt', w: 'boldItalic'}, {t: 'um'}, {t: '1916:'}]}
          cx={960} cy={210} width={1200} baseSize={50} align="center"
        />
        <Counter target={254000} unit="Meilen Schiene" cx={960} cy={560} delay={12} countFrames={140} />
      </Scene>

      {/* ── S8 · more than all of Europe (87.88) ─────────── */}
      <Scene from={A(87.88)} dur={A(92.52) - A(87.88)}>
        <EditorialText
          tokens={[{t: 'Mehr'}, {t: 'als'}, {t: 'ganz', w: 'italic'}, {t: 'Europa', w: 'boldItalic', accent: true}, {t: 'zusammen.'}]}
          cx={960} cy={220} width={1300} baseSize={54} align="center"
        />
        <CompareBars
          cx={920} cy={560} width={900}
          a={{label: 'USA', frac: 1.0}}
          b={{label: 'Europa', frac: 0.62}}
          delay={14}
        />
      </Scene>

      {/* ── S9 · a station in every town (92.52) ─────────── */}
      <Scene from={A(92.52)} dur={A(95.28) - A(92.52)}>
        <Cutout src="depot.png" cx={520} cy={560} width={520} entrance="slideR" delay={6} rotate={-2} />
        <Cutout src="depot.png" cx={1240} cy={560} width={520} entrance="drive" delay={12} rotate={2} flip />
        <EditorialText
          tokens={[{t: 'Jede'}, {t: 'Kleinstadt'}, {t: '—'}, {t: 'ein'}, {t: 'Bahnhof.', w: 'bold', accent: true}]}
          cx={960} cy={200} width={1200} baseSize={52} align="center"
        />
      </Scene>

      {/* ── S10 · luxury travel (95.28) ──────────────────── */}
      <Scene from={A(95.28)} dur={A(103.9) - A(95.28)}>
        <EditorialText
          tokens={[{t: 'Und'}, {t: 'das'}, {t: 'Reisen'}, {t: 'war'}, {t: 'komfortabel.', w: 'boldItalic'}]}
          cx={960} cy={130} width={1200} baseSize={46} align="center"
        />
        <PhotoCard src="pullman1.jpg" cx={470} cy={560} width={620} rotate={-4} delay={A(97.24) - A(95.28)} />
        <PhotoCard src="observation.jpg" cx={1020} cy={600} width={460} rotate={3} delay={A(98.94) - A(95.28)} />
        <PhotoCard src="pullman2.jpg" cx={1470} cy={540} width={560} rotate={-2} delay={A(100.62) - A(95.28)} />
        <EditorialText
          tokens={[{t: 'Schlafwagen.'}, {t: 'Speisewagen.', w: 'italic'}, {t: 'Aussichtswagen.', w: 'bold'}]}
          cx={960} cy={930} width={1400} baseSize={40} align="center" delay={A(97.24) - A(95.28)} stagger={18}
        />
      </Scene>

      {/* ── S11 · so dominant nobody imagined it ending (103.9) ─ */}
      <Scene from={A(103.9)} dur={CH1_DURATION - A(103.9)}>
        <Cutout src="loco.png" cx={960} cy={720} width={1000} entrance="drive" delay={8} />
        <EditorialText
          tokens={[
            {t: 'So'}, {t: 'dominant,', w: 'boldItalic'}, {t: 'dass'}, {t: 'niemand', br: true},
            {t: 'glaubte,'}, {t: 'es'}, {t: 'könnte'}, {t: 'je', w: 'italic'}, {t: 'enden.', w: 'bold', accent: true},
          ]}
          cx={960} cy={250} width={1300} baseSize={56} align="center"
        />
      </Scene>

      {/* voiceover spine + soft music bed */}
      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(CH1_START * FPS)} volume={1} />
      <Audio src={staticFile('audio/musicBed.mp3')} startFrom={Math.round(60 * FPS)} volume={0.09} />
    </AbsoluteFill>
  );
};
