function transferPlaylist(playlistId, playlistName, fromPlatform, toPlatform) {
    var loadingElement = document.getElementById("loading" + playlistId);
    loadingElement.style.display = "block";

    var proceedButton = document.getElementById("proceedButton" + playlistId);
    proceedButton.disabled = true;

    var url = "/transfer_playlist/" + fromPlatform + "/" + toPlatform;

    var remove_var = "";

    if (toPlatform == "spotify") {
        remove_var = "Unfollow";
    } else if (toPlatform == "deezer") {
        remove_var = "Delete";
    }

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            playlist_id: playlistId,
            name: playlistName,
        }),
    })
        .then((response) => {
            if (response.ok) {
                console.log("Playlist transferred successfully");
                response.json().then((data) => {
                    console.log(data);
                    const new_playlistId = data.data.playlist_id;
                    const playlistName = data.data.playlist_name;
                    const nbOfTracks = data.data.number_of_tracks;
                    const viewUrl = data.data.view_url;
                    const deleteUrl = data.data.delete_url;
                    const image_url = data.data.image_url;
                    const newCard = document.createElement("div");
                    newCard.className = "col-6";
                    newCard.innerHTML = ` <div id="playlistCard${playlistId}">
                    <div class="card" style="width: 15rem">
                    <a
                            href="${viewUrl}"
                            style="text-decoration: none; color: black;"
                        >    
                    <img
                            src="${image_url}"
                            class="card-img-top"
                            alt="..."
                        />
                        <div class="card-body">
                            <p class="card-text">${playlistName}</p>
                            <p class="card-text">Tracks: ${nbOfTracks}</p>
                            </a>
                            <div class="row">
                            <div class="col-12">
                            <a
                        href="${deleteUrl}"
                        class="btn btn-danger btn-block"
                    >${remove_var}</a>
                            </div>
                            </div>
                        </div>
                        
                    </div>
                    
                </div>
                    
                `;

                    if (toPlatform == "spotify") {
                        const spotifyPlaylistsContainer =
                            document.getElementById(
                                "spotifyPlaylistsContainer"
                            );
                        const firstCard = spotifyPlaylistsContainer.firstChild;

                        spotifyPlaylistsContainer.insertBefore(
                            newCard,
                            firstCard
                        );
                    } else if (toPlatform == "deezer") {
                        const deezerPlaylistsContainer =
                            document.getElementById("deezerPlaylistsContainer");
                        const firstCard = deezerPlaylistsContainer.firstChild;

                        deezerPlaylistsContainer.insertBefore(
                            newCard,
                            firstCard
                        );
                    }
                });

                if (toPlatform == "spotify") {
                    $("#spotifyModal" + playlistId).modal("hide");
                } else if (toPlatform == "deezer") {
                    $("#deezerModal" + playlistId).modal("hide");
                }
            } else {
                console.error("Failed to transfer playlist");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

function deletePlaylist(platform, playlistId) {
    console.log("ASD");
    fetch(`/delete/${platform}/${playlistId}`, {
        method: "POST",
    })
        .then((response) => {
            if (response.ok) {
                const playlistCard = document.getElementById(
                    `playlistCard${playlistId}`
                );
                if (playlistCard) {
                    playlistCard.remove();
                }
            } else {
                console.error("Error deleting playlist");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

function createPlaylist(platform, event) {
    event.preventDefault();
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

    var removing_value = "";
    if (platform.toLowerCase() == "spotify") {
        const form = document.getElementById("createPlaylistForm");
        formData = new FormData(form);
        removing_value = "Unfollow";
    } else if (platform.toLowerCase() == "deezer") {
        const form = document.getElementById("createPlaylistDeezerForm");
        formData = new FormData(form);
        removing_value = "Delete";
    }
    fetch("/create_playlist", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            console.log("tuk");
            if (response.ok) {
                console.log("OK");
                console.log("Playlist created successfully!");
                response.json().then((data) => {
                    const playlistId = data.data.playlist_id;
                    const playlistName = data.data.playlist_name;
                    const viewUrl = data.data.view_url;
                    const deleteUrl = data.data.delete_url;
                    const platform = data.data.platform;
                    const image_url = data.data.image_url;

                    const newCard = document.createElement("div");
                    newCard.className = "col-6";
                    newCard.innerHTML = `
                    <div id="playlistCard${playlistId}">
                        <div class="card" style="width: 15rem">
                        <a href="${viewUrl}"
                            style="text-decoration: none; color: black;">
                        <img
                                src="${image_url}"
                                class="card-img-top"
                                alt="..."
                            />
                            <div class="card-body">
                                <p class="card-text">${playlistName}</p>
                                <p class="card-text">Tracks: 0</p>
                                </a>
                                <div class="row">
                                <div class="col-12">
                                <a
                            href="${deleteUrl}"
                            onclick="confirmDelete('${platform.toLowerCase()}', '${playlistId}')"
                            class="btn btn-danger btn-block"
                        >${removing_value}</a>
                                </div>
                                </div>
                            </div>
                            
                        </div>
                        
                    </div>
                `;

                    if (platform.toLowerCase() == "spotify") {
                        const firstCard = spotifyPlaylistsContainer.firstChild;
                        spotifyPlaylistsContainer.insertBefore(
                            newCard,
                            firstCard
                        );
                    } else if (platform.toLowerCase() == "deezer") {
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
                console.error("Error creating playlist");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("playlistSearch");
    const playlistCards = document.querySelectorAll("[id^='playlistCard']");

    searchInput.addEventListener("input", function () {
        const searchTerm = searchInput.value.toLowerCase();

        playlistCards.forEach(function (card) {
            const playlistName = card
                .querySelector(".card-text")
                .textContent.toLowerCase();

            if (playlistName.includes(searchTerm)) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }
        });
    });
});

function confirmDelete(platform, playlistId) {
    if (confirm("Are you sure you want to remmove this playlist?")) {
        deletePlaylist(platform, playlistId);
    }
}
