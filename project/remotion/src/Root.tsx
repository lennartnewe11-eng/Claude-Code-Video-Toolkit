import {Composition} from 'remotion';
import {loadFont} from '@remotion/google-fonts/Inter';
import {Hook} from './Hook';
import {StyleProof, PROOF_DURATION} from './StyleProof';
import {Chapter1, CH1_DURATION} from './Chapter1';
import {DURATION_IN_FRAMES, FPS, WIDTH, HEIGHT} from './timeline';

loadFont('normal', {
  weights: ['600', '800', '900'],
  subsets: ['latin'],
  ignoreTooManyRequestsWarning: true,
});

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Hook"
        component={Hook}
        durationInFrames={DURATION_IN_FRAMES}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="StyleProof"
        component={StyleProof}
        durationInFrames={PROOF_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Chapter1"
        component={Chapter1}
        durationInFrames={CH1_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
