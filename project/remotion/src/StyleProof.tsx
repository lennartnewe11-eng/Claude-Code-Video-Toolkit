import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {PaperBackground} from './style/PaperBackground';
import {Cutout} from './style/Cutout';
import {EditorialText, Token} from './style/EditorialText';
import {AccentBlock, Kicker, Rule, PhotoCard} from './style/Bits';
import {COLORS} from './style/theme';

export const PROOF_DURATION = Math.round(12 * FPS);
const VO_START = Math.round(52.46 * FPS); // beat begins here in the full VO

const captionA: Token[] = [
  {t: 'die'}, {t: 'erste'},
  {t: 'transkontinentale', w: 'boldItalic'},
  {t: 'Eisenbahn', br: true},
  {t: 'fertiggestellt.'},
];

const stackB: Token[] = [
  {t: 'was', w: 'reg'}, {t: 'vorher', w: 'reg', br: true},
  {t: 'MONATE', display: true, size: 150, br: true},
  {t: 'im', w: 'reg'}, {t: 'Planwagen', w: 'bold'}, {t: 'dauerte', w: 'reg', br: true},
  {t: '—', w: 'reg'}, {t: 'nun', w: 'reg'}, {t: 'nur', w: 'reg'}, {t: 'noch', w: 'reg', br: true},
  {t: 'TAGE', display: true, size: 150, accent: true},
];

const Group: React.FC<{
  show: [number, number]; // [fadeInStart, fadeOutEnd] in frames
  children: React.ReactNode;
}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame,
    [show[0], show[0] + 8, show[1] - 12, show[1]],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

export const StyleProof: React.FC = () => {
  return (
    <AbsoluteFill>
      <PaperBackground />

      {/* persistent design furniture */}
      <AccentBlock x={0} y={120} w={70} h={150} color={COLORS.olive} delay={2} />
      <Kicker text="Kapitel 1 · Das goldene Zeitalter" x={120} y={120} delay={4} />
      <Rule x={120} y={172} w={520} delay={10} />

      {/* vintage railroad map as a paper card, right side */}
      <PhotoCard src="map1871.jpg" cx={1430} cy={560} width={680} rotate={-3} delay={10} sepia />

      {/* the Jupiter — the actual 1869 Golden Spike locomotive */}
      <Cutout src="loco.png" cx={520} cy={860} width={600} entrance="drive" delay={16} rotate={-2} />

      {/* SCENE A — "1869 ... transkontinentale Eisenbahn" */}
      <Group show={[0, 122]}>
        <EditorialText
          tokens={[{t: '1869', display: true, size: 300}]}
          cx={360}
          cy={470}
          width={760}
          align="left"
        />
        <EditorialText
          tokens={captionA}
          cx={760}
          cy={250}
          width={900}
          baseSize={50}
          align="left"
          delay={10}
        />
      </Group>

      {/* SCENE B — "Tage statt Monate / Planwagen" */}
      <Group show={[120, PROOF_DURATION]}>
        {/* soft paper wash to lift the text off the dark locomotive */}
        <AbsoluteFill
          style={{
            background:
              'radial-gradient(ellipse 540px 360px at 470px 470px, rgba(239,236,224,0.92) 0%, rgba(239,236,224,0.0) 100%)',
          }}
        />
        <Cutout src="wagon.png" cx={1380} cy={770} width={420} entrance="drop" delay={128} rotate={4} />
        <EditorialText
          tokens={stackB}
          cx={470}
          cy={450}
          width={720}
          baseSize={48}
          align="center"
          delay={126}
          stagger={3}
        />
      </Group>

      {/* voiceover for this beat + soft music bed */}
      <Audio src={staticFile('audio/vo.m4a')} startFrom={VO_START} volume={1} />
      <Audio src={staticFile('audio/musicBed.mp3')} startFrom={Math.round(20 * FPS)} volume={0.12} />
    </AbsoluteFill>
  );
};
