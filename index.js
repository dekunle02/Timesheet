const puppeteer = require('puppeteer');
const path = require('path');

const OUT_FILE_NAME = 'timesheet'
const OUT_HTML = `file:${path.join(__dirname, 'out', OUT_FILE_NAME + '.html')}`
const OUT_PNG = './out/' + OUT_FILE_NAME + '.png'


  async function main() {
    const browser = await puppeteer.launch({
      headless: true,
      ignoreHTTPSErrors: true,
      args: [`--window-size=1366,900`],
      defaultViewport: {
        width: 1366,
        height: 900
      }
    });
    const page =
    await browser.newPage();
    await page.goto(OUT_HTML);
    await page.screenshot({ path: OUT_PNG });
    await browser.close();


  }

main()