import {AbsoluteFill, Audio, Img, interpolate, Loop, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, Stamp, Highlight, RedNote, RouteLine, BigX, Crosshair, Seal} from './style/Evidence';
import {cond, mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 290.54;
export const C3P2_DURATION = Math.round(23.42 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, DRAW = 0.3, PAPER = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** A framed photo whose oversized image pans sideways → reads like tracking footage. */
const MovingPhoto: React.FC<{
  src: string; left: number; top: number; w: number; h: number; from: number; panFrac?: number; zoom?: number; speedLines?: boolean;
}> = ({src, left, top, w, h, from, panFrac = 0.18, zoom = 1.18, speedLines}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + f(7)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const imgW = w * zoom;
  const pan = -panFrac * (imgW - w) * t;
  return (
    <div style={{position: 'absolute', left, top, width: w, height: h, overflow: 'hidden', border: '8px solid #1b1812', boxShadow: '6px 10px 18px rgba(20,16,10,0.36)'}}>
      <Img src={staticFile(`photos/${src}`)} style={{position: 'absolute', left: pan, top: '50%', width: imgW, transform: 'translateY(-50%)', filter: 'grayscale(1) contrast(1.12) brightness(1.0)'}} />
      {speedLines && (
        <AbsoluteFill style={{
          backgroundImage: `repeating-linear-gradient(90deg, rgba(255,255,255,0.0) 0px, rgba(255,255,255,0.0) 60px, rgba(255,255,255,0.22) 62px, rgba(255,255,255,0.0) 66px)`,
          backgroundPositionX: -((frame * 40) % 200),
          opacity: 0.5, mixBlendMode: 'screen',
        }} />
      )}
      <AbsoluteFill style={{boxShadow: 'inset 0 0 120px rgba(0,0,0,0.55)'}} />
    </div>
  );
};

/** Looping documentary video panel (B/W, grain, vignette). */
const VideoPanel: React.FC<{left: number; top: number; w: number; h: number; loopFrames: number}> = ({left, top, w, h, loopFrames}) => (
  <div style={{position: 'absolute', left, top, width: w, height: h, overflow: 'hidden', border: '8px solid #1b1812', boxShadow: '6px 10px 18px rgba(20,16,10,0.36)'}}>
    <Loop durationInFrames={loopFrames} layout="none">
      <OffthreadVideo src={staticFile('clips/olympics64.mp4')} muted style={{width: w, height: h, objectFit: 'cover', filter: 'grayscale(1) contrast(1.18) brightness(1.02)'}} />
    </Loop>
    <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.16) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.45}} />
    <AbsoluteFill style={{boxShadow: 'inset 0 0 120px rgba(0,0,0,0.6)'}} />
  </div>
);

