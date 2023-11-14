from flask import Flask, request, jsonify
import os
import json
import glob
from twitter_scraper import Twitter_Scraper
from dotenv import load_dotenv
from threads_interface import ThreadsInterface
from collections import Counter
import re

app = Flask(__name__)

# Initialize Twitter_Scraper object for login
scraper = None
scraper2 = ThreadsInterface()

# Initialize ThreadsInterface object
threads_scraper = ThreadsInterface()

output_filename = "user_data.json"
update_interval_seconds = 300  # 5 minutes

def login_to_twitter():
    global scraper
    user_uname = os.getenv("TWITTER_USERNAME")
    user_password = os.getenv("TWITTER_PASSWORD")

    if user_uname is None or user_password is None:
        return {"error": "Twitter username or password not found. Cannot login.", "success": False}, 400

    try:
        scraper = Twitter_Scraper(
            username=user_uname,
            password=user_password,
        )
        scraper.login()
    except Exception as e:
        return {"error": f"Error logging in to Twitter: {str(e)}", "success": False}, 500

def merge_scraped_data(scraped_data):
    existing_data = []

    # Try to open existing JSON file
    try:
        with open('scraped_tweets.json', 'r') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        pass  # JSON file does not exist yet

    # Merge new data with existing data
    for tweet in scraped_data:
        if tweet not in existing_data:
            existing_data.append(tweet)

    return existing_data

def merge_all_json_files():
    # Get list of all JSON files
    json_files = glob.glob('*.json')

    merged_data = []

    # Iterate over all files
    for file in json_files:
        # Open each file
        with open(file) as f:
            # Load JSON data from file
            data = json.load(f)
            # Append data to merged_data
            merged_data.append(data)

    # Write merged data to new JSON file
    with open('merged_data.json', 'w') as f:
        json.dump(merged_data, f, indent=4)

def load_user_data():
    try:
        with open(output_filename, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {"data": {"mediaData": {"threads": []}}}

def save_user_data(user_data):
    with open(output_filename, "w") as json_file:
        json.dump(user_data, json_file, indent=4)

def count_words_occurrences(json_file, words):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract all words from the tweets
    words_in_tweets = []
    for tweet in data:
        if 'text' in tweet:
            words_in_tweets.extend(re.findall(r'\w+', tweet['text'].lower()))  # Find all words in each tweet

    # Count occurrences of each word
    word_counts = Counter(words_in_tweets)

    # Get counts for the specified words
    word_counts = {word: word_counts.get(word, 0) for word in words}

    # Sort words by count, in descending order
    word_counts = dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))

    return word_counts


@app.route('/api/scrape_tweets', methods=['POST'])
def scrape_tweets_api():
    global scraper

    if scraper is None or not scraper.is_logged_in():
        login_response = login_to_twitter()
        if not login_response["success"]:
            return login_response

    # Get parameters from POST request
    max_tweets = request.form.get("max_tweets")
    username = request.form.get("scrape_username")
    hashtag = request.form.get("scrape_hashtag")
    query = request.form.get("scrape_query")
    latest = request.form.get("scrape_latest")
    top = request.form.get("scrape_top")
    poster_details = request.form.get("scrape_poster_details")

    # Check if parameters are "true" for latest and top
    latest = latest == "true" if latest else False
    top = top == "true" if top else False
    poster_details = poster_details.lower() == "pd" if poster_details else False

    # Scrape tweets with appropriate parameters
    max_tweets = int(max_tweets) if max_tweets else None

    params = {
        "max_tweets": max_tweets,
        "scrape_username": username,
        "scrape_hashtag": hashtag,
        "scrape_query": query,
        "scrape_latest": latest,
        "scrape_top": top,
        "scrape_poster_details": poster_details
    }

    try:
        scraper.scrape_tweets(**{k: v for k, v in params.items() if v is not None})
    except Exception as e:
        return {"error": f"Error scraping tweets: {str(e)}", "success": False}, 500

    # Get scraped results
    scraped_result = scraper.get_tweets()

    if scraped_result:
        # Merge new data with existing data in JSON file
        merged_data = merge_scraped_data(scraped_result)
        try:
            with open('scraped_tweets.json', 'w') as json_file:
                json.dump(merged_data, json_file, indent=4)
        except Exception as e:
            return {"error": f"Error saving scraped tweets: {str(e)}", "success": False}, 500

        # Merge all JSON files
        merge_all_json_files()

        return {"message": "Scraping completed, results saved in 'scraped_tweets.json'", "success": True}
    else:
        return {"error": "No scraped results to save.", "success": False}, 400

