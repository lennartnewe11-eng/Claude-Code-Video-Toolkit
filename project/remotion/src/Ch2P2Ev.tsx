import {AbsoluteFill, Audio, staticFile} from 'remotion';
import {FPS} from './timeline';
import {GraphPaper, TypeHeading, Headline, TapedPhoto, Typewriter, Highlight, Stamp, Seal, CornerMarks, DashedBox, Crosshair} from './style/Evidence';
import {Sfx, TypeClicks, DroneBed} from './style/Sound';

const START = 115.96;
export const C2P2_DURATION = Math.round(13.3 * FPS);
const f = (s: number) => Math.round(s * FPS);

const PAPER = 0.3, STAMP = 0.5, TYPE = 0.2, DRONE = 0.06;

/**
 * Chapter 2 · Beat 1 (115.96–129.24) — the Model T dossier.
 * 1908 launch -> "at first a toy: expensive, unreliable, no paved roads"
 * -> "not yet a serious rival". Dossier look: typed spec sheet with yellow
 * highlights, taped photos with corner marks, stamps, a round seal.
 */
export const Ch2P2Ev: React.FC = () => {
  return (
    <AbsoluteFill>
      <GraphPaper />
      <TypeHeading text="Akte 02 — Der Herausforderer" x={110} y={70} size={26} at={f(0.2)} highlight />
      <Seal text="Ford Motor Co · Detroit" x={1770} y={120} at={f(0.6)} size={150} />

      {/* Henry Ford — taped, corner-marked */}
      <TapedPhoto src="ford.jpg" cx={300} cy={470} w={340} rot={-3} at={f(0.5)} caption="Henry Ford" />
      <CornerMarks x={150} y={300} w={300} h={340} at={f(1.0)} />

      {/* Model T — taped */}
      <TapedPhoto src="modelt_photo.jpg" cx={1430} cy={340} w={620} rot={2} at={f(1.2)} caption="Ford Model T · 1908" />

      {/* spec sheet */}
      <DashedBox x={560} y={300} w={560} h={300} at={f(1.4)} />
      <TypeHeading text="Steckbrief" x={585} y={325} size={20} at={f(1.5)} />
      <Typewriter text="Hersteller ....... Ford, Detroit" x={585} y={385} size={26} at={f(1.7)} cps={34} />
      <Typewriter text="Markteinführung .. 1908" x={585} y={435} size={26} at={f(2.2)} cps={34} />
      <Typewriter text="Preis ............ $850" x={585} y={485} size={26} at={f(2.7)} cps={34} />
      <Highlight x={580} y={538} w={470} at={f(3.1)} h={28} />
      <Typewriter text="Status ... Spielzeug der Reichen" x={585} y={535} size={26} at={f(3.2)} cps={40} />

      {/* the verdict, beat by beat */}
      <Stamp text="Teuer" x={760} y={720} size={64} at={f(5.2)} rot={-7} />
      <Stamp text="Unzuverlässig" x={1080} y={780} size={56} at={f(5.9)} rot={5} />

      {/* the roads */}
      <TapedPhoto src="badroad.jpg" cx={1470} cy={770} w={560} rot={-2} at={f(6.6)} caption="Straßen: kaum befestigt" />
      <CornerMarks x={1200} y={640} w={540} h={300} at={f(7.2)} color="#b3271c" />

      {/* not yet a threat */}
      <Highlight x={300} y={935} w={760} at={f(10.5)} h={28} />
      <Headline text="Noch keine Gefahr" x={300} y={918} size={74} at={f(10.6)} />

      {/* ── sound ── */}
      <DroneBed durationInFrames={C2P2_DURATION} volume={DRONE} />
      <TypeClicks at={f(0.2)} n={5} gap={4} volume={TYPE} />
      <Sfx src="sfx_paper.mp3" at={f(0.5)} volume={PAPER} />
      <Sfx src="sfx_paper.mp3" at={f(1.2)} volume={PAPER} />
      <TypeClicks at={f(1.7)} n={16} gap={5} volume={TYPE} />
      <Sfx src="sfx_stamp.mp3" at={f(5.2)} volume={STAMP} />
      <Sfx src="sfx_stamp.mp3" at={f(5.9)} volume={STAMP} />
      <Sfx src="sfx_paper.mp3" at={f(6.6)} volume={PAPER} />
      <Sfx src="sfx_stamp.mp3" at={f(10.6)} volume={STAMP} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
