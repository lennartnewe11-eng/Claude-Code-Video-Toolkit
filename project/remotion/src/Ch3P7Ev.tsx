import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, MapBackdrop, RouteLine, MapDot, Stamp, Highlight, RedNote, FileTag, Seal, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 412.221;
export const C3P7_DURATION = Math.round(13.7 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3, DRAW = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 7, show[1] - 9, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const C: [number, number][] = [[1500, 300], [1180, 470], [950, 600], [770, 740]];

/** Dense population dots accumulating along the corridor (built-up motif). */
const DensityField: React.FC<{from: number}> = ({from}) => {
  const frame = useCurrentFrame();
  const pts: [number, number, number][] = [];
  for (let si = 0; si < C.length - 1; si++) {
    const [a, b] = [C[si], C[si + 1]];
    const ang = Math.atan2(b[1] - a[1], b[0] - a[0]) + Math.PI / 2;
    for (let k = 0; k < 16; k++) {
      const t = k / 16;
      const off = (((si * 37 + k * 53) % 13) - 6) * 9;
      const x = a[0] + (b[0] - a[0]) * t + Math.cos(ang) * off;
      const y = a[1] + (b[1] - a[1]) * t + Math.sin(ang) * off;
      pts.push([x, y, si * 16 + k]);
    }
  }
  return (
    <>
      {pts.map(([x, y, idx], i) => {
        const appear = from + idx * 0.7;
        const o = interpolate(frame - appear, [0, 5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const sz = 5 + (idx % 3) * 2;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: sz, height: sz, background: '#5d574c', opacity: o * 0.7, transform: 'translate(-50%,-50%) rotate(45deg)'}} />;
      })}
    </>
  );
};

export const Ch3P7Ev: React.FC = () => {
  const frame = useCurrentFrame();
  const arrowP = interpolate(frame, [f(9.0), f(9.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />

      {/* header */}
      <FileTag text="3·e" x={150} y={92} at={f(0.4)} size={62} />
      <TypeHeading text="Akte — Der Schauplatz" x={210} y={78} size={26} at={f(0.2)} />
      <Crosshair x={1850} y={70} at={f(0.8)} />

      {/* ── Board A: the corridor on the map ── */}
      <Group show={[0, f(6.4)]}>
        <Highlight x={120} y={290} w={860} at={f(1.0)} h={48} />
        <Headline text="Der Nord-Ost-Korridor" x={120} y={180} size={84} at={f(0.6)} />
        <TypeHeading text="dicht besiedelt — die Wahl fiel klar aus" x={125} y={300} size={26} at={f(1.4)} color="#5d574c" />

        <MapBackdrop src="us1867.jpg" cx={1180} cy={520} w={1100} at={f(0.6)} opacity={0.22} rot={2} />
        <DensityField from={f(2.4)} />
        <RouteLine points={C} at={f(1.6)} drawFrames={34} arrow width={6} />
        <MapDot x={C[0][0]} y={C[0][1]} label="New York" at={f(2.0)} />
        <MapDot x={C[1][0]} y={C[1][1]} label="Philadelphia" at={f(2.6)} below />
        <MapDot x={C[2][0]} y={C[2][1]} label="Baltimore" at={f(3.1)} below />
        <MapDot x={C[3][0]} y={C[3][1]} label="Washington" at={f(3.6)} below />
        <RedNote text="~360 km" x={1120} y={640} size={44} at={f(4.4)} rot={-6} />
      </Group>

      {/* ── Board B: two capitals, electrified since the 1930s ── */}
      <Group show={[f(6.0), C3P7_DURATION]}>
        <Headline text="Wirtschaft trifft Politik" x={120} y={150} size={66} at={f(6.2)} />

        <TapedPhoto src="nyc.jpg" cx={430} cy={470} w={620} rot={-2} at={f(6.6)} caption="New York — wirtschaftliche Hauptstadt" />
        <TapedPhoto src="capitol.jpg" cx={1480} cy={450} w={660} rot={2} at={f(7.6)} caption="Washington — politische Hauptstadt" />

        {/* connector */}
        <div style={{position: 'absolute', left: 760, top: 455, width: 360 * arrowP, height: 5, background: EV.red}} />
        <div style={{position: 'absolute', left: 760 + 360 * arrowP, top: 447, color: EV.red, fontFamily: cond, fontSize: 40, opacity: arrowP, transform: 'translateX(-6px)'}}>▶</div>

        <TapedPhoto src="gg1.jpg" cx={960} cy={820} w={760} rot={-1} at={f(10.0)} caption="elektrifiziert seit den 1930ern — PRR GG1" />
        <Highlight x={150} y={690} w={520} at={f(11.6)} h={40} />
        <Headline text="Strom seit den 1930ern" x={150} y={668} size={48} at={f(11.5)} />
        <RedNote text="⚡" x={1430} y={690} size={90} at={f(11.8)} rot={-8} />
        <Stamp text="ideale Strecke" x={1430} y={820} size={40} at={f(12.4)} rot={-6} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P7_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(1.6)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(2.0)} volume={0.3} />
      <Sfx src="sfx_paper.mp3" at={f(6.6)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(7.6)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(10.0)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(12.4)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
