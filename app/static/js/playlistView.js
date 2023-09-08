function searchTracks() {
    // Get the search query from the input field
    const searchQuery = document.getElementById("searchBar").value;
    console.log(searchQuery);
    const playlist_id = document.getElementById("playlistId").value;
    const platform = document.getElementById("platform").value;
    console.log(playlist_id, platform);
    // Send a POST request to /baba with the search query
    fetch("/baba", {
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
                const card = document.createElement("div");
                card.className = "card mb-3";
                card.style = "max-width: 500px;";

                const innerDiv1 = document.createElement("div");
                innerDiv1.className = "row g-0";
                card.appendChild(innerDiv1);

                const innerDiv2 = document.createElement("div");
                innerDiv2.className = "col-md-4";
                innerDiv1.appendChild(innerDiv2);

                const image = document.createElement("img");
                image.src = track.image_url;
                image.className = "img-fluid rounded-start";
                innerDiv2.appendChild(image);

                const innerDiv3 = document.createElement("div");
                innerDiv3.className = "col-md-8";
                innerDiv1.appendChild(innerDiv3);

                const cardBody = document.createElement("div");
                cardBody.className = "card-body";
                innerDiv3.appendChild(cardBody);

                const title = document.createElement("h5");
                title.className = "card-title";
                title.textContent = track.name;
                cardBody.appendChild(title);

                const artists = document.createElement("p");
                artists.className = "card-text";
                artists.textContent = "Artists: " + track.artists.join(", ");
                cardBody.appendChild(artists);

                searchResultsDiv.appendChild(card);
            });
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

document.addEventListener("DOMContentLoaded", function () {
    const removeTrackButtons = document.querySelectorAll(
        ".remove-track-button"
    );

    removeTrackButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const trackId = button.getAttribute("data-track-id");

            const playlist_id = document.getElementById("playlistId").value;
            const platform = document.getElementById("platform").value;
            const cardId = `trackCard${trackId}`;

            fetch(`/remove_track_from_playlist`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    track_id: trackId,
                    platform: platform,
                    playlist_id: playlist_id,
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
        });
    });
});