@app.route('/api/scraped_tweets', methods=['GET'])
def get_scraped_tweets():
    keyword = request.args.get('keyword', None)

    try:
        # Read JSON file containing scraped results
        with open('scraped_tweets.json', 'r') as json_file:
            scraped_tweets = json.load(json_file)

        if keyword:
            # Filter tweets based on the keyword
            filtered_tweets = [tweet for tweet in scraped_tweets if keyword.lower() in tweet['text'].lower()]
            return jsonify(filtered_tweets)

        return jsonify(scraped_tweets)
    except Exception as e:
        return {"error": f"Error reading scraped tweets: {str(e)}", "success": False}, 500

@app.route('/api/count_words', methods=['POST'])
def count_words_api():
    # Get words from POST request
    words = request.json.get("words")
    if not words:
        return {"error": "No words provided.", "success": False}, 400

    # Count occurrences of each word
    word_counts = count_words_occurrences('scraped_tweets.json', words)

    if not word_counts:
        return {"message": "No occurrences found for the provided words.", "success": True}, 200

    return jsonify(word_counts)
    
@app.route('/user_data', methods=['GET'])
def get_user_data():
    username = request.args.get('username', 'bekasi24jamcom')

    user_id = scraper2.retrieve_user_id(username)
    user_data = scraper2.retrieve_user_threads(user_id)

    # Load previous user data
    previous_user_data = load_user_data()

    # Update data if there are differences
    if user_data != previous_user_data:
        # Merge new data with existing data without duplicates
        existing_ids = {thread["id"] for thread in previous_user_data["data"]["mediaData"]["threads"]}
        new_threads = [thread for thread in user_data["data"]["mediaData"]["threads"] if thread["id"] not in existing_ids]
        user_data["data"]["mediaData"]["threads"] = new_threads + previous_user_data["data"]["mediaData"]["threads"]

        # Save updated data
        save_user_data(user_data)

        # Count the amount of data
        total_data = len(user_data["data"]["mediaData"]["threads"])

        return jsonify({"message": "New data detected. Data updated and saved.", "total_data": total_data, "data": user_data})
    else:
        # Count the amount of data
        total_data = len(previous_user_data["data"]["mediaData"]["threads"])

        return jsonify({"message": "No new data.", "total_data": total_data, "data": user_data})

@app.route('/user_data/json', methods=['GET'])
def get_user_data_json():
    user_data = load_user_data()

    # Get search keyword from 'keyword' parameter
    keyword = request.args.get('keyword', '')

    # Modify data before sending as response
    modified_data = []
    seen_titles = set()  # To track titles that have been seen

    for thread in user_data["data"]["mediaData"]["threads"]:
        if thread["thread_items"] and thread["thread_items"][0]["post"]:
            post = thread["thread_items"][0]["post"]
            title = None

            text_post_app_info = post.get("text_post_app_info")
            if text_post_app_info and text_post_app_info.get("link_preview_attachment"):
                title = text_post_app_info["link_preview_attachment"].get("title")

            # Check if title has been seen before and matches keyword
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

    # Count the amount of data
    total_data = len(modified_data)

    return jsonify({"total_data": total_data, "data": modified_data})

if __name__ == '__main__':
    app.run(debug=True)
