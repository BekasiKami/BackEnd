Berikut adalah contoh README.md dan dokumentasi Postman:

Twitter Scraper API
Twitter Scraper API adalah aplikasi Flask yang digunakan untuk melakukan web scraping pada data Twitter dan menyimpannya dalam format JSON.

Instalasi
Clone repositori ini.
Install dependencies menggunakan pip:
pip install -r requirements.txt
Jalankan aplikasi:
python app_main.py
API Endpoints
POST /api/scrape_tweets
Memulai proses scraping tweets.

Request Parameters
max_tweets (optional): Jumlah maksimum tweets yang akan di-scrape.
scrape_username (optional): Username Twitter yang akan di-scrape.
scrape_hashtag (optional): Hashtag yang akan di-scrape.
scrape_query (optional): Query pencarian yang akan di-scrape.
scrape_latest (optional): Jika disetel ke "true", akan mengambil tweets terbaru.
scrape_top (optional): Jika disetel ke "true", akan mengambil tweets paling populer.
scrape_poster_details (optional): Jika disetel ke "pd", akan mengambil detail poster.
Response
Jika scraping berhasil, akan mengembalikan pesan sukses dan menyimpan hasil scraping ke dalam file 'scraped_tweets.json'.
Jika terjadi kesalahan, akan mengembalikan pesan error dan status kesalahan.
GET /api/scraped_tweets
Mendapatkan hasil scraping tweets yang telah disimpan dalam file 'scraped_tweets.json'.

Response
Mengembalikan JSON yang berisi hasil scraping tweets.
Jika terjadi kesalahan saat membaca file, akan mengembalikan pesan error dan status kesalahan.
GET /user_data
Mendapatkan data pengguna berdasarkan username.

Request Parameters
username (optional): Username Twitter yang akan diambil datanya. Jika tidak disediakan, akan menggunakan 'bekasi24jamcom' sebagai default.
Response
Mengembalikan JSON yang berisi data pengguna.
Jika terdapat data baru, akan mengupdate dan menyimpan data tersebut.
Jika tidak ada data baru, akan mengembalikan data yang ada.
GET /user_data/json
Mendapatkan data pengguna dalam format JSON berdasarkan kata kunci pencarian.

Request Parameters
keyword (optional): Kata kunci pencarian. Jika tidak disediakan, akan mengembalikan semua data.
Response
Mengembalikan JSON yang berisi data pengguna yang sesuai dengan kata kunci pencarian.
Jika terjadi kesalahan, akan mengembalikan pesan error dan status kesalahan.
Postman Documentation
Anda dapat mengimpor koleksi Postman berikut untuk menguji API ini:

Run in Postman

Ganti your-collection-id dengan ID koleksi Postman Anda. Anda dapat membuat dokumentasi Postman Anda sendiri dengan mengikuti panduan ini.