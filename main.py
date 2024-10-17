import json
import time
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def clean_text(text):
    """Cleans unwanted characters from the text."""
    return text.replace('\u2019', "'").strip()  # Replace unwanted character and strip whitespace

# Function to scrape data from the page
def scrape_to_json():
    # Set up Selenium with ChromeDriver in headless mode
    options = Options()
    options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    options.add_argument('--disable-gpu')  # Disable GPU acceleration (recommended for headless)
    options.add_argument('--no-sandbox')  # Bypass OS security model (required for some environments)
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems

    # Use webdriver-manager to automatically manage ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Navigate to the URL
    url = 'https://www.sotwe.com/hashtag/Uranium'
    driver.get(url)

    # Let the page load
    time.sleep(5)

    # Initialize a list to store scraped data
    scraped_posts = []

    # Scroll increment settings
    total_height = driver.execute_script("return document.body.scrollHeight")
    scroll_increment = total_height / 8  # Scroll down by 1/8 of the total height

    # Scroll and scrape loop
    while True:
        # Wait for post elements to be present
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'px-4')))

        # Find all post elements with class "px-4"
        post_elements = driver.find_elements(By.CLASS_NAME, 'px-4')

        # Find all image elements within "v-responsive__content"
        img_elements = driver.find_elements(By.CSS_SELECTOR, 'div.v-responsive__content img')

        # Find user IDs and post times using their respective XPaths
        user_id_elements = driver.find_elements(By.XPATH, '//*[@id="app"]/div/main/div/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/div[1]/div[1]')
        post_time_elements = driver.find_elements(By.XPATH, '//*[@id="app"]/div/main/div/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div/div[1]/div[2]')

        # Zip the text content, image sources, user IDs, and post times together
        for post, img, user_id, post_time in zip(post_elements, img_elements, user_id_elements, post_time_elements):
            content = clean_text(post.text)  # Clean text content
            image_src = img.get_attribute('src')  # Extract image source
            user_id_text = clean_text(user_id.text)  # Clean user ID text
            post_time_text = clean_text(post_time.text)  # Clean post time text
            
            scraped_posts.append({
                "content": content,
                "image_src": image_src,
                "user_id": user_id_text,
                "post_time": post_time_text
            })

        # Scroll down by the specified increment
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        
        # Wait for new content to load
        time.sleep(3)

        # Check if new content is loaded by comparing the length of post_elements
        new_post_elements = driver.find_elements(By.CLASS_NAME, 'px-4')
        if len(new_post_elements) <= len(post_elements):
            print("No new posts loaded, stopping.")
            break

    # Save the scraped data to a JSON file
    with open('scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump(scraped_posts, f, ensure_ascii=False, indent=4)

    print("Data scraped and saved to scraped_data.json")

    # Close the browser
    driver.quit()

@app.route('/scrape', methods=['GET'])
def scrape_and_download():
    try:
        scrape_to_json()
        return jsonify({"message": "Data scraped successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
