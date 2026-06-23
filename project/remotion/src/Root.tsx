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
import {Ch2P8Ev, C2P8_DURATION} from './Ch2P8Ev';
import {Ch2P9Ev, C2P9_DURATION} from './Ch2P9Ev';
import {Ch3P1Ev, C3P1_DURATION} from './Ch3P1Ev';
import {Ch3P2Ev, C3P2_DURATION} from './Ch3P2Ev';
import {Ch3P3Ev, C3P3_DURATION} from './Ch3P3Ev';
import {Ch3P4Ev, C3P4_DURATION} from './Ch3P4Ev';
import {Ch3P5Ev, C3P5_DURATION} from './Ch3P5Ev';
import {Ch3P6Ev, C3P6_DURATION} from './Ch3P6Ev';
import {Ch3P7Ev, C3P7_DURATION} from './Ch3P7Ev';
import {Ch3P8Ev, C3P8_DURATION} from './Ch3P8Ev';
import {Ch3P9Ev, C3P9_DURATION} from './Ch3P9Ev';
import {Ch3P10Ev, C3P10_DURATION} from './Ch3P10Ev';
import {Ch3P11Ev, C3P11_DURATION} from './Ch3P11Ev';
import {Ch3P12Ev, C3P12_DURATION} from './Ch3P12Ev';
import {Ch3P13Ev, C3P13_DURATION} from './Ch3P13Ev';
import {Ch3P14Ev, C3P14_DURATION} from './Ch3P14Ev';
import {Ch3P15Ev, C3P15_DURATION} from './Ch3P15Ev';
import {Ch3P16Ev, C3P16_DURATION} from './Ch3P16Ev';
import {Ch3P17Ev, C3P17_DURATION} from './Ch3P17Ev';
import {Ch3P18Ev, C3P18_DURATION} from './Ch3P18Ev';
import {FazitEv, FAZIT_DURATION} from './FazitEv';
import {ThumbEv} from './ThumbEv';
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
      <Composition id="Ch2P8Ev" component={Ch2P8Ev} durationInFrames={C2P8_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch2P9Ev" component={Ch2P9Ev} durationInFrames={C2P9_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P1Ev" component={Ch3P1Ev} durationInFrames={C3P1_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P2Ev" component={Ch3P2Ev} durationInFrames={C3P2_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P3Ev" component={Ch3P3Ev} durationInFrames={C3P3_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P4Ev" component={Ch3P4Ev} durationInFrames={C3P4_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P5Ev" component={Ch3P5Ev} durationInFrames={C3P5_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P6Ev" component={Ch3P6Ev} durationInFrames={C3P6_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P7Ev" component={Ch3P7Ev} durationInFrames={C3P7_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P8Ev" component={Ch3P8Ev} durationInFrames={C3P8_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P9Ev" component={Ch3P9Ev} durationInFrames={C3P9_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P10Ev" component={Ch3P10Ev} durationInFrames={C3P10_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P11Ev" component={Ch3P11Ev} durationInFrames={C3P11_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P12Ev" component={Ch3P12Ev} durationInFrames={C3P12_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P13Ev" component={Ch3P13Ev} durationInFrames={C3P13_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P14Ev" component={Ch3P14Ev} durationInFrames={C3P14_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P15Ev" component={Ch3P15Ev} durationInFrames={C3P15_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P16Ev" component={Ch3P16Ev} durationInFrames={C3P16_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P17Ev" component={Ch3P17Ev} durationInFrames={C3P17_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="Ch3P18Ev" component={Ch3P18Ev} durationInFrames={C3P18_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="FazitEv" component={FazitEv} durationInFrames={FAZIT_DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
      <Composition id="ThumbEv" component={ThumbEv} durationInFrames={1} fps={FPS} width={WIDTH} height={HEIGHT} />
    </>
  );
};
