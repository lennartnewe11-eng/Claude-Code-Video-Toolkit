import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';
import {PaperBackground} from './style/PaperBackground';
import {Cutout} from './style/Cutout';
import {CutoutVideo} from './style/CutoutVideo';
import {EditorialText, Token} from './style/EditorialText';
import {AccentBlock, Kicker, Rule, PhotoCard} from './style/Bits';
import {COLORS} from './style/theme';

export const PROOF_DURATION = Math.round(12 * FPS);
const VO_START = Math.round(52.46 * FPS);

// Transition (train wipe) timing
const TRANS_START = 92;
const TRANS_LEN = 52;
const SWAP = 118; // where scene A hands over to scene B (train covers centre)

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

const Group: React.FC<{show: [number, number]; children: React.ReactNode}> = ({show, children}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame,
    [show[0], show[0] + 8, show[1] - 10, show[1]],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

export const StyleProof: React.FC = () => {
  return (
    <AbsoluteFill>
      <PaperBackground />

      {/* persistent furniture */}
      <AccentBlock x={0} y={120} w={70} h={150} color={COLORS.olive} delay={2} />
      <Kicker text="Kapitel 1 · Das goldene Zeitalter" x={120} y={120} delay={4} />
      <Rule x={120} y={172} w={520} delay={10} />

      {/* ===== SCENE A — "1869 / transkontinentale Eisenbahn" ===== */}
      <Group show={[0, SWAP + 10]}>
        <PhotoCard src="map1871.jpg" cx={1430} cy={560} width={680} rotate={-3} delay={10} sepia />
        <Cutout src="loco.png" cx={540} cy={830} width={560} entrance="drive" delay={18} rotate={-2} />
        <EditorialText
          tokens={[{t: '1869', display: true, size: 300}]}
          cx={360} cy={470} width={760} align="left"
        />
        <EditorialText
          tokens={captionA} cx={770} cy={250} width={920} baseSize={50} align="left" delay={10}
        />
      </Group>

      {/* ===== SCENE B — "Tage statt Monate / Planwagen" ===== */}
      <Group show={[SWAP, PROOF_DURATION]}>
        <AbsoluteFill
          style={{
            background:
              'radial-gradient(ellipse 540px 360px at 470px 470px, rgba(239,236,224,0.92) 0%, rgba(239,236,224,0.0) 100%)',
          }}
        />
        <Cutout src="wagon.png" cx={1380} cy={770} width={420} entrance="drop" delay={SWAP + 8} rotate={4} />
        <EditorialText
          tokens={stackB} cx={470} cy={450} width={720} baseSize={48} align="center" delay={SWAP + 6} stagger={3}
        />
      </Group>

      {/* ===== TRANSITION — the steam train rushes across (wipe) ===== */}
      <Sequence from={TRANS_START} durationInFrames={TRANS_LEN + 6} name="train-wipe" layout="none">
        <CutoutVideo
          src="train_pass.webm"
          fromX={-2600}
          toX={2600}
          y={560}
          width={3200}
          durationFrames={TRANS_LEN}
          rotate={-1}
        />
      </Sequence>

      {/* voiceover + soft music bed */}
      <Audio src={staticFile('audio/vo.m4a')} startFrom={VO_START} volume={1} />
      <Audio src={staticFile('audio/musicBed.mp3')} startFrom={Math.round(20 * FPS)} volume={0.1} />
    </AbsoluteFill>
  );
};
