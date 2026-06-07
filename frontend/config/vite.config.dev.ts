import { mergeConfig } from 'vite';
import baseConfig from './vite.config.base';

export default mergeConfig(
  {
    mode: 'development',
    server: {
      host: '0.0.0.0',
      port: 5173,
      open: true,
      fs: {
        strict: true,
      },
    },
  },
  baseConfig
);
