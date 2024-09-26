from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# The cookie for Doc's session (retrieved from Doc's actual session or manually set)
DOC_SESSION_COOKIE = {
    'name': 'session',  # The name of the session cookie, e.g., "session" or "session_id"
    'value': 'doc_session_cookie_value',  # The actual session cookie value
    'domain': 'localhost',  # Domain where the cookie is valid
    'path': '/',  # Path for which the cookie is valid
    'httpOnly': True,  # If applicable
    'secure': False,  # Set to True if using HTTPS
}

# Set up Chrome options for headless browsing
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Start the ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Navigate to the site so that the cookie is accepted
driver.get("http://localhost:5000/")

# Add Doc's session cookie
driver.add_cookie(DOC_SESSION_COOKIE)

# Revisit the page where Doc's session is required, e.g., /secret
driver.get("http://localhost:5000/secret")

# Extract the page content or any cookie information (this will simulate Doc's session access)
try:
    page_source = driver.page_source
    print("[BOT] Page Source: ", page_source[:500])  # Print first 500 characters for brevity
    cookies = driver.get_cookies()  # Optionally retrieve all cookies
    print("[BOT] Cookies: ", cookies)
except Exception as e:
    print("[BOT] Error: ", e)

driver.quit()

