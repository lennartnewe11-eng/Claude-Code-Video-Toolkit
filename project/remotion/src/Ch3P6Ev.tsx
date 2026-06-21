import {AbsoluteFill, Audio, interpolate, Loop, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, TapedPhoto, Stamp, Highlight, RedNote, FileTag, Seal, Crosshair} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 382.745;
export const C3P6_DURATION = Math.round(29.3 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3, DRAW = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const VideoPanel: React.FC<{src: string; left: number; top: number; w: number; h: number; loopFrames: number; rot?: number}> = ({src, left, top, w, h, loopFrames, rot = 0}) => (
  <div style={{position: 'absolute', left, top, width: w, height: h, transform: `rotate(${rot}deg)`, overflow: 'hidden', border: '8px solid #1b1812', boxShadow: '6px 10px 18px rgba(20,16,10,0.36)'}}>
    <Loop durationInFrames={loopFrames} layout="none">
      <OffthreadVideo src={staticFile(`clips/${src}`)} muted style={{width: w, height: h, objectFit: 'cover', filter: 'grayscale(1) contrast(1.18)'}} />
    </Loop>
    <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.16) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.4}} />
    <AbsoluteFill style={{boxShadow: 'inset 0 0 120px rgba(0,0,0,0.6)'}} />
  </div>
);

/** A small drawn US flag (subtle wave). */
const Flag: React.FC<{x: number; y: number; w?: number; at?: number; rot?: number}> = ({x, y, w = 240, at = 0, rot = -3}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const wave = Math.sin(frame / 12) * 1.4;
  const h = w * 0.53;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: o, transform: `rotate(${rot + wave}deg)`, boxShadow: '4px 6px 12px rgba(20,16,10,0.34)', backgroundImage: `repeating-linear-gradient(0deg, #b3271c 0, #b3271c ${h / 13}px, #f3efe4 ${h / 13}px, #f3efe4 ${(h / 13) * 2}px)`, filter: 'grayscale(0.35) contrast(1.05)'}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: w * 0.42, height: (h / 13) * 7, background: '#23335c', display: 'flex', flexWrap: 'wrap', alignContent: 'center', justifyContent: 'center', gap: w * 0.018, padding: 6}}>
        {Array.from({length: 24}).map((_, i) => <div key={i} style={{width: w * 0.022, height: w * 0.022, borderRadius: '50%', background: '#f3efe4'}} />)}
      </div>
    </div>
  );
};