export const Ch3P2Ev: React.FC = () => {
  const frame = useCurrentFrame();
  const OLY = f(6.95); // olympics loop length

  // speed counter for phase C
  const kmh = Math.round(interpolate(frame, [f(13.8), f(16.6)], [0, 210], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));

  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 03 — Die andere Seite der Welt" x={110} y={70} size={26} at={f(0.3)} />
      <Crosshair x={1850} y={70} at={f(0.9)} />

      {/* ── Phase A: USA dying → arc to Japan ── */}
      <Group show={[0, f(7.0)]}>
        {/* small US panel struck out */}
        <div style={{position: 'absolute', left: 150, top: 360, width: 420, height: 300, overflow: 'hidden', border: '7px solid #1b1812', boxShadow: '5px 8px 14px rgba(20,16,10,0.34)'}}>
          <Img src={staticFile('photos/passengertrain.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(1) contrast(1.1) brightness(0.78)'}} />
        </div>
        <TypeHeading text="USA" x={160} y={320} size={28} at={f(0.6)} />
        <BigX x={160} y={365} w={400} h={290} at={f(2.0)} />
        <RedNote text="stirbt" x={360} y={700} size={48} at={f(2.6)} rot={-5} />

        {/* sweeping marker arc to the right */}
        <RouteLine points={[[600, 480], [1050, 300], [1480, 470]]} at={f(3.4)} drawFrames={26} arrow width={5} />

        {/* Japan target */}
        <Headline text="Das genaue Gegenteil" x={1180} y={560} size={70} at={f(4.4)} />
        <TypeHeading text="dort: Aufbruch" x={1190} y={690} size={26} at={f(5.6)} highlight />
      </Group>

      {/* ── Phase B: Tokyo 1964 Olympics (real footage) ── */}
      <Group show={[f(6.8), f(11.4)]}>
        <VideoPanel left={170} top={230} w={900} h={620} loopFrames={OLY} />
        <div style={{position: 'absolute', left: 180, top: 800, fontFamily: mono, fontSize: 22, color: EV.inkSoft, letterSpacing: '0.06em'}}>Tokio 1964 · Olympische Spiele</div>
        <RedNote text="1964" x={300} y={300} size={86} at={f(7.4)} rot={-6} />

        <Headline text="Japan zeigt der Welt" x={1130} y={300} size={58} at={f(7.6)} />
        <Highlight x={1130} y={430} w={620} at={f(8.6)} h={40} />
        <Headline text="den Shinkansen" x={1140} y={410} size={88} at={f(8.6)} />
        <TypeHeading text="vorgestellt zu den Spielen" x={1135} y={560} size={24} at={f(9.6)} color="#5d574c" />
        <Stamp text="Bullet Train" x={1430} y={700} size={48} at={f(10.4)} rot={-5} />
      </Group>

      {/* ── Phase C: the Shinkansen itself + speed ── */}
      <Group show={[f(11.2), f(18.0)]}>
        <MovingPhoto src="shinkansen0.jpg" left={150} top={210} w={1180} h={660} from={f(11.2)} panFrac={0.55} zoom={1.22} speedLines />
        <div style={{position: 'absolute', left: 162, top: 818, fontFamily: mono, fontSize: 22, color: EV.inkSoft, letterSpacing: '0.06em'}}>Shinkansen, Serie 0 — Tōkaidō-Linie</div>

        <Headline text="Der erste echte" x={1390} y={250} size={52} at={f(11.6)} />
        <Headline text="Hochgeschwindig-" x={1390} y={320} size={52} at={f(11.9)} />
        <Headline text="keitszug der Welt" x={1390} y={390} size={52} at={f(12.2)} />

        {/* live speed counter */}
        <div style={{position: 'absolute', left: 1390, top: 560}}>
          <div style={{fontFamily: cond, fontWeight: 700, fontSize: 150, lineHeight: 0.9, color: EV.red}}>{kmh}</div>
          <div style={{fontFamily: mono, fontWeight: 700, fontSize: 30, letterSpacing: '0.2em', color: EV.ink, marginTop: 6}}>KM / H</div>
          {/* fill bar */}
          <div style={{marginTop: 18, width: 360, height: 16, border: `2px solid ${EV.ink}`, background: 'rgba(0,0,0,0.05)'}}>
            <div style={{height: '100%', width: `${interpolate(kmh, [0, 210], [0, 100])}%`, background: EV.yellow}} />
          </div>
        </div>
        <RedNote text="über 200!" x={1620} y={540} size={40} at={f(16.4)} rot={6} />
      </Group>

      {/* ── Phase D: world wonder / global race ── */}
      <Group show={[f(17.8), C3P2_DURATION]}>
        {/* keep real footage moving in a corner */}
        <VideoPanel left={1360} top={560} w={460} h={320} loopFrames={OLY} />
        <MovingPhoto src="shinkansen0.jpg" left={110} top={130} w={760} h={420} from={f(17.8)} panFrac={0.7} zoom={1.25} speedLines />

        <Highlight x={930} y={250} w={760} at={f(18.6)} h={46} />
        <Headline text="Über Nacht" x={930} y={210} size={96} at={f(18.4)} />
        <Headline text="zum Weltwunder" x={930} y={330} size={84} at={f(19.2)} />

        <TypeHeading text="Startschuss: ein globales Wettrennen" x={120} y={640} size={30} at={f(20.6)} highlight />
        {/* radiating race arrows */}
        <RouteLine points={[[420, 560], [620, 720]]} at={f(21.2)} drawFrames={16} arrow width={4} />
        <RouteLine points={[[470, 560], [470, 760]]} at={f(21.5)} drawFrames={16} arrow width={4} />
        <RouteLine points={[[520, 560], [330, 720]]} at={f(21.8)} drawFrames={16} arrow width={4} />
        <Seal text={'Welt-\nrennen\nstartet'} x={1180} y={760} at={f(21.4)} size={150} rot={-10} />
      </Group>

      {/* ── sound ── */}
      <DroneBed durationInFrames={C3P2_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.3)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_draw.mp3" at={f(3.4)} volume={DRAW} />
      <Sfx src="sfx_stamp.mp3" at={f(2.0)} volume={0.4} />
      <Sfx src="sfx_paper.mp3" at={f(6.9)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(10.4)} volume={STAMP} />
      <Sfx src="sfx_paper.mp3" at={f(11.2)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(18.4)} volume={STAMP} />
      <Sfx src="sfx_draw.mp3" at={f(21.2)} volume={DRAW} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
