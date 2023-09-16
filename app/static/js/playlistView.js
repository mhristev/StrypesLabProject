function searchTracks() {
    const searchQuery = document.getElementById("searchBar").value;
    const playlist_id = document.getElementById("playlistId").value;
    const platform = document.getElementById("platform").value;

    fetch("/search_tracks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            searchQuery: searchQuery,
            playlist_id: playlist_id,
            platform: platform,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            const searchResultsDiv = document.getElementById("searchResults");
            searchResultsDiv.innerHTML = "";

            data.results.forEach((track) => {
                const newCard = document.createElement("div");
                newCard.className = "card mb-3";
                newCard.style = "max-width: 540px;";
                var track_identifier = null;
                if (track.uri == null) {
                    track_identifier = track.id;
                } else {
                    track_identifier = track.uri;
                }
                albumName = track.album_name;
                newCard.id = "FoundTrackCard" + track_identifier;
                newCard.innerHTML = `

               
  <div class="row g-0">
    <div class="col-md-4">
      <img src="${track.image_url}" class="img-fluid rounded-start" alt="...">
    </div>
    <div class="col-md-8">
      <div class="card-body">
        <h5 class="card-title">${track.name}</h5>
        <p class="card-text"><small class="text-muted">Album: ${albumName}</small></p>
        <p class="card-text">${track.artists
            .map((artist) => artist.name)
            .join(", ")}</p>
            <button class="btn btn-primary" onclick="addToPlaylist('${track_identifier}')">Add to Playlist</button>
      </div>
    </div>
  </div>


  `;

                searchResultsDiv.appendChild(newCard);
            });
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

function addToPlaylist(trackId) {
    const playlistId = document.getElementById("playlistId").value;

    const platform = document.getElementById("platform").value;
    console.log(trackId, playlistId, platform);
    fetch(`/add_to_playlist`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            track_indentifier: trackId,
            platform: platform,
            playlist_id: playlistId,
        }),
    })
        .then((response) => {
            if (response.ok) {
                response.json().then((data) => {
                    console.log(data);
                    track_name = data.data.name;
                    track_image = data.data.image_url;
                    track_album = data.data.album_name;
                    console.log(track_name, track_image);
                    const cardHtml = `
                    <div
                    class="card mb-3"
                    style="max-width: 540px"
                    id="trackCard${trackId}"
                >
                    <div class="row g-0">
                        <div class="col-md-4">
                            <img
                                src="${track_image}"
                                class="img-fluid rounded-start"
                                alt="..."
                            />
                        </div>
                        <div class="col-md-8">
                            <div class="card-body">
                                <h5 class="card-title">${track_name}</h5>
                                <p class="text-muted">
                                    Album: ${track_album}
                                </p>

                                <p class="card-text">
                                ${data.data.artists
                                    .map((artist) => artist.name)
                                    .join(", ")}
                                </p>
                            </div>
                        </div>
                    </div>
                    <button
                        class="btn btn-danger remove-track-button"
                        data-track-id="{% if not track.uri %}{{ track.id }}{% else %}{{ track.uri }}{% endif %}"
                        onclick="removeTrackFromPlaylist('${trackId}', '${playlistId}', '${platform}')"
                    >
                        Remove
                    </button>
                </div>
                `;
                    const playlistTracksContainer =
                        document.getElementById("playlistTracks");

                    const newCardContainer = document.createElement("div");

                    newCardContainer.innerHTML = cardHtml;

                    playlistTracksContainer.insertBefore(
                        newCardContainer,
                        playlistTracksContainer.firstChild
                    );
                });
            } else {
                console.error("Error removing track");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

function removeTrackFromPlaylist(trackId, playlistId, platform) {
    const cardId = `trackCard${trackId}`;
    console.log(trackId, playlistId, platform);
    fetch(`/remove_track_from_playlist`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            track_id: trackId,
            platform: platform,
            playlist_id: playlistId,
        }),
    })
        .then((response) => {
            if (response.ok) {
                const cardToRemove = document.getElementById(cardId);
                if (cardToRemove) {
                    cardToRemove.remove();
                    console.log(`Track with ID ${trackId} removed.`);
                } else {
                    console.log(`Track with ID ${trackId} not found.`);
                }
            } else {
                console.error("Error removing track");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}
