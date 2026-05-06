import pandas as pd
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

download_dir = r'C:\Users\Terry_Chang\Desktop\教育訓練\PY\pdf'
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

excel_path = r'C:\Users\Terry_Chang\Desktop\教育訓練\PY\trigger file.xlsx'
df = pd.read_excel(excel_path)
todo_list = df[(df["下載狀態"].isna()) | (df['下載狀態'] == '失敗')].copy()

chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_setting_values.automatic_downloads": 1 
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    for index, row in todo_list.iterrows():
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.switch_to.default_content()

        company_id = str(row['公司代號'])
        year = str(row['年度'])
        url_key = str(row['URL'])
        target_file_key = str(row['電子檔案'])
        
        print(f"啟動任務 公司：{company_id} | 模式：{url_key}")

        if 't100sb02_1' in url_key:
            driver.get('https://mops.twse.com.tw/mops/#/web/t100sb02_1')
            time.sleep(random.uniform(4.0, 6.0))
            
            year_input = wait.until(EC.presence_of_element_located((By.ID, "year")))
            year_input.clear(); year_input.send_keys(year)
            id_input = driver.find_element(By.ID, "co_id")
            id_input.clear(); id_input.send_keys(company_id)
            
            search_btn = driver.find_element(By.ID, "searchBtn")
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(random.uniform(7.0, 9.0))

        elif 't57sb01_q5' in url_key:
            driver.get('https://mops.twse.com.tw/mops/#/web/t57sb01_q5')
            time.sleep(5)
            
            wait.until(EC.presence_of_element_located((By.ID, "year"))).send_keys(year)
            driver.find_element(By.ID, "co_id").send_keys(company_id)
            driver.execute_script("document.getElementById('searchBtn').click();")
            time.sleep(8)

        else:
            driver.get('https://mops.twse.com.tw/mops/web/index')
            time.sleep(3)
            driver.execute_script(f"""
                var links = document.querySelectorAll('a');
                for (var i = 0; i < links.length; i++) {{
                    if (links[i].href.includes('{url_key}')) {{ links[i].click(); break; }}
                }}
            """)
            time.sleep(4)
            if len(driver.find_elements(By.TAG_NAME, "iframe")) > 0:
                driver.switch_to.frame(0)
            
            wait.until(EC.presence_of_element_located((By.ID, "companyId"))).send_keys(company_id)
            wait.until(EC.presence_of_element_located((By.ID, "year"))).send_keys(year)
            driver.execute_script("document.getElementById('searchBtn').click();")
            time.sleep(6)

        if len(driver.window_handles) > 1:
            main_h = driver.window_handles[0]
            res_h = driver.window_handles[1]
            driver.switch_to.window(main_h); driver.close()
            driver.switch_to.window(res_h)
            print(f"已切換至結果分頁")
            time.sleep(5)

        if 't100sb02_1' not in url_key:
            try:
                driver.switch_to.default_content()
                if len(driver.find_elements(By.TAG_NAME, "iframe")) > 0: driver.switch_to.frame(0)
                
                detail_xpath = "//input[contains(@src, 't56sf26.gif')] | //img[contains(@src, 't56sf26.gif')]"
                detail_btn = wait.until(EC.element_to_be_clickable((By.XPATH, detail_xpath)))
                
                curr_h_list = driver.window_handles
                driver.execute_script("arguments[0].click();", detail_btn)
                time.sleep(5)
                
                if len(driver.window_handles) > len(curr_h_list):
                    driver.switch_to.window(driver.window_handles[0]); driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    print("已進入最終清單頁")
            except:
                print("提示：此頁面無詳細資料按鈕，直接掃描")

        driver.switch_to.default_content()
        if len(driver.find_elements(By.TAG_NAME, "iframe")) > 0: driver.switch_to.frame(0)

        all_links = driver.find_elements(By.XPATH, f"//a[contains(., '{target_file_key}')]")
        unique_texts = list(dict.fromkeys([lnk.text.strip() for lnk in all_links if lnk.text.strip()]))
        
        print(f"找到 {len(unique_texts)} 個唯一檔案")

        for text in unique_texts:
            list_window = driver.current_window_handle
            try:
                print(f"下載中：{text}")
                driver.switch_to.default_content()
                if len(driver.find_elements(By.TAG_NAME, "iframe")) > 0: driver.switch_to.frame(0)
                
                target_lnk = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, text)))
                driver.execute_script("arguments[0].click();", target_lnk)
                time.sleep(5)
                
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    try:
                        pdf_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/pdf/')]")))
                        pdf_btn.click()
                        time.sleep(random.uniform(5, 8))
                    except:
                        pass
                    driver.close()
                    driver.switch_to.window(list_window)
                else:
                    time.sleep(random.uniform(4, 6))

            except Exception as e:
                print(f"子檔案下載失敗: {e}")
                while len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    if driver.current_window_handle != list_window: driver.close()
                driver.switch_to.window(list_window)

        print(f"{company_id} 處理結束")

except Exception as e:
    print(f"系統嚴重異常：{e}")
finally:
    print(f"結束 下載目錄：{download_dir}")
