// Initialize N with the default value
let N = 10;
let currentUserId = null;

// Function to handle the selection of N
function handleNChange() {
    const numRecommendationsSelect = document.getElementById("numRecommendations");
    N = parseInt(numRecommendationsSelect.value); // Update the global N

    if(currentUserId != null){
        getRecommendations(currentUserId);
    }
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

// Function to handle user ID input and display greeting
function handleUserIdInput() {
    const userIdInput = document.getElementById("userIdInput");
    const greetingDiv = document.getElementById("greeting");
    const userId = userIdInput.value.trim();
    currentUserId = userId;

    if (userId) {
        greetingDiv.textContent = `Hello ${userId}!`;
        getRecommendations(userId);
        userIdInput.value = ""; // Clear the input field
    } else {
        greetingDiv.textContent = `Please, enter your UserID`;
    }
}
function createStarRating(similarity) {
    const maxStars = 5;
    const numStars = Math.min(maxStars*2, Math.floor(similarity * 20))/2; // Scale to 0-10 and round
    const fullStars = Math.floor(numStars); // Number of full stars
    console.log(fullStars)
    const hasHalfStar = (numStars%1>0); // Check for a half star

    let starRatingHTML = '';
    for (let i = 0; i < fullStars; i++) {
        starRatingHTML += '<span class="star full-star">&#9733;</span>'; // Full star
    }
    if (hasHalfStar) {
        starRatingHTML += '<span class="fa">&#xf123;</span>'; // Half star
    }
    for (let i = 0; i < 5- (fullStars + hasHalfStar); i++) {
        starRatingHTML += '<span class="star full-star">&#9734;</span>'; // Full star
    }

    return starRatingHTML;
}


function createPlaceElement(itemName, similarity) {
    const placeDiv = document.createElement("div");
    placeDiv.classList.add("place");
    placeDiv.classList.add("recommendation");

    const h2 = document.createElement("h2");
    h2.textContent = itemName;
    placeDiv.appendChild(h2);

    const p = document.createElement("p");
    p.textContent = `Similarity: ${similarity.toFixed(2)}`;
    placeDiv.appendChild(p);

    const starRating = createStarRating(similarity);
    placeDiv.insertAdjacentHTML('beforeend', starRating); // Add rating to the place

    return placeDiv;
}

function displayRecommendations(recommendations) {
    const recommendationsDiv = document.getElementById("recommendations");
    recommendationsDiv.innerHTML = ""; // Clear previous recommendations

    if (recommendations && recommendations.length > 0) { // Check for an array
        recommendations.forEach(item => { // Use forEach on the array
            const placeElement = createPlaceElement(item.name, item.similarity);
            recommendationsDiv.appendChild(placeElement);
        });
    } else {
        recommendationsDiv.textContent = "No recommendations found.";
    }
}

async function getRecommendations(userId) {
    // **** START: Get selected recommendation types from CHECKBOXES ****

    // 1. Select all checkboxes belonging to the group using their shared 'name' attribute.
    //    We specifically select only the ones that are currently ':checked'.
    const typeCheckboxes = document.querySelectorAll('input[name="recommendationType"]:checked');

    // 2. Create an array to store the *values* of the checked boxes.
    //    We iterate through the NodeList returned by querySelectorAll.
    //    For each checked checkbox found, we get its 'value' attribute (e.g., "content", "collaborative").
    const selectedTypes = Array.from(typeCheckboxes).map(checkbox => checkbox.value);
    console.log(selectedTypes);

    // Now, the 'selectedTypes' variable holds an array of strings,
    // like: ['content'], or ['content', 'demographic'], or ['collaborative'], or [] if none are checked.

    // **** END: Get selected recommendation types from CHECKBOXES ****

    // Optional: Handle case where no type is selected
    if (selectedTypes.length === 0) {
        // You could default to one type, show a message, or let the backend handle it
        console.warn("No recommendation type selected. Sending empty array or defaulting.");
        // Example: Default to 'content' if none selected
        // selectedTypes.push('content');
        // Or display a message to the user:
        // document.getElementById('greeting').textContent = "Please select at least one recommendation type.";
        // return; // Stop the function if selection is required
    }



    if (userId != "") {
        try {
            const response = await fetch("http://127.0.0.1:5000/recommendations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ 
                    userId: userId, 
                    num_recommendations: N,
                    recommendation_types: selectedTypes,
                }), 
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayRecommendations(data.recommendations);
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        }
    } else {
        displayRecommendations([]);
    }
}

// Add event listener for Enter key press in the user ID input field
window.addEventListener("load", function () {
    const userIdInput = document.getElementById("userIdInput");
    userIdInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            handleUserIdInput();
        }
    });
});
