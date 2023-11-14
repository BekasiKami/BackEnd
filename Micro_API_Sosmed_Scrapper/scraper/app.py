from flask import Flask, request, jsonify
import os
import json
from twitter_scraper import Twitter_Scraper
from dotenv import load_dotenv

app = Flask(__name__)

try:
    load_dotenv()
except Exception as e:
    raise Exception(f"Error loading .env file: {str(e)}")

# Initialize Twitter_Scraper object for login
scraper = None

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

# Login when the server is first run
login_to_twitter()

# Function to merge scraped results with existing data in JSON file
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

        return {"message": "Scraping completed, results saved in 'scraped_tweets.json'", "success": True}
    else:
        return {"error": "No scraped results to save.", "success": False}, 400

@app.route('/api/scraped_tweets', methods=['GET'])
def get_scraped_tweets():
    try:
        # Read JSON file containing scraped results
        with open('scraped_tweets.json', 'r') as json_file:
            scraped_tweets = json.load(json_file)

        return jsonify(scraped_tweets)
    except Exception as e:
        return {"error": f"Error reading scraped tweets: {str(e)}", "success": False}, 500

if __name__ == '__main__':
    app.run(debug=True)
