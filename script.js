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
