from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Fungsi untuk scrape halaman tertentu
def scrape_page(driver):
    data = []
    ds_div = driver.find_element(By.CSS_SELECTOR, "#ds .form-body")
    elements_10 = ds_div.find_elements(By.CSS_SELECTOR, ".col-md-10.align-left")
    elements_6 = ds_div.find_elements(By.CSS_SELECTOR, ".col-md-6.align-left")

    for element_10, element_6 in zip(elements_10, elements_6):
        h2 = element_10.find_element(By.TAG_NAME, "h2")
        title = h2.text
        link = h2.find_element(By.TAG_NAME, "a").get_attribute("href")
        paragraph = element_10.find_element(By.TAG_NAME, "p").text
        text = element_6.text
        data.append({"title": title, "link": link, "paragraph": paragraph, "text": text})

    return data

# Fungsi untuk berpindah ke halaman berikutnya
def next_page(driver):
    # Implementasi berpindah ke halaman berikutnya di sini
    pass

@app.route('/scrape_projects', methods=['GET'])
def scrape_projects():
    try:
        driver_path = ChromeDriverManager().install()
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--headless")

        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        url = "https://projects.co.id/public/browse_projects/listing"
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "ds")))

        all_data = []
        data = scrape_page(driver)
        all_data.extend(data)

        for page in range(2, 12):
            next_page(driver)
            data = scrape_page(driver)
            all_data.extend(data)

        driver.quit()

        with open("projects_data.json", "w") as json_file:
            json.dump(all_data, json_file, indent=4)

        return jsonify({"message": "Scraping selesai, data tersimpan di 'projects_data.json'", "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == "__main__":
    app.run(debug=True)
