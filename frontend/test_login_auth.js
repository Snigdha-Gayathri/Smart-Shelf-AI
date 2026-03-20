const puppeteer = require('puppeteer');

(async () => {
    // Wait for the server to spin up
    await new Promise(resolve => setTimeout(resolve, 8000));
    
    const browser = await puppeteer.launch({ headless: true });
    try {
        const page = await browser.newPage();
        
        // Setup console logs from browser page
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
        
        console.log("Page loaded");
        
        // Click on login to register
        await page.waitForSelector('.auth-card-register input[placeholder="Name"]', { visible: true });
        await page.type('.auth-card-register input[placeholder="Name"]', `Test User`);
        
        const timestamp = Date.now();
        const username = `test_delete_user_${timestamp}`;
        await page.type('.auth-card-register input[placeholder="Username"]', username);
        
        await page.type('.auth-card-register input[placeholder="Password"]', 'TestPass1!');
        
        console.log("Submitting registration");
        
        await page.click('.auth-card-register button.auth-btn-primary');
        
        // Wait for registration and auto-login
        await page.waitForSelector('.auth-card-login input[placeholder="Username"]', { visible: true });
        
        console.log("Registration complete. Logging in");
        // Form clears and populates login after 1.5s
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        await page.type('.auth-card-login input[placeholder="Password"]', 'TestPass1!');
        await page.click('.auth-card-login button.auth-btn-primary');
        
        // Wait for page reload after login success
        await page.waitForNavigation({ waitUntil: 'networkidle0' });
        
        const tokenToken = await page.evaluate(() => {
            const authStr = localStorage.getItem('auth');
            if (authStr) {
                const parsed = JSON.parse(authStr);
                return parsed.token;
            }
            return null;
        });
        
        if (!tokenToken) {
            console.error("Token missing in local storage after login");
        } else {
            console.log("Token successfully found in local storage:", tokenToken);
        }
        
    } catch (e) {
        console.error("Test error:", e);
    } finally {
        await browser.close();
    }
    
})();
