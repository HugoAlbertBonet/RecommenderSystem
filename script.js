document.addEventListener('DOMContentLoaded', () => {
    // --- Get DOM Elements ---
    const loginScreen = document.getElementById('login-screen');
    const mainAppContent = document.getElementById('main-app-content');

    // Login Form Elements
    const loginForm = document.getElementById('login-form');
    const loginUserIdInput = document.getElementById('loginUserId');
    const loginPasswordInput = document.getElementById('loginPassword');
    const loginButton = document.getElementById('loginButton');
    const loginError = document.getElementById('login-error');
    const showRegisterLink = document.getElementById('show-register-link');

    // Register Form Elements
    const registerForm = document.getElementById('register-form');
    const registerUserIdInput = document.getElementById('registerUserId');
    const registerNameInput = document.getElementById('registerName');
    const registerAgeInput = document.getElementById('registerAge');
    const registerGenderInput = document.getElementById('registerGender');
    const registerJobInput = document.getElementById('registerJob');
    const registerChildrenInput = document.getElementById('registerChildren');
    const registerChildrenOldInput = document.getElementById('registerChildrenOld');
    const registerChildrenYoungInput = document.getElementById('registerChildrenYoung');
    const registerPasswordInput = document.getElementById('registerPassword');
    const registerConfirmPasswordInput = document.getElementById('registerConfirmPassword');
    const registerButton = document.getElementById('registerButton');
    const registerMessage = document.getElementById('register-message');
    const showLoginLink = document.getElementById('show-login-link');

    // Main App Elements
    const greetingDiv = document.getElementById('greeting');
    const recommendationsDiv = document.getElementById('recommendations');
    const numRecommendationsSelect = document.getElementById('numRecommendations');
    const recommendationCheckboxes = document.querySelectorAll('input[name="recommendationType"]');
    const titleElement = document.querySelector("header h1"); // For fetchTitle

    // --- Global State ---
    let N = parseInt(numRecommendationsSelect.value); // Initialize N
    let currentUserId = null; // Logged-in user ID

    // --- Event Listeners ---

    // Login/Register Toggles
    showRegisterLink.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent default link behavior
        showRegisterForm();
    });

    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent default link behavior
        showLoginForm();
    });

    // Form Submissions
    loginButton.addEventListener('click', handleLogin);
    registerButton.addEventListener('click', handleRegister);

    // Enter Key Listeners
    loginPasswordInput.addEventListener('keyup', function(event) {
        if (event.key === "Enter") handleLogin();
    });
    registerConfirmPasswordInput.addEventListener('keyup', function(event) {
        if (event.key === "Enter") handleRegister();
    });
    // Optional: Add Enter listener to other register fields if desired

    // Recommendation Controls Listeners
    numRecommendationsSelect.addEventListener('change', handleNChange);
    recommendationCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleRecommendationTypeChange);
    });

    // Fetch title on initial load
    fetchTitle();

    // --- View Toggle Functions ---

    function showLoginForm() {
        registerForm.style.display = 'none';
        loginForm.style.display = 'block';
        loginError.textContent = ''; // Clear any previous login errors
        registerMessage.textContent = ''; // Clear any register messages
    }

    function showRegisterForm() {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        loginError.textContent = ''; // Clear any login errors
        registerMessage.textContent = ''; // Clear any previous register messages
    }


    // --- Authentication Functions ---

    function handleLogin() {
        const userId = loginUserIdInput.value.trim();
        const password = loginPasswordInput.value;

        loginError.textContent = ''; // Clear previous errors
        loginError.classList.remove('success'); // Ensure not green

        if (!userId || !password) {
            loginError.textContent = 'Please enter both User ID and Password.';
            return;
        }

        // --- !!! IMPORTANT: LOGIN VALIDATION ---
        // Replace this with your actual validation logic (e.g., API call to /login)
        const isValidLogin = validateCredentials(userId, password); // Placeholder

        if (isValidLogin) {
            // Login Successful
            currentUserId = userId;
            greetingDiv.textContent = `Welcome, User ${currentUserId}!`;

            loginScreen.style.display = 'none';
            mainAppContent.style.display = 'block';

            recommendationsDiv.innerHTML = '<p>Loading recommendations...</p>';
            getRecommendations(currentUserId);

        } else {
            // Login Failed
            loginError.textContent = 'Invalid User ID or Password.';
            loginPasswordInput.value = '';
        }
    }

    async function handleRegister() {
        const userId = registerUserIdInput.value.trim();
        const user_name = registerNameInput.value.trim();
        const userAge = registerAgeInput.value.trim();
        const userGender = registerGenderInput.value.trim();
        const userJob = registerJobInput.value.trim();
        const userChildren = registerChildrenInput.value.trim();
        const userChildrenOld = registerChildrenOldInput.value.trim();
        const userChildrenYoung = registerChildrenYoungInput.value.trim();
        const password = registerPasswordInput.value;
        const confirmPassword = registerConfirmPasswordInput.value;

        registerMessage.textContent = ''; // Clear previous messages
        registerMessage.classList.remove('success'); // Ensure not green

        // --- Client-side validation ---
        if (!userId || !user_name || !userAge || !userGender || !userJob || !userChildren || !password || !confirmPassword) {
            registerMessage.textContent = 'Please fill in all required fields.';
            return;
        }
        if (password !== confirmPassword) {
            registerMessage.textContent = 'Passwords do not match.';
            return;
        }
        // Optional: Add more validation (e.g., password complexity, user ID format)

        // --- Call Backend for Registration ---
        try {
            // *** YOU NEED TO CREATE THIS /register ENDPOINT IN YOUR BACKEND (backend.py) ***
            const response = await fetch("http://127.0.0.1:5000/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    userId: userId,
                    password: password, // Send password (backend should hash it)
                    user_name: user_name,
                    userAge: userAge,
                    userGender: userGender,
                    userJob: userJob,
                    userChildren: userChildren,
                    userChildrenOld: userChildrenOld,
                    userChildrenYoung: userChildrenYoung,
                }),
            });

            const data = await response.json(); // Always try to parse JSON

            if (!response.ok) {
                // Use error message from backend if available, otherwise use status text
                throw new Error(data.error || `Registration failed: ${response.statusText}`);
            }

            // Registration Successful
            registerMessage.textContent = data.message || 'Registration successful! You can now log in.';
            registerMessage.classList.add('success'); // Make text green

            // Clear the form
            registerUserIdInput.value = '';
            registerPasswordInput.value = '';
            registerConfirmPasswordInput.value = '';

            // Optionally switch back to login form after a short delay
            setTimeout(showLoginForm, 2000); // Switch back after 2 seconds

        } catch (error) {
            console.error("Registration Error:", error);
            registerMessage.textContent = error.message || 'An error occurred during registration.';
            registerMessage.classList.remove('success');
        }
    }

    // --- Placeholder Login Validation Function ---
    // Replace this with a real check (e.g., API call to a /login endpoint)
    function validateCredentials(userId, password) {
        console.log(`Validating User: ${userId}`);
        // --- !!! DUMMY CHECK - DO NOT USE IN PRODUCTION !!! ---
        return userId.length > 0 && password.length > 0;
    }

    // --- Recommendation Functions (handleNChange, handleRecommendationTypeChange, fetchTitle, createStarRating, createPlaceElement, displayRecommendations, getRecommendations) ---
    // --- Keep all your existing recommendation-related functions here ---
    // --- (No changes needed in them for the registration feature) ---

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
        // Using the class name from your previous version that worked for styling
        placeDiv.classList.add("place");
        placeDiv.classList.add("recommendation"); // Keep both if needed, or just the one your CSS uses

        // Use h3 for semantic structure within a card/item
        const heading = document.createElement("h3");
        heading.textContent = itemName;
        placeDiv.appendChild(heading);

        const p = document.createElement("p");
        // Check if similarity is a valid number before formatting
        const similarityText = typeof similarity === 'number' ? similarity.toFixed(3) : 'N/A';
        p.textContent = `Similarity: ${similarityText}`;
        placeDiv.appendChild(p);

        // Add star rating only if similarity is a valid number
        if (typeof similarity === 'number') {
            const starRatingDiv = document.createElement('div');
            starRatingDiv.classList.add('star-rating'); // Add class for styling
            starRatingDiv.innerHTML = createStarRating(similarity);
            placeDiv.appendChild(starRatingDiv);
        }

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

        if (selectedTypes.length === 0) {
            console.warn("No recommendation type selected.");
            // Decide if you want to proceed or show a message
            // recommendationsDiv.innerHTML = "<p>Please select at least one recommendation type.</p>";
            // return;
        }

        recommendationsDiv.innerHTML = '<p>Loading recommendations...</p>';

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
                let errorData = null;
                try { errorData = await response.json(); } catch (e) { /* Ignore */ }
                const errorMessage = errorData?.error || `HTTP error! status: ${response.status}`;
                throw new Error(errorMessage);
            }

            const data = await response.json();
            if (data && data.recommendations) {
                 displayRecommendations(data.recommendations);
            } else {
                console.error("Unexpected response format from backend:", data);
                displayRecommendations([]);
            }

        } catch (error) {
            console.error("Error fetching recommendations:", error);
            recommendationsDiv.innerHTML = `<p>Error loading recommendations: ${error.message}</p>`;
        }
    }


    // --- Initial State Setup ---
    // Login form is shown by default (HTML/CSS handles hiding others)
    // fetchTitle() is called above.

}); // End DOMContentLoaded
