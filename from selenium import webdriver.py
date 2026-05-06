from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("測試開始...")
try:
    # 啟動最陽春的瀏覽器
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # 測試連線
    driver.get("https://www.google.com")
    print(f"目前網址: {driver.current_url}")
    
    time.sleep(5)
    driver.quit()
    print("測試成功！")
except Exception as e:
    print(f"測試失敗，原因: {e}")