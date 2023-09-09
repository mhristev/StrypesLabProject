function transferSpotifyToDeezer(playlistId) {
    console.log(playlistId);
    fetch("/transfer_playlist_spotify_to_deezer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            playlist_id: playlistId,
            name: "transfer1",
        }),
    })
        .then((response) => {
            // Handle the server's response here (e.g., show a success message)
            if (response.ok) {
                console.log("Playlist transferred successfully");
                $("#deezerModal" + playlistId).modal("hide");
                // You can perform further actions or update the UI as needed
            } else {
                console.error("Failed to transfer playlist");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });

    // Close the modal (optional)
}
// JavaScript for handling playlist deletion
// JavaScript for handling playlist deletion
function deletePlaylist(platform, playlistId) {
    console.log(platform);
    console.log(playlistId);
    fetch(`/delete/${platform}/${playlistId}`, {
        method: "POST",
    })
        .then((response) => {
            if (response.ok) {
                console.log("TIIIIKKKK");
                // Handle success, e.g., remove the playlist card from the UI
                const playlistCard = document.getElementById(
                    `playlistCard${playlistId}`
                );
                if (playlistCard) {
                    playlistCard.remove();
                }
            } else {
                // Handle errors here
                console.error("Error deleting playlist");
            }
        })
        .catch((error) => {
            // Handle network or other errors here
            console.error("Error:", error);
        });
}

function createPlaylist(platform, event) {
    event.preventDefault();
    console.log("Creating playlist");
    formData = null;
    const spotifyPlaylistsContainer = document.getElementById(
        "spotifyPlaylistsContainer"
    );
    const deezerPlaylistsContainer = document.getElementById(
        "deezerPlaylistsContainer"
    );
    var spotifyPlaylistsContainer1 = document.getElementById(
        "spotifyPlaylistsContainer"
    );

    console.log(spotifyPlaylistsContainer1);
    console.log(deezerPlaylistsContainer);

    if (platform.toLowerCase() == "spotify") {
        const form = document.getElementById("createPlaylistForm");
        formData = new FormData(form);
    } else if (platform.toLowerCase() == "deezer") {
        const form = document.getElementById("createPlaylistDeezerForm");
        formData = new FormData(form);
    }
    fetch("/create_playlist", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            console.log("tuk");
            if (response.ok) {
                console.log("OK");
                // Handle success, you can optionally redirect or show a success message
                console.log("Playlist created successfully!");
                response.json().then((data) => {
                    console.log(data);
                    const playlistId = data.data.playlist_id; // Replace with the actual field name from your Flask response
                    const playlistName = data.data.playlist_name; // Replace with the actual field name from your Flask response
                    const viewUrl = data.data.view_url;
                    const deleteUrl = data.data.delete_url;
                    const transferUrl = data.data.transfer_url;
                    const platform = data.data.platform;
                    const image_url = data.data.image_url;
                    console.log("Playlist name: " + playlistName);
                    console.log(playlistId);
                    // Create a new card element
                    const newCard = document.createElement("div");
                    newCard.className = "col-md-4";
                    newCard.innerHTML = `
                    <div class="card mb-4" style="width: 18rem">
                        <img
                            src="${image_url}"
                            class="card-img-top"
                            alt="..."
                        />
                        <div class="card-body">
                            <p class="card-text">${playlistName}</p>
                        </div>
                        <a
                            href="${viewUrl}"
                            class="btn btn-primary stretched-link"
                        >View</a>
                    </div>
                    <a
                        href="${deleteUrl}"
                        class="btn btn-warning"
                    >Unfollow</a>
                    <a
                        href="${transferUrl}"
                        class="btn btn-warning"
                    >Send to Deezer</a>
                `;

                    if (platform.toLowerCase() == "spotify") {
                        const firstCard = spotifyPlaylistsContainer.firstChild;
                        spotifyPlaylistsContainer.insertBefore(
                            newCard,
                            firstCard
                        );
                    } else if (platform.toLowerCase() == "deezer") {
                        console.log("in the if for deezer");
                        const deezerPlaylistsContainer =
                            document.getElementById("deezerPlaylistsContainer");
                        console.log(deezerPlaylistsContainer);
                        const firstCard = deezerPlaylistsContainer.firstChild;
                        console.log(firstCard.textContent);
                        deezerPlaylistsContainer.insertBefore(
                            newCard,
                            firstCard
                        );
                    }
                });
            } else {
                // Handle errors here
                console.error("Error creating playlist");
            }
        })
        .catch((error) => {
            // Handle network or other errors here
            console.error("Error:", error);
        });
}
