import {loadFont as loadDisplay} from '@remotion/google-fonts/PlayfairDisplay';
import {loadFont as loadBody} from '@remotion/google-fonts/PTSerif';

// Editorial collage palette — sampled directly from the reference video.
export const COLORS = {
  paper: '#EFECE0',
  ink: '#1a1714',
  inkSoft: '#6b6560',
  olive: '#3D4C41',
  taupe: '#D4CEB9',
  accent: '#8c2f1f', // muted oxblood for emphasis
};

export const display = loadDisplay('normal', {
  weights: ['700', '800', '900'],
  subsets: ['latin'],
  ignoreTooManyRequestsWarning: true,
}).fontFamily;

export const body = loadBody('normal', {
  weights: ['400', '700'],
  subsets: ['latin'],
  ignoreTooManyRequestsWarning: true,
}).fontFamily;

loadBody('italic', {
  weights: ['400', '700'],
  subsets: ['latin'],
  ignoreTooManyRequestsWarning: true,
});

// Soft collage drop shadow used on every cut-out.
export const CUTOUT_SHADOW =
  'drop-shadow(10px 16px 10px rgba(20,16,10,0.30))';