/** A stack of legislative acts that builds upward (accumulation motif). */
const ActStack: React.FC<{x: number; y: number; from: number; labels: string[]}> = ({x, y, from, labels}) => {
  const frame = useCurrentFrame();
  const cardW = 380, cardH = 50, step = 40;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: cardW + 30, height: labels.length * step + cardH}}>
      {labels.map((lab, i) => {
        const appear = from + i * 7;
        const o = interpolate(frame - appear, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const ty = interpolate(frame - appear, [0, 7], [28, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const rot = (i % 2 ? 1 : -1) * 1.1;
        const top = (labels.length - 1 - i) * step;
        const top2 = labels.length - 1 - i;
        const hot = i === labels.length - 1;
        return (
          <div key={i} style={{position: 'absolute', left: (i % 3) - 1, top: top + ty, width: cardW, height: cardH, opacity: o, transform: `rotate(${rot}deg)`, background: '#fbf8ef', boxShadow: '0 2px 4px rgba(20,16,10,0.3)', borderLeft: `6px solid ${hot ? EV.yellow : EV.ink}`, display: 'flex', alignItems: 'center', paddingLeft: 16, zIndex: 100 - top2, fontFamily: mono, fontWeight: 700, fontSize: 21, color: EV.ink, textTransform: 'uppercase', letterSpacing: '0.04em'}}>
            {hot && <span style={{position: 'absolute', left: -5, top: '16%', height: '68%', width: '100%', background: EV.yellow, opacity: 0.5, zIndex: -1}} />}
            {lab}
          </div>
        );
      })}
    </div>
  );
};

/** Rising leaderboard podium: Japan on top, USA trailing. */
const Podium: React.FC<{x: number; y: number; from: number}> = ({x, y, from}) => {
  const frame = useCurrentFrame();
  const bars = [
    {label: 'JAPAN', rank: '1', h: 300, w: 210, delay: 0, gold: true},
    {label: 'EUROPA', rank: '?', h: 170, w: 190, delay: 8},
    {label: 'USA', rank: '?', h: 110, w: 190, delay: 14},
  ];
  let cx = 0;
  return (
    <div style={{position: 'absolute', left: x, top: y}}>
      {bars.map((b, i) => {
        const sc = interpolate(frame - from - b.delay, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const left = cx; cx += b.w + 16;
        return (
          <div key={i} style={{position: 'absolute', left, bottom: 0, width: b.w, height: b.h * sc, background: b.gold ? EV.yellow : '#cfc8b6', border: `3px solid ${EV.ink}`, transformOrigin: 'bottom'}}>
            <div style={{position: 'absolute', top: -54, left: 0, width: '100%', textAlign: 'center', fontFamily: cond, fontWeight: 700, fontSize: 48, color: b.gold ? EV.red : EV.inkSoft}}>{b.rank}</div>
            <div style={{position: 'absolute', bottom: 10, left: 0, width: '100%', textAlign: 'center', fontFamily: cond, fontWeight: 700, fontSize: 30, color: EV.ink, letterSpacing: '0.04em', opacity: sc}}>{b.label}</div>
          </div>
        );
      })}
    </div>
  );
};

/** A signed legislative document with a scrawled signature that draws on. */
const ActDoc: React.FC<{x: number; y: number; at: number; signAt: number}> = ({x, y, at, signAt}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sc = interpolate(frame - at, [0, 8], [0.92, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sig = interpolate(frame - signAt, [0, 22], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const DASH = 760;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: 470, opacity: o, transform: `rotate(2deg) scale(${sc})`, background: '#fbf8ef', padding: '28px 30px 26px', boxShadow: '8px 12px 22px rgba(20,16,10,0.34)'}}>
      <div style={{position: 'absolute', top: -16, left: 40, width: 110, height: 28, background: EV.tape, transform: 'rotate(-3deg)'}} />
      <div style={{fontFamily: mono, fontSize: 13, letterSpacing: '0.18em', color: EV.inkSoft}}>89TH CONGRESS · 1965</div>
      <div style={{fontFamily: cond, fontWeight: 700, fontSize: 34, lineHeight: 1.0, color: EV.ink, textTransform: 'uppercase', margin: '8px 0 14px'}}>High-Speed Ground Transportation Act</div>
      {['to provide for research and development', 'in high-speed ground transportation', 'within the United States …'].map((t, i) => (
        <div key={i} style={{fontFamily: mono, fontSize: 14, color: EV.ink, opacity: 0.7, marginBottom: 5}}>{t}</div>
      ))}
      <div style={{marginTop: 24, borderTop: `2px solid ${EV.inkSoft}`, width: 230, paddingTop: 4, fontFamily: mono, fontSize: 12, color: EV.inkSoft}}>Lyndon B. Johnson, President</div>
      <svg style={{position: 'absolute', left: 36, top: 196}} width={240} height={70}>
        <path d="M6 46 C 24 8, 40 8, 44 40 C 48 60, 58 22, 78 30 C 96 38, 92 12, 110 18 C 138 28, 150 60, 176 28 C 196 6, 214 18, 232 40" fill="none" stroke={EV.ink} strokeWidth={4} strokeLinecap="round" strokeDasharray={DASH} strokeDashoffset={DASH * (1 - sig)} />
      </svg>
    </div>
  );
};

export const Ch3P6Ev: React.FC = () => {
  const OLY = f(6.95);

  return (
    <AbsoluteFill>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />
      <div style={{position: 'absolute', right: 0, top: 0, width: 150, height: 360, background: EV.red, opacity: 0.13, transform: 'skewX(-8deg) translateX(60px)'}} />

      {/* header */}
      <FileTag text="3·d" x={150} y={92} at={f(0.4)} size={62} />
      <TypeHeading text="Akte — Die Politik greift ein" x={210} y={78} size={26} at={f(0.2)} />
      <Crosshair x={1500} y={70} at={f(0.8)} />
      <Seal text={'WEISSES\nHAUS\n1965'} x={1810} y={120} at={f(2.0)} size={150} rot={-10} />

      {/* ── Board A: politics wants to catch up ── */}
      <Group show={[0, f(10.9)]}>
        <TypeHeading text="Auch die Politik will aufholen" x={765} y={130} size={26} at={f(0.6)} highlight />
        <Headline text="Amerika gründlich" x={760} y={180} size={70} at={f(2.6)} />
        <Headline text="modernisieren" x={760} y={262} size={70} at={f(2.9)} />

        <TapedPhoto src="lbj.jpg" cx={380} cy={600} w={520} rot={-3} at={f(2.4)} caption="Präsident Lyndon B. Johnson" />
        <RedNote text="1963–69" x={250} y={400} size={40} at={f(3.0)} rot={-6} />

        <ActStack x={780} y={400} from={f(3.6)} labels={['Civil Rights Act', 'Medicare', 'Voting Rights Act', 'Clean Air Act', 'Hochgeschwindigkeit?']} />

        <Flag x={1540} y={210} w={250} at={f(7.2)} rot={-3} />
        <TypeHeading text="eine Frage des" x={1500} y={420} size={26} at={f(7.4)} color="#5d574c" />
        <Headline text="nationalen Stolzes" x={1500} y={460} size={48} at={f(7.6)} />
      </Group>

      {/* ── Board B: Japan leads — of all nations ── */}
      <Group show={[f(10.4), f(19.3)]}>
        <Highlight x={120} y={210} w={900} at={f(11.0)} h={46} />
        <Headline text="Ausgerechnet Japan führt" x={120} y={150} size={76} at={f(10.8)} />

        <VideoPanel src="olympics64.mp4" left={120} top={320} w={620} h={440} loopFrames={OLY} rot={-1} />
        <div style={{position: 'absolute', left: 130, top: 772, fontFamily: mono, fontSize: 19, color: EV.inkSoft}}>Tokio 1964 · Japan an der Spitze</div>

        <Podium x={1180} y={760} from={f(11.6)} />
        <RedNote text="↑" x={1290} y={420} size={70} at={f(13.0)} rot={0} />
        <Stamp text="20 Jahre zuvor: noch im Krieg" x={1380} y={310} size={34} at={f(14.4)} rot={-6} />
      </Group>

      {/* ── Board C: the Act is signed ── */}
      <Group show={[f(18.8), C3P6_DURATION]}>
        <TypeHeading text="1965 — der Startschuss" x={125} y={120} size={26} at={f(19.0)} highlight />
        <Headline text="High-Speed Ground" x={120} y={170} size={64} at={f(19.2)} />
        <Headline text="Transportation Act" x={120} y={245} size={64} at={f(19.5)} />

        <TapedPhoto src="lbjsign.jpg" cx={470} cy={640} w={660} rot={-2} at={f(19.6)} caption="L. B. Johnson unterzeichnet, 1965" />
        <ActDoc x={1080} y={350} at={f(20.4)} signAt={f(22.0)} />
        <Stamp text="unterzeichnet" x={1230} y={690} size={48} at={f(24.2)} rot={-8} />

        <Highlight x={1080} y={800} w={700} at={f(26.4)} h={42} />
        <Headline text="Ziel: den Bullet Train" x={1080} y={760} size={50} at={f(26.2)} />
        <Headline text="alt aussehen lassen" x={1080} y={830} size={50} at={f(26.6)} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P6_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(2.4)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(3.6)} volume={0.22} />
      <Sfx src="sfx_paper.mp3" at={f(4.5)} volume={0.2} />
      <Sfx src="sfx_paper.mp3" at={f(5.4)} volume={0.2} />
      <Sfx src="sfx_stamp.mp3" at={f(14.4)} volume={STAMP} />
      <Sfx src="sfx_paper.mp3" at={f(19.6)} volume={PAPER} />
      <Sfx src="sfx_draw.mp3" at={f(22.0)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(24.2)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
