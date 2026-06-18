import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Typewriter, TapedPhoto, Stamp, Highlight, Crosshair} from './style/Evidence';
import {mono, cond, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 160.96;
export const C2P6_DURATION = Math.round(29.0 * FPS);
const f = (s: number) => Math.round(s * FPS);
const PAPER = 0.3, STAMP = 0.5, TYPE = 0.2, DRONE = 0.06;

const FX = 960, FY = 360, L = 700, HANG = 96;

/** A small weight/label tag that drops onto a scale pan. */
const Tag: React.FC<{x: number; y: number; at: number; text: string; color: string; ink?: string}> = ({x, y, at, text, color, ink = '#fff'}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (frame < at - 1) return null;
  return (
    <div style={{position: 'absolute', left: x, top: y - (1 - p) * 60, transform: 'translate(-50%,-50%)', opacity: p, background: color, color: ink, fontFamily: mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.06em', padding: '6px 14px', whiteSpace: 'nowrap', boxShadow: '2px 3px 6px rgba(20,16,10,0.3)'}}>
      {text}
    </div>
  );
};

export const Ch2P6Ev: React.FC = () => {
  const frame = useCurrentFrame();

  // scale tips left (BAHN) down as its burden grows
  const tilt = interpolate(frame, [f(5.5), f(8.5), f(18.5), f(23.5)], [-1, -9, -9, -16], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const a = (tilt * Math.PI) / 180;
  const lEnd = {x: FX - Math.cos(a) * L / 2, y: FY - Math.sin(a) * L / 2};
  const rEnd = {x: FX + Math.cos(a) * L / 2, y: FY + Math.sin(a) * L / 2};
  const lPan = {x: lEnd.x, y: lEnd.y + HANG};
  const rPan = {x: rEnd.x, y: rEnd.y + HANG};

  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 02 — Der ungleiche Wettkampf" x={110} y={70} size={26} at={f(0.2)} highlight />
      <Crosshair x={1850} y={70} at={f(0.8)} />
      <Typewriter text="Das Auto hatte einen entscheidenden Vorteil:" x={110} y={135} size={26} at={f(0.4)} cps={32} />

      {/* ── the balance ── */}
      {/* fulcrum */}
      <div style={{position: 'absolute', left: FX, top: FY, transform: 'translate(-50%,0)', width: 0, height: 0, borderLeft: '26px solid transparent', borderRight: '26px solid transparent', borderBottom: `120px solid ${EV.ink}`}} />
      {/* beam */}
      <div style={{position: 'absolute', left: FX, top: FY, width: L, height: 12, background: EV.ink, transform: `translate(-50%,-50%) rotate(${tilt}deg)`, borderRadius: 6}} />
      {/* hangers */}
      <svg style={{position: 'absolute', left: 0, top: 0}} width={1920} height={1080}>
        <line x1={lEnd.x} y1={lEnd.y} x2={lPan.x} y2={lPan.y} stroke={EV.ink} strokeWidth={3} />
        <line x1={rEnd.x} y1={rEnd.y} x2={rPan.x} y2={rPan.y} stroke={EV.ink} strokeWidth={3} />
      </svg>
      {/* pans */}
      <div style={{position: 'absolute', left: lPan.x, top: lPan.y, transform: 'translate(-50%,-50%)', width: 280, height: 12, background: EV.ink, borderRadius: 6}} />
      <div style={{position: 'absolute', left: rPan.x, top: rPan.y, transform: 'translate(-50%,-50%)', width: 280, height: 12, background: EV.ink, borderRadius: 6}} />
      <div style={{position: 'absolute', left: lPan.x, top: lPan.y + 34, transform: 'translate(-50%,-50%)', fontFamily: cond, fontWeight: 700, fontSize: 40, color: EV.ink}}>DIE BAHN</div>
      <div style={{position: 'absolute', left: rPan.x, top: rPan.y + 34, transform: 'translate(-50%,-50%)', fontFamily: cond, fontWeight: 700, fontSize: 40, color: EV.ink}}>DAS AUTO</div>

      {/* BAHN burden tags (stack up from its pan) */}
      <TypeHeading text="Privatunternehmen" x={lPan.x - 110} y={lPan.y - 210} size={18} at={f(3.3)} />
      <Tag x={lPan.x} y={lPan.y - 30} at={f(5.8)} text="Gleise BAUEN — selbst" color={EV.red} />
      <Tag x={lPan.x} y={lPan.y - 74} at={f(6.7)} text="WARTEN — selbst" color={EV.red} />
      <Tag x={lPan.x} y={lPan.y - 118} at={f(7.6)} text="BEZAHLEN — selbst" color={EV.red} />
      <Tag x={lPan.x} y={lPan.y - 162} at={f(19.1)} text="+ GEWINN machen" color={EV.red} />

      {/* AUTO side: the state pays */}
      <Tag x={rPan.x} y={rPan.y - 30} at={f(10.8)} text="Straßen = der STAAT" color={EV.ink} />
      <Tag x={rPan.x} y={rPan.y - 74} at={f(13.2)} text="mit Steuergeld" color={EV.yellow} ink={EV.ink} />
      <Tag x={rPan.x} y={rPan.y - 118} at={f(14.4)} text="KOSTENLOS" color={EV.yellow} ink={EV.ink} />
      <Tag x={rPan.x} y={rPan.y - 162} at={f(23.4)} text="geschenkt" color={EV.yellow} ink={EV.ink} />

      {/* evidence photos */}
      <TapedPhoto src="railworkers.jpg" cx={250} cy={830} w={360} rot={-3} at={f(5.8)} caption="Bahn baut & wartet selbst" />
      <TapedPhoto src="roadworkers.jpg" cx={1670} cy={830} w={360} rot={3} at={f(10.8)} caption="Straßen: WPA, Steuergeld" />

      {/* verdict + close */}
      <Stamp text="Brutal ungleich" x={960} y={620} size={62} at={f(16.9)} rot={-6} />
      <Highlight x={150} y={978} w={1180} at={f(26.6)} h={30} />
      <Headline text="Ein Wettkampf, den die Bahn nur verlieren konnte" x={150} y={960} size={56} at={f(26.6)} />

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P6_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.4)} n={9} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(5.8)} volume={0.28} />
      <Sfx src="sfx_stamp.mp3" at={f(5.8)} volume={0.32} />
      <Sfx src="sfx_stamp.mp3" at={f(6.7)} volume={0.32} />
      <Sfx src="sfx_stamp.mp3" at={f(7.6)} volume={0.32} />
      <Sfx src="sfx_paper.mp3" at={f(10.8)} volume={0.28} />
      <Sfx src="sfx_stamp.mp3" at={f(16.9)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(19.1)} volume={0.32} />
      <Sfx src="sfx_stamp.mp3" at={f(26.6)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
