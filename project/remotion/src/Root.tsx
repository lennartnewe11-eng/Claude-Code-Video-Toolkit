import {Composition} from 'remotion';
import {loadFont} from '@remotion/google-fonts/Inter';
import {Hook} from './Hook';
import {StyleProof, PROOF_DURATION} from './StyleProof';
import {Chapter1, CH1_DURATION} from './Chapter1';
import {Ch1P1, P1_DURATION} from './Ch1P1';
import {Ch1P1Ev, P1EV_DURATION} from './Ch1P1Ev';
import {Ch1P2Ev, P2EV_DURATION} from './Ch1P2Ev';
import {Ch1P3Ev, P3EV_DURATION} from './Ch1P3Ev';
import {Ch1P4Ev, P4EV_DURATION} from './Ch1P4Ev';
import {Ch1P5Ev, P5EV_DURATION} from './Ch1P5Ev';
import {Ch1P6Ev, P6EV_DURATION} from './Ch1P6Ev';
import {Ch2P1Ev, C2P1_DURATION} from './Ch2P1Ev';
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
      <Composition
        id="Ch1P1"
        component={Ch1P1}
        durationInFrames={P1_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Ch1P1Ev"
        component={Ch1P1Ev}
        durationInFrames={P1EV_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Ch1P2Ev"
        component={Ch1P2Ev}
        durationInFrames={P2EV_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Ch1P3Ev"
        component={Ch1P3Ev}
        durationInFrames={P3EV_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Ch1P4Ev"
        component={Ch1P4Ev}
        durationInFrames={P4EV_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Ch1P5Ev"
        component={Ch1P5Ev}
        durationInFrames={P5EV_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Ch1P6Ev"
        component={Ch1P6Ev}
        durationInFrames={P6EV_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Ch2P1Ev"
        component={Ch2P1Ev}
        durationInFrames={C2P1_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
