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
import {Ch2P2Ev, C2P2_DURATION} from './Ch2P2Ev';
import {Ch2P3Ev, C2P3_DURATION} from './Ch2P3Ev';
import {Ch2P4Ev, C2P4_DURATION} from './Ch2P4Ev';
import {Ch2P5Ev, C2P5_DURATION} from './Ch2P5Ev';
import {Ch2P6Ev, C2P6_DURATION} from './Ch2P6Ev';
import {Ch2P7Ev, C2P7_DURATION} from './Ch2P7Ev';
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
      <Composition
        id="Ch2P2Ev"
        component={Ch2P2Ev}
        durationInFrames={C2P2_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition id="Ch2P3Ev" component={Ch2P3Ev} durationInFrames={C2P3_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch2P4Ev" component={Ch2P4Ev} durationInFrames={C2P4_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch2P5Ev" component={Ch2P5Ev} durationInFrames={C2P5_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch2P6Ev" component={Ch2P6Ev} durationInFrames={C2P6_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch2P7Ev" component={Ch2P7Ev} durationInFrames={C2P7_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
    </>
  );
};
