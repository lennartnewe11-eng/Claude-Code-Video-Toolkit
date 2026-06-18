import {AbsoluteFill, Audio, interpolate, Loop, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, Halftone, TypeHeading, Headline, Stamp, Highlight, Dossier, QuoteBox, FileTag, Seal, CornerMarks, Crosshair} from './style/Evidence';
import {mono, EV} from './style/evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 275.52;
export const C3P1_DURATION = Math.round(15.0 * FPS);
const f = (s: number) => Math.round(s * FPS);
const TYPE = 0.2, STAMP = 0.5, DRONE = 0.06, PAPER = 0.3;

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [show[0], show[0] + 8, show[1] - 10, show[1]], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

/** Looping archival video panel (B/W, grain, vignette), optionally taped/tilted. */
const VideoPanel: React.FC<{
  src: string; left: number; top: number; w: number; h: number; loopFrames: number; startFrom?: number; rot?: number; tape?: boolean;
}> = ({src, left, top, w, h, loopFrames, startFrom = 0, rot = 0, tape}) => (
  <div style={{position: 'absolute', left, top, width: w, height: h, transform: `rotate(${rot}deg)`, overflow: 'visible', boxShadow: '6px 10px 18px rgba(20,16,10,0.36)', border: '8px solid #1b1812'}}>
    {tape && <div style={{position: 'absolute', top: -18, left: '50%', transform: 'translateX(-50%) rotate(-4deg)', width: 110, height: 28, background: EV.tape, zIndex: 3}} />}
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
      <Loop durationInFrames={loopFrames} layout="none">
        <OffthreadVideo src={staticFile(`clips/${src}`)} muted startFrom={startFrom} style={{width: w, height: h, objectFit: 'cover', filter: 'grayscale(1) contrast(1.16) brightness(1.0)'}} />
      </Loop>
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.16) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 3px)', opacity: 0.4}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 120px rgba(0,0,0,0.6)'}} />
    </div>
  </div>
);

export const Ch3P1Ev: React.FC = () => {
  const RAIL = f(14); // railpax loop length

  return (
    <AbsoluteFill>
      <GraphPaper />
      <Halftone opacity={0.1} size={7} />

      {/* title */}
      <Group show={[0, f(3.9)]}>
        <TypeHeading text="Kapitel 3" x={110} y={300} size={28} at={f(0.2)} highlight />
        <Headline text="Der verpasste Schnellzug" x={110} y={360} size={120} at={f(0.5)} />
        <TypeHeading text="Die Geschichte des Hochgeschwindigkeitszugs" x={115} y={520} size={28} at={f(1.4)} color="#5d574c" />
      </Group>

      {/* US rail dying — dossier board */}
      <Group show={[f(3.7), C3P1_DURATION]}>
        <FileTag text="03" x={150} y={92} at={f(4.6)} size={62} />
        <TypeHeading text="Akte — USA, Anfang 1960er" x={200} y={78} size={26} at={f(3.8)} />
        <Crosshair x={1500} y={70} at={f(4.2)} />
        <Seal text={'U.S. RAIL\nCASE FILE\n1960'} x={1810} y={120} at={f(4.8)} size={150} rot={-10} />

        {/* layered archival video panels (period footage, looped) */}
        <VideoPanel src="railpax.mp4" left={100} top={300} w={720} h={500} loopFrames={RAIL} />
        <CornerMarks x={88} y={288} w={744} h={524} at={f(4.4)} />
        <div style={{position: 'absolute', left: 112, top: 812, fontFamily: mono, fontSize: 19, color: EV.inkSoft, letterSpacing: '0.05em'}}>US-Personenverkehr · Mitte der 1950er (Archiv)</div>
        {/* second, smaller offset panel = different shot */}
        <VideoPanel src="railpax.mp4" left={560} top={210} w={340} h={250} loopFrames={RAIL} startFrom={Math.round(7.5 * FPS)} rot={3} tape />

        {/* verdict headline */}
        <Headline text="Personenverkehr" x={965} y={300} size={60} at={f(4.0)} />
        <Highlight x={965} y={414} w={600} at={f(4.8)} h={42} />
        <Headline text="= Verlustgeschäft" x={975} y={392} size={70} at={f(4.7)} />

        {/* typed case file */}
        <Dossier x={968} y={520} w={760} at={f(6.0)} title="Befund — Schienen-Personenverkehr"
          rows={[
            {label: 'Bilanz', value: 'Verlustgeschäft', hl: true},
            {label: 'Erträge aus', value: 'Güterverkehr', hl: true},
            {label: 'Fahrgäste gelten als', value: 'Last'},
            {label: 'Netz', value: 'schrumpft'},
          ]} />

        {/* quote slip */}
        <QuoteBox text="Personen bringen kein Geld mehr — nur Verluste." x={970} y={770} w={620} at={f(9.6)} rot={-2} size={24} cite="interne Einschätzung, um 1960" />

        {/* burden stamp over the crowd */}
        <Stamp text="Fahrgäste = Last" x={470} y={690} size={44} at={f(12.4)} rot={-6} />
      </Group>

      {/* sound */}
      <DroneBed durationInFrames={C3P1_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={6} gap={4} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(0.5)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(4.8)} volume={0.4} />
      <TypeClicks at={f(6.0)} n={8} gap={5} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(9.6)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(12.4)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
