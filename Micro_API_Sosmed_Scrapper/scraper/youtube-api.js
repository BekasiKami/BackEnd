const axios = require('axios');
const moment = require('moment');

const apiKey = "AIzaSyAIoHOr_uIrPuhFRWAB38WjoDt4sMs1M-I";
const searchQuery = "bekasi";
const wordsToCount = ["banjir", "pembullyan", "perundungan", "maling", "hilang", "pembunuhan"];
const endpoint = "https://www.googleapis.com/youtube/v3/search";
const maxResults = 50;

const params = {
  q: searchQuery,
  part: "snippet",
  maxResults,
  key: apiKey
};

function processSearchResults(data) {
  for (const item of data.items) {
    const videoId = item.id.videoId;
    const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
    const title = item.snippet.title;

    console.log(`Title: ${title}`);
    console.log(`URL: ${videoUrl}`);

    const videoText = item.snippet.title + " " + item.snippet.description;

    const wordFrequencies = {};
    for (const word of wordsToCount) {
      wordFrequencies[word] = 0;
    }

    const words = videoText.toLowerCase().split(' ');

    for (const word of words) {
      if (word in wordFrequencies) {
        wordFrequencies[word]++;
      }
    }

    const sortedWords = Object.entries(wordFrequencies)
      .sort((a, b) => b[1] - a[1])
      .filter(entry => entry[1] > 0);

    for (const [word, frequency] of sortedWords) {
      console.log(`${word}: ${frequency}`);
    }

    console.log("\n");
  }
}

async function fetchAndProcessData() {
  while (true) {
    try {
      const response = await axios.get(endpoint, { params });
      const data = response.data;

      if ("error" in data) {
        console.log("Error:", data.error.message);
        break;
      }

      processSearchResults(data);
    } catch (error) {
      console.error("An error occurred:", error.message);
      break;
    }

    // Tunggu sebelum permintaan berikutnya (3 detik)
    await new Promise(resolve => setTimeout(resolve, 3000));
  }
}

fetchAndProcessData();
