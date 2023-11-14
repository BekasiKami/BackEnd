import requests
from bs4 import BeautifulSoup

def scrape_cnn_indonesia_articles(query):
    base_url = "https://www.cnnindonesia.com/search/?query={}".format(query)
    response = requests.get(base_url)

    if response.status_code != 200:
        print("Failed to fetch data from CNN Indonesia")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("article")

    results = []

    for article in articles:
        title = article.find("h2", class_="title").text.strip()
        url = article.find("a")["href"].strip()
        date = article.find("div", class_="date").text.strip()
        excerpt = article.find("div", class_="desc").text.strip()

        results.append({
            "title": title,
            "url": url,
            "date": date,
            "excerpt": excerpt
        })

    return results

# Set the query you want to search for (e.g., "bekasi")
query = "bekasi"

# Scrape articles related to the query
articles = scrape_cnn_indonesia_articles(query)

# Display the scraped articles
for index, article in enumerate(articles, start=1):
    print(f"Article {index}:")
    print(f"Title: {article['title']}")
    print(f"URL: {article['url']}")
    print(f"Date: {article['date']}")
    print(f"Excerpt: {article['excerpt']}\n")
