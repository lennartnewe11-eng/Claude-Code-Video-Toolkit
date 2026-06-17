import {AbsoluteFill, Audio, staticFile} from 'remotion';
import {FPS} from './timeline';
import {PaperBackground} from './style/PaperBackground';
import {Kicker, Rule, AccentBlock} from './style/Bits';
import {ObjectBurst, WordFlash, Tick} from './style/Fast';
import {COLORS} from './style/theme';

const START = 36.22;
export const P1_DURATION = Math.round(13.4 * FPS);
const f = (s: number) => Math.round(s * FPS);

/**
 * Chapter 1 · Part 1 (36.22–49.6). High-frequency collage: a new object/word
 * roughly every ~0.5–0.7s, overlapping so the frame is never empty. Each of
 * the 14 cut-outs is used exactly once.
 */
export const Ch1P1: React.FC = () => {
  return (
    <AbsoluteFill>
      <PaperBackground />
      <Kicker text="Kapitel 1 · Das goldene Zeitalter" x={120} y={70} delay={4} />
      <Rule x={120} y={122} w={520} delay={10} />

      {/* ░ A · TITLE — "Das goldene Zeitalter" (0–2.6) ░ */}
      <ObjectBurst src="watch.png" at={f(0.15)} life={38} cx={300} cy={610} w={240} dir="d" rot={-6} />
      <WordFlash text="Das goldene" at={f(0.3)} life={66} cx={960} cy={420} size={128} />
      <ObjectBurst src="compass.png" at={f(0.55)} life={30} cx={1480} cy={300} w={380} dir="u" rot={6} />
      <WordFlash text="Zeitalter" at={f(0.75)} life={62} cx={960} cy={575} size={168} accent />
      <ObjectBurst src="lantern.png" at={f(1.05)} life={34} cx={1620} cy={580} w={150} dir="r" rot={5} />
      <ObjectBurst src="keys.png" at={f(1.5)} life={30} cx={320} cy={290} w={150} dir="l" rot={-12} />
      <ObjectBurst src="tophat.png" at={f(2.05)} life={30} cx={1520} cy={800} w={230} dir="d" rot={8} />
      <Tick at={f(0.2)} x={170} y={300} />

      {/* ░ B · "wie tief Amerika gefallen ist" (2.74–5.0) ░ */}
      <ObjectBurst src="spike.png" at={f(2.5)} life={30} cx={760} cy={300} w={340} dir="u" rot={-18} />
      <WordFlash text="Wie tief" at={f(2.7)} life={30} cx={640} cy={350} size={92} disp={false} italic />
      <WordFlash text="GEFALLEN" at={f(3.3)} life={48} cx={980} cy={560} size={178} accent />
      <ObjectBurst src="clock.png" at={f(3.6)} life={34} cx={1440} cy={610} w={240} dir="r" rot={6} />
      <ObjectBurst src="coin.png" at={f(4.3)} life={30} cx={600} cy={690} w={150} dir="d" rot={-4} />

      {/* ░ C · "zu Beginn des Eisenbahnzeitalters" (5.0–8.6) ░ */}
      <WordFlash text="Zu Beginn" at={f(4.9)} life={34} cx={960} cy={220} size={80} disp={false} italic />
      <ObjectBurst src="telegraph.png" at={f(5.2)} life={34} cx={520} cy={580} w={420} dir="l" rot={-4} />
      <ObjectBurst src="insulator.png" at={f(5.8)} life={30} cx={1400} cy={520} w={200} dir="r" rot={8} />
      <ObjectBurst src="inkwell.png" at={f(6.3)} life={30} cx={910} cy={360} w={180} dir="u" rot={-6} />
      <ObjectBurst src="plate.png" at={f(6.8)} life={34} cx={980} cy={660} w={300} dir="d" rot={-5} />
      <WordFlash text="des Eisenbahn­zeitalters" at={f(7.3)} life={46} cx={960} cy={885} size={58} disp={false} />
      <ObjectBurst src="whistle.png" at={f(7.6)} life={34} cx={1280} cy={600} w={150} dir="u" rot={10} />
      <AccentBlock x={0} y={770} w={90} h={120} color={COLORS.olive} delay={f(5.0)} />
      <Tick at={f(6.1)} x={1660} y={300} />

      {/* ░ D · "Im 19. Jh — nicht irgendein Verkehrsmittel" (8.4–13.3) ░ */}
      <WordFlash text="Im 19." at={f(8.4)} life={28} cx={680} cy={260} size={66} disp={false} italic />
      <ObjectBurst src="stagecoach.png" at={f(8.7)} life={62} cx={760} cy={690} w={640} dir="l" rot={-3} />
      <WordFlash text="Jahrhundert" at={f(9.0)} life={44} cx={1080} cy={330} size={112} />
      <WordFlash text="nicht irgendein" at={f(9.9)} life={40} cx={1180} cy={470} size={72} disp={false} italic />
      <WordFlash text="Verkehrsmittel." at={f(10.9)} life={56} cx={960} cy={250} size={104} disp={false} accent />
      <Tick at={f(10.7)} x={250} y={840} />

      <Audio src={staticFile('audio/vo.m4a')} startFrom={Math.round(START * FPS)} volume={1} />
    </AbsoluteFill>
  );
};
