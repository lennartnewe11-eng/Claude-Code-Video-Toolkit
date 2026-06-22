import {AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, Dossier, Stamp, Highlight, RedNote, RouteLine, FileTag, Seal, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 684.282;
export const C3P16_DURATION = Math.round(36.7 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3, DRAW = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const MAPX = 980, MAPY = 150, MAPW = 760, SC = MAPW / 520;
const mx = (vx: number) => MAPX + vx * SC;
const my = (vy: number) => MAPY + vy * SC;
const DALLAS: [number, number] = [mx(262), my(150)];
const HOUSTON: [number, number] = [mx(340), my(300)];

/** Hand-drawn Texas silhouette as a paper map cut-out. */
const TexasMap: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sc = interpolate(frame - at, [0, 12], [0.94, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const d = 'M175,28 L255,28 L255,98 L300,100 C345,108 365,124 384,156 L388,196 C386,236 372,262 352,288 C320,330 280,360 232,420 C210,398 178,360 150,338 C118,306 132,282 140,266 C108,244 78,236 96,214 C116,192 146,182 162,168 L162,120 L175,98 Z';
  return (
    <div style={{position: 'absolute', left: MAPX, top: MAPY, opacity: o, transform: `scale(${sc})`, transformOrigin: 'center'}}>
      <svg width={MAPW} height={MAPW * 480 / 520} viewBox="0 0 520 480">
        <path d={d} fill="#efe9da" stroke="#1b1812" strokeWidth={5} style={{filter: 'drop-shadow(6px 10px 10px rgba(20,16,10,0.3))'}} />
        <path d={d} fill="none" stroke="rgba(60,54,42,0.25)" strokeWidth={1} transform="translate(8,8)" />
      </svg>
    </div>
  );
};

/** Sleek bullet-train silhouette (cut-out style). */
const BulletTrain: React.FC<{x: number; y: number; rot: number; at: number; w?: number}> = ({x, y, rot, at, w = 360}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const h = w * 70 / 300;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: o, transform: `translate(-50%,-50%) rotate(${rot}deg)`, filter: 'drop-shadow(3px 5px 6px rgba(20,16,10,0.4))'}}>
      <svg width={w} height={h} viewBox="0 0 300 70">
        <path d="M6,52 C36,26 86,20 150,20 L286,20 C293,20 296,24 296,30 L296,52 C296,56 293,58 288,58 L12,58 C7,58 5,56 6,52 Z" fill="#17140f" />
        <path d="M6,52 C36,26 86,20 150,20 L150,30 C92,30 44,34 22,52 Z" fill="#2a261d" />
        {[120, 150, 180, 210, 240, 270].map((wx) => <rect key={wx} x={wx} y={30} width={20} height={14} rx={2} fill="#cfc8b6" />)}
        <rect x={6} y={46} width={290} height={5} fill={EV.red} />
        <circle cx={30} cy={44} r={4} fill="#cfc8b6" />
      </svg>
    </div>
  );
};

