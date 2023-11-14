import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Fungsi untuk scrape halaman tertentu
def scrape_page(driver):
    # Inisialisasi list untuk data
    data = []

    # Get the div with id "ds" and class "form-body"
    ds_div = driver.find_element(By.CSS_SELECTOR, "#ds .form-body")

    # Get all elements with class "col-md-10 align-left"
    elements_10 = ds_div.find_elements(By.CSS_SELECTOR, ".col-md-10.align-left")
    elements_6 = ds_div.find_elements(By.CSS_SELECTOR, ".col-md-6.align-left")

    for element_10, element_6 in zip(elements_10, elements_6):
        h2 = element_10.find_element(By.TAG_NAME, "h2")
        title = h2.text
        # Ambil tautan dari elemen <a> dalam elemen <h2>
        link = h2.find_element(By.TAG_NAME, "a").get_attribute("href")
        paragraph = element_10.find_element(By.TAG_NAME, "p").text
        text = element_6.text
        data.append({"title": title, "link": link, "paragraph": paragraph, "text": text})

    return data

# Fungsi untuk berpindah ke halaman berikutnya
def next_page(driver):
    # Implementasikan cara berpindah ke halaman berikutnya di sini
    pass

def scrape_and_update():
    while True:
        # Menggunakan ChromeDriverManager untuk mengelola driver
        driver_path = ChromeDriverManager().install()
        options = Options()
        options.add_argument("--disable-notifications")  # Untuk menonaktifkan notifikasi pop-up
        options.add_argument("--headless")  # Jalankan headless (tanpa tampilan GUI)

        # Inisialisasi objek service
        service = ChromeService(executable_path=driver_path)

        # Inisialisasi WebDriver dengan objek service dan opsi
        driver = webdriver.Chrome(service=service, options=options)

        url = "https://projects.co.id/public/browse_projects/listing"
        driver.get(url)

        # Wait for the content to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "ds")))

        # Inisialisasi list untuk semua data dari beberapa halaman
        all_data = []

        # Scrape halaman pertama
        data = scrape_page(driver)
        all_data.extend(data)

        # Lakukan loop untuk 10 halaman
        for page in range(2, 12):  # Scrap halaman 2 hingga 11
            next_page(driver)  # Pindah ke halaman berikutnya
            data = scrape_page(driver)  # Scrap halaman saat ini
            all_data.extend(data)  # Tambahkan data ke list semua data

        # Close the WebDriver
        driver.quit()

        # Simpan data ke file JSON
        with open("projects_data.json", "w") as json_file:
            json.dump(all_data, json_file, indent=4)

        time.sleep(3600)  # Tunggu 1 jam sebelum mengupdate kembali

if __name__ == "__main__":
    scrape_and_update()
