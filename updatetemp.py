import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import imageio.v2 as imageio
import os
import time
from selenium.webdriver.common.by import By
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import re

timestamp = int(time.time())
def get_loc():
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'\(([\d.-]+),\s*([\d.-]+)\)', content)
        if match:
            lon = round(float(match.group(1)), 3)
            lat = round(float(match.group(2)), 3)
            return lon, lat
        return 116.38, 39.90  

lon, lat = get_loc()
html_content = f"""
<!DOCTYPE html>
<html>
    <style>
        html, body {{
          margin: 0;
          padding: 0;
          width: 100%;
          height: 100%;
          overflow: hidden; 
        }}
        iframe {{
          width: 100%;
          height: 100%;
          border: none;
        }}
      </style>
   <iframe src="https://earth.nullschool.net/#current/wind/surface/level/overlay=misery_index/patterson={lat},{lon},876/loc={lat},{lon}"></iframe>
</html>
"""
with open("temp.html", "w", encoding="utf-8") as f:
    f.write(html_content)


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1300,900') 

driver = webdriver.Chrome(options=chrome_options)
driver.get(f"file://{os.path.abspath('temp.html')}")
time.sleep(10)  


iframe = driver.find_element(By.TAG_NAME, "iframe")
driver.switch_to.frame(iframe)


os.makedirs("images", exist_ok=True)
frames = []

fps = 15  
frames_duration = 1
total_frames = frames_duration * fps  
gif_fps = 5

def capture_frame(i):
    screenshot = driver.get_screenshot_as_png()
    file_path = f"images/frame_{i}.png"
    with open(file_path, "wb") as f:
        f.write(screenshot)
    return file_path  


with ThreadPoolExecutor(max_workers=5) as executor:  
    futures = [executor.submit(capture_frame, i) for i in range(total_frames)]
    frames = [imageio.imread(f.result()) for f in futures] 


imageio.mimsave("images/demo.gif", frames, duration=1/gif_fps, loop=0, quantize=64)


with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(os.remove, [f"images/frame_{i}.png" for i in range(total_frames)])
os.remove("temp.html")

driver.quit()

with open("README.md", "r", encoding='utf-8') as file:
    content = file.read()

new_content = content.replace(
    "![temp](images/demo.gif)",
    f"![temp](images/demo.gif?{timestamp})"
)

with open("README.md", "w") as file:
    file.write(new_content)