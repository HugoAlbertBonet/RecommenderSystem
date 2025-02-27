function filterPlaces() {
    let filter = document.getElementById("filter").value;
    let places = document.querySelectorAll(".place");

    places.forEach(place => {
        if (filter === "all" || place.classList.contains(filter)) {
            place.style.display = "block";
        } else {
            place.style.display = "none";
        }
    });
}

// Function to fetch the title from the backend
function fetchTitle() {
    fetch("http://127.0.0.1:5000/get_title") // Replace with your backend URL if needed
        .then(response => response.json())
        .then(data => {
            const titleElement = document.querySelector("header h1");
            titleElement.textContent = data.title;
        })
        .catch(error => {
            console.error("Error fetching title:", error);
        });
}

// Call fetchTitle() when the page loads
window.addEventListener("load", fetchTitle);
