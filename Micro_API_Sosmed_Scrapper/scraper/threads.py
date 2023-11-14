from flask import Flask, jsonify, request
from threads_interface import ThreadsInterface
import json
import os

app = Flask(__name__)
scraper = ThreadsInterface()
output_filename = "user_data.json"
update_interval_seconds = 300  # 5 minutes

def load_user_data():
    try:
        with open(output_filename, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {"data": {"mediaData": {"threads": []}}}

def save_user_data(user_data):
    with open(output_filename, "w") as json_file:
        json.dump(user_data, json_file, indent=4)

@app.route('/user_data', methods=['GET'])
def get_user_data():
    username = request.args.get('username', 'bekasi24jamcom')

    user_id = scraper.retrieve_user_id(username)
    user_data = scraper.retrieve_user_threads(user_id)

    # Muat data pengguna sebelumnya
    previous_user_data = load_user_data()

    # Perbarui data jika ada perbedaan
    if user_data != previous_user_data:
        # Gabungkan data baru dengan data yang ada tanpa duplikasi
        existing_ids = {thread["id"] for thread in previous_user_data["data"]["mediaData"]["threads"]}
        new_threads = [thread for thread in user_data["data"]["mediaData"]["threads"] if thread["id"] not in existing_ids]
        user_data["data"]["mediaData"]["threads"] = new_threads + previous_user_data["data"]["mediaData"]["threads"]

        # Simpan data yang telah di-update
        save_user_data(user_data)

        # Hitung jumlah data yang ada
        total_data = len(user_data["data"]["mediaData"]["threads"])

        return jsonify({"message": "New data detected. Data updated and saved.", "total_data": total_data, "data": user_data})
    else:
        # Hitung jumlah data yang ada
        total_data = len(previous_user_data["data"]["mediaData"]["threads"])

        return jsonify({"message": "No new data.", "total_data": total_data, "data": user_data})

@app.route('/user_data/json', methods=['GET'])
def get_user_data_json():
    user_data = load_user_data()

    # Dapatkan kata kunci pencarian dari parameter 'keyword'
    keyword = request.args.get('keyword', '')

    # Modifikasi data sebelum dikirim sebagai respons
    modified_data = []
    seen_titles = set()  # Untuk melacak judul yang sudah terlihat

    for thread in user_data["data"]["mediaData"]["threads"]:
        if thread["thread_items"] and thread["thread_items"][0]["post"]:
            post = thread["thread_items"][0]["post"]
            title = None

            text_post_app_info = post.get("text_post_app_info")
            if text_post_app_info and text_post_app_info.get("link_preview_attachment"):
                title = text_post_app_info["link_preview_attachment"].get("title")

            # Cek apakah judul sudah terlihat sebelumnya dan sesuai dengan kata kunci
            if title and title not in seen_titles and keyword.lower() in title.lower():
                modified_thread = {
                    "id": thread["id"],
                    "thread_items": []
                }
                modified_post = {
                    "username": post["user"].get("username") if post.get("user") else None,
                    "title": title,
                    "image_url": text_post_app_info["link_preview_attachment"].get("image_url"),
                    "url": text_post_app_info["link_preview_attachment"].get("url")
                }
                modified_thread["thread_items"].append({"post": modified_post})

                modified_data.append(modified_thread)
                seen_titles.add(title)

    # Hitung jumlah data yang ada
    total_data = len(modified_data)

    return jsonify({"total_data": total_data, "data": modified_data})

if __name__ == '__main__':
    app.run(debug=True)
