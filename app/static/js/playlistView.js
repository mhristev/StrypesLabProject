function searchTracks() {
    // Get the search query from the input field
    const searchQuery = document.getElementById("searchBar").value;
    console.log(searchQuery);
    const playlist_id = document.getElementById("playlistId").value;
    const platform = document.getElementById("platform").value;
    console.log(playlist_id, platform);
    // Send a POST request to /baba with the search query
    fetch("/search_tracks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            searchQuery: searchQuery,
            playlist_id: playlist_id,
            platform: platform,
        }), // Send the search query as JSON
    })
        .then((response) => response.json())
        .then((data) => {
            // Update the #searchResults div with the search results
            const searchResultsDiv = document.getElementById("searchResults");
            searchResultsDiv.innerHTML = ""; // Clear previous results

            // Create Bootstrap cards for each track
            data.results.forEach((track) => {
                const newCard = document.createElement("div");
                newCard.className = "row g-0";
                var track_identifier = null;
                if (track.uri == null) {
                    track_identifier = track.id;
                } else {
                    track_identifier = track.uri;
                }
                albumName = track.album_name;
                newCard.id = "FoundTrackCard" + track_identifier;
                newCard.innerHTML = `
                <div class="col-md-4">
      <img src="${track.image_url}" class="img-fluid rounded-start" alt="...">
    </div>
    <div class="col-md-8">
      <div class="card-body">
        <h5 class="card-title"> ${track.name}</h5>
        <p class="card-text">Artist: ${track.artists
            .map((artist) => artist.name)
            .join(", ")}</p>
        <p class="card-text"><small class="text-muted">Album:${albumName}</small></p>
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
    console.log("AAAAA");
    // Get the value of the hidden input with id "playlistId"
    const playlistId = document.getElementById("playlistId").value;

    // Get the value of the hidden input with id "platform"
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
                    <div class="row mb-4" id="trackCard${trackId}">
                        <!-- Start a new row for each track -->
                        <div class="col-md-12">
                            <div class="d-flex position-relative">
                                <img
                                    src="${track_image}"
                                    class="flex-shrink-0 me-3"
                                    alt="..."
                                    width="200"
                                    height="200"
                                />
                                <div>
                                    <h5 class="mt-0">${track_name}</h5>
                                    <p class="mt-0">Album: ${track_album}</p>
                                    <p class="mt-0">${data.data.artists
                                        .map((artist) => artist.name)
                                        .join(", ")}</p>
                                </div>
                            </div>
                            <button
                                class="btn btn-danger remove-track-button"
                                onclick="removeTrackFromPlaylist('${trackId}', '${playlistId}', '${platform}')"
                            >
                                Remove
                            </button>
                        </div>
                    </div>
                `;
                    const playlistTracksContainer =
                        document.getElementById("playlistTracks");

                    // Create a new div element to hold the card
                    const newCardContainer = document.createElement("div");

                    // Set the innerHTML of the new container to the card HTML
                    newCardContainer.innerHTML = cardHtml;

                    // Insert the new card at the beginning of the container
                    playlistTracksContainer.insertBefore(
                        newCardContainer,
                        playlistTracksContainer.firstChild
                    );
                });
            } else {
                // Handle error cases here
                console.error("Error removing track");
            }
        })
        .catch((error) => {
            // Handle network or other errors here
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
                // Handle error cases here
                console.error("Error removing track");
            }
        })
        .catch((error) => {
            // Handle network or other errors here
            console.error("Error:", error);
        });
}
