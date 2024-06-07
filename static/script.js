function searchLyrics() {

    const query = document.getElementById('query').value;
    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';
            if (data.error) {
                resultsDiv.innerHTML = `<p class="has-text-danger">${data.error}</p>`;
            } else {
                data.response.hits.forEach(hit => {
                    const result = document.createElement('div');
                    const coverImageUrl = hit.result.song_art_image_thumbnail_url;
                    const title = hit.result.full_title.length > 35 ? hit.result.full_title.substring(0, 35) + '...' : hit.result.full_title;
                    result.innerHTML = `
                        <div class="box" style="display: flex; padding: 10px; width: 100%; height: 200px; margin-bottom: 10px; animation: moveBannerCard 1s forwards;">
                        <img id="image" src="${coverImageUrl}" alt="Song Cover" style="height: 100%;">
                        <div class="desc" style="margin-left: 30px;">
                            <h2 class="title">${title}</h2>
                            <p>Artist: ${hit.result.primary_artist.name}</p>
                            <a href="/lyrics/${hit.result.id}" class="button is-link" style="background: rgb(194, 76, 92);">View Lyrics</a>
                            </div>
                        </div>
                    `;
                    resultsDiv.appendChild(result);
                });
            }
        });
}
document.addEventListener("DOMContentLoaded", function() {
    // Event listener for Enter key press
    document.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            searchLyrics();
        }
    });
});