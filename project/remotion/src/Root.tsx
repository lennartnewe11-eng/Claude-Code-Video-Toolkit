import {Composition} from 'remotion';
import {loadFont} from '@remotion/google-fonts/Inter';
import {Hook} from './Hook';
import {DURATION_IN_FRAMES, FPS, WIDTH, HEIGHT} from './timeline';

loadFont('normal', {
  weights: ['600', '800', '900'],
  subsets: ['latin'],
  ignoreTooManyRequestsWarning: true,
});

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Hook"
      component={Hook}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
