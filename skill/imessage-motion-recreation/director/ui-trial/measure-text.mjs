// Build in Chromium so the synchronous measurer uses the same font shaping as export.
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const require = createRequire(new URL('../../scripts/engines/package.json', import.meta.url));

export function chromiumPath() {
  return process.env.CHROME_PATH ?? require('playwright').chromium.executablePath();
}

export async function buildWithBrowserText(options) {
  const {build} = require('esbuild');
  const {chromium} = require('playwright');
  const bundle = await build({
    entryPoints: [fileURLToPath(new URL('../conversation.mjs', import.meta.url))],
    bundle: true,
    format: 'iife',
    globalName: 'ConversationKit',
    write: false,
  });
  const browser = await chromium.launch({executablePath: chromiumPath(), headless: true});
  try {
    const page = await browser.newPage();
    await page.addScriptTag({content: bundle.outputFiles[0].text});
    return await page.evaluate(options => {
      const context = document.createElement('canvas').getContext('2d');
      return globalThis.ConversationKit.buildConversation({
        ...options,
        measureText(value, {fontFamily, fontSize, fontWeight = 400}) {
          context.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
          return context.measureText(value).width;
        },
      });
    }, options);
  } finally {
    await browser.close();
  }
}
