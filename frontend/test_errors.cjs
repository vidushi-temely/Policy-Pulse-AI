const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  page.on('requestfailed', request => console.log('REQUEST FAILED:', request.url(), request.failure().errorText));

  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2' });
  
  // Wait a bit
  await new Promise(r => setTimeout(r, 2000));
  
  // Click tabs to trigger errors
  const tabs = await page.$$('.tab-btn');
  if (tabs.length > 2) {
      await tabs[1].click();
      await new Promise(r => setTimeout(r, 1000));
      await tabs[2].click();
      await new Promise(r => setTimeout(r, 1000));
  }
  
  await browser.close();
})();
