document.addEventListener('DOMContentLoaded', () => {
    // --- Get DOM Elements ---
    const loginScreen = document.getElementById('login-screen');
    const mainAppContent = document.getElementById('main-app-content');
    const loginUserIdInput = document.getElementById('loginUserId');
    const loginPasswordInput = document.getElementById('loginPassword');
    const loginButton = document.getElementById('loginButton');
    const loginError = document.getElementById('login-error');
    const greetingDiv = document.getElementById('greeting');
    const recommendationsDiv = document.getElementById('recommendations');
    const numRecommendationsSelect = document.getElementById('numRecommendations');
    const recommendationCheckboxes = document.querySelectorAll('input[name="recommendationType"]');
    const titleElement = document.querySelector("header h1"); // For fetchTitle

    // --- Global State ---
    let N = parseInt(numRecommendationsSelect.value); // Initialize N from the select element
    let currentUserId = null; // Variable to store the logged-in user ID

    // --- Event Listeners ---

    // Login Button Click Handler
    loginButton.addEventListener('click', handleLogin);

    // Listen for Enter key press in password field for convenience
    loginPasswordInput.addEventListener('keyup', function(event) {
        if (event.key === "Enter") {
            handleLogin();
        }
    });

    // Recommendation Controls Listeners
    numRecommendationsSelect.addEventListener('change', handleNChange);
    recommendationCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleRecommendationTypeChange);
    });

    // Fetch title on initial load
    fetchTitle(); // Call fetchTitle when the DOM is ready

    // --- Functions ---

    function handleLogin() {
        const userId = loginUserIdInput.value.trim();
        const password = loginPasswordInput.value;

        loginError.textContent = ''; // Clear previous errors

        if (!userId || !password) {
            loginError.textContent = 'Please enter both User ID and Password.';
            return;
        }

        // --- !!! IMPORTANT: LOGIN VALIDATION ---
        // Replace this with your actual validation logic (e.g., API call)
        const isValidLogin = validateCredentials(userId, password);

        if (isValidLogin) {
            // Login Successful
            currentUserId = userId; // Store the logged-in user ID
            greetingDiv.textContent = `Welcome, User ${currentUserId}!`; // Update greeting

            // Hide login screen, show main app
            loginScreen.style.display = 'none';
            mainAppContent.style.display = 'block'; // Or 'flex', 'grid' etc.

            // --- *** CALL ACTUAL getRecommendations *** ---
            recommendationsDiv.innerHTML = '<p>Loading recommendations...</p>'; // Show loading indicator
            getRecommendations(currentUserId); // Fetch initial recommendations

        } else {
            // Login Failed
            loginError.textContent = 'Invalid User ID or Password.';
            loginPasswordInput.value = ''; // Clear password field on failure
        }
    }

    // --- Placeholder Validation Function ---
    // Replace this with a real check (e.g., API call to a /login endpoint)
    function validateCredentials(userId, password) {
        console.log(`Validating User: ${userId}`); // Keep console log for debugging
        // --- !!! THIS IS A DUMMY CHECK - DO NOT USE IN PRODUCTION !!! ---
        // In a real app, send userId and password to a secure backend endpoint.
        // For demonstration, let's accept any non-empty user/pass
        return userId.length > 0 && password.length > 0;
    }

    // --- Function to handle the selection of N ---
    function handleNChange() {
        N = parseInt(numRecommendationsSelect.value); // Update the global N
        console.log("Number of recommendations changed to:", N);
        if (currentUserId) { // Only fetch if a user is logged in
            getRecommendations(currentUserId);
        }
    }

    // --- Function to handle recommendation type changes ---
    function handleRecommendationTypeChange() {
        console.log("Recommendation types changed.");
        if (currentUserId) { // Only fetch if a user is logged in
            getRecommendations(currentUserId);
        }
    }


    // --- Function to fetch the title from the backend ---
    function fetchTitle() {
        fetch("http://127.0.0.1:5000/get_title") // Replace with your backend URL if needed
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (titleElement) {
                    titleElement.textContent = data.title;
                }
            })
            .catch(error => {
                console.error("Error fetching title:", error);
                if (titleElement) {
                    titleElement.textContent = "Valencia Guide (Error Loading Title)"; // Fallback title
                }
            });
    }

    // --- Star Rating Function ---
    function createStarRating(similarity) {
        const maxStars = 5;
        // Ensure similarity is treated as a number between 0 and 1
        const validSimilarity = Math.max(0, Math.min(1, Number(similarity) || 0));
        const numStars = Math.round((validSimilarity * maxStars) * 2) / 2; // Round to nearest 0.5
        const fullStars = Math.floor(numStars);
        const hasHalfStar = (numStars % 1 !== 0);

        let starRatingHTML = '';
        for (let i = 0; i < fullStars; i++) {
            starRatingHTML += '<span class="star full-star">&#9733;</span>'; // Full star
        }
        if (hasHalfStar) {
            // Using Font Awesome half star - make sure Font Awesome is linked in your HTML
            starRatingHTML += '<span class="fa fa-star-half-o" aria-hidden="true"></span>';
            // Or use a text-based half star if Font Awesome isn't available:
            // starRatingHTML += '<span class="star half-star">½</span>';
        }
        const emptyStars = maxStars - fullStars - (hasHalfStar ? 1 : 0);
        for (let i = 0; i < emptyStars; i++) {
            starRatingHTML += '<span class="star empty-star">&#9734;</span>'; // Empty star
        }

        return starRatingHTML;
    }


    // --- Create Place Element Function ---
    function createPlaceElement(itemName, similarity) {
        const placeDiv = document.createElement("div");
        placeDiv.classList.add("place");
        placeDiv.classList.add("recommendation");

        const h2 = document.createElement("h2");
        h2.textContent = itemName;
        placeDiv.appendChild(h2);

        const p = document.createElement("p");
        p.textContent = `Similarity: ${similarity.toFixed(3)}`;
        placeDiv.appendChild(p);

        const starRating = createStarRating(similarity);
        placeDiv.insertAdjacentHTML('beforeend', starRating); // Add rating to the place

        return placeDiv;
    }

    // --- Display Recommendations Function ---
    function displayRecommendations(recommendations) {
        recommendationsDiv.innerHTML = ""; // Clear previous recommendations or loading message

        if (recommendations && Array.isArray(recommendations) && recommendations.length > 0) {
            recommendations.forEach(item => {
                // Assuming your backend returns 'name' and 'similarity'
                if (item && typeof item.name !== 'undefined' && typeof item.similarity !== 'undefined') {
                    const placeElement = createPlaceElement(item.name, item.similarity);
                    recommendationsDiv.appendChild(placeElement);
                } else {
                    console.warn("Received recommendation item in unexpected format:", item);
                }
            });
        } else {
            recommendationsDiv.innerHTML = "<p>No recommendations found or error fetching data.</p>"; // More informative message
        }
    }

    // --- Get Recommendations Function (Your existing logic) ---
    async function getRecommendations(userId) {
        if (!userId) {
            console.error("getRecommendations called without userId.");
            displayRecommendations([]); // Clear display if no user ID
            return;
        }

        const typeCheckboxes = document.querySelectorAll('input[name="recommendationType"]:checked');
        const selectedTypes = Array.from(typeCheckboxes).map(checkbox => checkbox.value);

        console.log(`Fetching ${N} recommendations for user ${userId} (Types: ${selectedTypes.join(', ') || 'None'})`);

        // Optional: Handle case where no type is selected if required by backend
        if (selectedTypes.length === 0) {
            console.warn("No recommendation type selected. Sending empty array.");
            // If your backend requires at least one type, you might want to show a message
            // recommendationsDiv.innerHTML = "<p>Please select at least one recommendation type.</p>";
            // return;
        }

        // Show loading indicator *before* the fetch call
        recommendationsDiv.innerHTML = '<p>Loading recommendations...</p>';

        try {
            const response = await fetch("http://127.0.0.1:5000/recommendations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    userId: userId,
                    num_recommendations: N, // Use the global N variable
                    recommendation_types: selectedTypes,
                }),
            });

            if (!response.ok) {
                // Try to get error message from backend response body
                let errorData = null;
                try {
                    errorData = await response.json();
                } catch (e) { /* Ignore if body isn't valid JSON */ }
                const errorMessage = errorData?.error || `HTTP error! status: ${response.status}`;
                throw new Error(errorMessage);
            }

            const data = await response.json();
            // Ensure the backend response has the expected structure
            if (data && data.recommendations) {
                 displayRecommendations(data.recommendations);
            } else {
                console.error("Unexpected response format from backend:", data);
                displayRecommendations([]); // Display empty state
            }

        } catch (error) {
            console.error("Error fetching recommendations:", error);
            recommendationsDiv.innerHTML = `<p>Error loading recommendations: ${error.message}</p>`; // Show error message
        }
    }

    // --- Initial State Setup ---
    // The main app is hidden via CSS/inline style initially.
    // fetchTitle() is called above.
    // No initial recommendation fetch, waits for login.

}); // End DOMContentLoaded