/** Governance blockers stacking up — each level can stop the project. */
const GovStack: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const rows = ['Bund', 'Bundesstaat', 'Bezirke', 'Städte'];
  return (
    <div style={{position: 'absolute', left: x, top: y}}>
      {rows.map((r, i) => {
        const at = from + i * 9;
        const o = interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const tx = interpolate(frame - at, [0, 7], [-26, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (
          <div key={i} style={{position: 'absolute', top: i * 92, left: tx, opacity: o, display: 'flex', alignItems: 'center'}}>
            <div style={{width: 360, height: 70, background: '#fbf8ef', borderLeft: `7px solid ${EV.ink}`, boxShadow: '2px 4px 8px rgba(20,16,10,0.3)', display: 'flex', alignItems: 'center', paddingLeft: 22, fontFamily: cond, fontWeight: 700, fontSize: 40, color: EV.ink, textTransform: 'uppercase'}}>{r}</div>
            <div style={{marginLeft: 22, fontFamily: cond, fontWeight: 700, fontSize: 30, color: EV.red, border: `4px solid ${EV.red}`, padding: '4px 14px', transform: 'rotate(-4deg)'}}>STOPP ✋</div>
          </div>
        );
      })}
    </div>
  );
};

export const Ch3P16Ev: React.FC = () => {
  const frame = useCurrentFrame();
  const cost = Math.round(interpolate(frame, [f(8.0), f(10.4)], [12, 41], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));

  return (
    <AbsoluteFill>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />
      <div style={{position: 'absolute', right: 0, top: 0, width: 150, height: 380, background: EV.red, opacity: 0.12, transform: 'skewX(-8deg) translateX(60px)'}} />

      {/* header */}
      <FileTag text="04" x={150} y={92} at={f(0.4)} size={62} />
      <TypeHeading text="Akte — Texas" x={210} y={78} size={26} at={f(0.2)} />
      <Crosshair x={1500} y={70} at={f(0.8)} />
      <Seal text={'TEXAS\nCENTRAL\nprivat'} x={1810} y={120} at={f(1.0)} size={150} rot={-10} />

      {/* ── Board A: the Dallas–Houston project ── */}
      <Group show={[0, f(12.6)]}>
        <Headline text="Texas — dieselbe" x={110} y={180} size={66} at={f(0.6)} />
        <Headline text="Geschichte" x={110} y={252} size={66} at={f(0.9)} />
        <TypeHeading text="Privates Unternehmen: Dallas ↔ Houston" x={115} y={360} size={24} at={f(3.8)} highlight />

        {/* Texas map with the route */}
        <TexasMap at={f(1.0)} />
        <Img src={staticFile('cutouts/houston.png')} style={{position: 'absolute', left: HOUSTON[0] - 130, top: HOUSTON[1] - 70, width: 260, filter: 'grayscale(1) contrast(1.1) drop-shadow(2px 4px 5px rgba(20,16,10,0.4))', opacity: interpolate(frame, [f(5.0), f(5.8)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} />
        <RouteLine points={[DALLAS, HOUSTON]} at={f(4.2)} drawFrames={20} arrow width={6} />
        <BulletTrain x={(DALLAS[0] + HOUSTON[0]) / 2} y={(DALLAS[1] + HOUSTON[1]) / 2} rot={56} at={f(6.2)} w={300} />
        <div style={{position: 'absolute', left: DALLAS[0] - 10, top: DALLAS[1] - 54, fontFamily: mono, fontWeight: 700, fontSize: 24, color: EV.ink}}>Dallas</div>
        <div style={{position: 'absolute', left: HOUSTON[0] + 30, top: HOUSTON[1] + 60, fontFamily: mono, fontWeight: 700, fontSize: 24, color: EV.ink}}>Houston</div>

        {/* cost explosion */}
        <div style={{position: 'absolute', left: 120, top: 520, fontFamily: mono, fontWeight: 700, fontSize: 24, letterSpacing: '0.1em', color: EV.inkSoft}}>GESCHÄTZTE KOSTEN</div>
        <div style={{position: 'absolute', left: 120, top: 560, fontFamily: cond, fontWeight: 700, fontSize: 150, lineHeight: 0.9, color: cost > 30 ? EV.red : EV.ink}}>${cost}<span style={{fontSize: 50, fontFamily: mono}}> Mrd.</span></div>
        <RedNote text="von $12 Mrd. → über $40 Mrd." x={420} y={760} size={40} at={f(10.6)} rot={-3} />
      </Group>

      {/* ── Board B: investors flee, funding pulled ── */}
      <Group show={[f(12.3), f(19.6)]}>
        <TypeHeading text="Akte — Das Aus" x={150} y={150} size={26} at={f(12.5)} />
        <Highlight x={120} y={290} w={820} at={f(12.9)} h={48} />
        <Headline text="Die Investoren springen ab" x={120} y={200} size={74} at={f(12.6)} />
        <Dossier x={120} y={420} w={680} at={f(13.6)} title="Projektende"
          rows={[
            {label: 'Investoren', value: 'ziehen sich zurück', hl: true},
            {label: 'Staatliche Förderung', value: 'gestrichen', hl: true},
            {label: 'Status', value: 'gescheitert'},
          ]} />
        <Stamp text="abgesprungen" x={1380} y={520} size={64} at={f(15.4)} rot={-8} />
        <TypeHeading text="Dahinter: ein wiederkehrendes Muster" x={120} y={760} size={30} at={f(17.6)} highlight />
      </Group>

      {/* ── Board C: the recurring pattern — fragmented power ── */}
      <Group show={[f(17.3), C3P16_DURATION]}>
        <TypeHeading text="Akte — Das Muster" x={150} y={120} size={26} at={f(17.5)} />
        <Crosshair x={1850} y={70} at={f(17.6)} />
        <Headline text="Alle reden mit —" x={110} y={200} size={70} at={f(20.0)} />
        <Headline text="jeder kann blockieren" x={110} y={272} size={70} at={f(20.4)} />

        <GovStack x={110} y={420} from={f(20.2)} />
        <TapedPhoto src="gavel.jpg" cx={1430} cy={400} w={520} rot={3} at={f(26.8)} caption="Jahrelange Gerichtsprozesse" />
        <RedNote text="Niemand kann einfach entscheiden zu bauen" x={1430} y={680} size={32} at={f(30.2)} rot={-3} />
        <Stamp text="Jahre vor Gericht" x={1430} y={800} size={48} at={f(33.8)} rot={-6} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P16_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(1.0)} volume={0.4} />
      <Sfx src="sfx_draw.mp3" at={f(4.2)} volume={DRAW} />
      <Sfx src="sfx_paper.mp3" at={f(5.0)} volume={PAPER} />
      <TypeClicks at={f(13.6)} n={8} gap={5} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(15.4)} volume={STAMP} />
      {[0, 1, 2, 3].map((i) => <Sfx key={i} src="sfx_stamp.mp3" at={f(20.2) + i * 9} volume={0.4} />)}
      <Sfx src="sfx_paper.mp3" at={f(26.8)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(33.8)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
