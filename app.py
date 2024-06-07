import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

GENIUS_API_TOKEN = 'X1CkjRN0ZfMsYFY4Bc87Z1WB_zTaOCo0zn--mTurfAu2lE6zoWZiTocEVxeK0Xct'

def search_lyrics(query):
    url = "https://api.genius.com/search"
    headers = {
        "Authorization": f"Bearer {GENIUS_API_TOKEN}"
    }
    params = {
        "q": query
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def get_song_details(song_id):
    url = f"https://api.genius.com/songs/{song_id}"
    headers = {
        "Authorization": f"Bearer {GENIUS_API_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        json_response = response.json()
        
        song = json_response.get('response', {}).get('song', {})
        media = song.get('media', [])
        
        media_url = None
        for m in media:
            if m.get('provider') == 'soundcloud':
                media_url = m.get('url')
                break

        # Fetch oEmbed HTML for SoundCloud
        oembed_html = None
        if media_url:
            oembed_response = requests.get(f"https://soundcloud.com/oembed?format=json&url={media_url}")
            oembed_response.raise_for_status()
            oembed_html = oembed_response.json().get('html')
            
            if oembed_html:
                soup = BeautifulSoup(oembed_html, 'html.parser')
                iframe = soup.find('iframe')
                if iframe:
                    iframe['width'] = "100%"  # Set width to 100%
                    iframe['height'] = "200px"  # Set height to 200px
                    oembed_html = str(soup)
                else:
                    oembed_html = None

        release_date = song.get('release_date')
        if release_date:
            year = release_date.split('-')[0]
        else:
            year = 'Unknown'

        song_info = {
            'title': song.get('title'),
            'artist': song.get('primary_artist', {}).get('name'),
            'producers': [producer.get('name') for producer in song.get('producer_artists', [])],
            'label': song.get('label', 'Unknown'),
            'cover_image_url': song.get('song_art_image_url'),
            'media_html': oembed_html,
            'year': year
        }
        return song_info
    except Exception as e:
        print("Error occurred:", e)
        return None


def get_lyrics(song_id):
    url = f"https://api.genius.com/songs/{song_id}"
    headers = {
        "Authorization": f"Bearer {GENIUS_API_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        json_response = response.json()
        path = json_response['response']['song']['path']
        cover_image_url = json_response['response']['song']['song_art_image_thumbnail_url']

        # Scrape the lyrics from the song's URL
        page_url = f"https://genius.com{path}"
        page = requests.get(page_url)
        page.raise_for_status()  # Raise an exception for HTTP errors
        html = BeautifulSoup(page.text, 'html.parser')

        # Try multiple methods to get the lyrics
        lyrics_div = html.find("div", class_="lyrics")
        if lyrics_div:
            lyrics = lyrics_div.get_text()
        else:
            # Check for the new lyrics container
            lyrics_containers = html.find_all("div", class_="Lyrics__Container-sc-1ynbvzw-1 kUgSbL")
            lyrics = ""
            for container in lyrics_containers:
                lyrics += container.get_text(separator="\n")
            if not lyrics:
                lyrics = "Sorry, the lyrics could not be found."

        return lyrics, cover_image_url
    except Exception as e:
        print("Error occurred:", e)
        return "Sorry, an error occurred while fetching the lyrics.", None, None


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        results = search_lyrics(query)
        return jsonify(results)
    return jsonify({"error": "No query provided"})

@app.route('/lyrics/<song_id>', methods=['GET'])
def lyrics(song_id):
    lyrics, cover_image_url = get_lyrics(song_id)
    song_details = get_song_details(song_id)
    print("Song Details:", song_details)
    if not lyrics:
        # Handle case where lyrics are not found
        return render_template('lyrics.html', lyrics="Sorry, the lyrics could not be found.", cover_image_url=None)
    return render_template('lyrics.html', lyrics=lyrics, cover_image_url=cover_image_url, song_details=song_details)


if __name__ == '__main__':
    app.run(debug=True)
