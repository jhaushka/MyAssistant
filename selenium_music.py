from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Music:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--enable-unsafe-swiftshader")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def play_music(self, query):
        try:
            # Open YouTube search results page
            self.driver.get("https://www.youtube.com/results?search_query=" + query)
            
            # Wait for the first video to be clickable and then click to play
            video = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "video-title"))
            )
            video.click()
            print(f"Playing: {query}")
            input("Press Enter to stop...")
           
        except Exception as e:
            print("An error occurred:", e)
        finally:
            self.driver.quit()

    def search_music(self, query):
        try:
            # Open YouTube search results page without playing
            self.driver.get("https://www.youtube.com/results?search_query=" + query)
            print("Search results are now displayed. Press 'Enter' to close the browser.")
            input("Press 'Enter' to exit...")  
        except Exception as e:
            print("An error occurred:", e)
        finally:
            self.driver.quit()

# # Main loop for interaction
# assist = Music()
# assist.play_music("khamoshiyan")
if __name__ == "__main__":
    assist = Music()
    assist.play_music("khamoshiyan")

