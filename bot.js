// bot.js
const puppeteer = require('puppeteer');

async function processMessage(message) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    // Simulate Doc's session (if needed, set cookies or login as Doc)
    await page.goto('http://localhost:5000/communicate');

    // Execute the script from the message
    const result = await page.evaluate(message);

    await browser.close();

    return result;
}

// Expose the function for bot to call
module.exports = processMessage;

