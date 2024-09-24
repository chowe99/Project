from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route('/process_message', methods=['POST'])
def process_message():
    # Set up Chrome options for headless browsing
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Start the ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Visit the /communicate page where Marty left the message
    driver.get("http://localhost:5000/communicate")

    # Simulate Doc's session by adding the correct session cookie
    driver.add_cookie({
        'name': 'session', 
        'value': 'doc_session=True',  # Ensure that Doc's session is active
        'path': '/'
    })

    # Revisit /communicate with Doc's session active
    driver.get("http://localhost:5000/communicate")
    
    # Extract the page content or any cookie information (this will simulate an XSS payload)
    try:
        page_source = driver.page_source
        cookies = driver.execute_script("return document.cookie;")
    except Exception as e:
        page_source = f"Error executing script: {e}"
    
    driver.quit()

    # Return the page content and Doc's cookie to simulate the XSS exploit
    return {
        'page_content': page_source,
        'doc_cookie': cookies
    }, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8070)

