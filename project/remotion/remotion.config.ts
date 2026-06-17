import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// H.264, good quality for a fast-cut hook. CRF lower = better quality.
Config.setCodec('h264');
Config.setCrf(18);
// The remote env routes HTTPS through a TLS-inspecting proxy whose CA the
// bundled Chromium does not trust; without this, loading Google Fonts (and any
// remote asset) fails with ERR_CERT_AUTHORITY_INVALID.
Config.setChromiumIgnoreCertificateErrors(true);
