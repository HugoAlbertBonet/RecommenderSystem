document.addEventListener('DOMContentLoaded', () => {
    // Configuration
    const API_URL = 'http://localhost:5000'; // Adjust if your backend runs elsewhere

    // DOM Elements
    const preferencesListDiv = document.getElementById('preferencesList');
    const ratingsForm = document.getElementById('ratingsForm');
    const submitButton = document.getElementById('submitButton');
    const errorMessageDiv = document.getElementById('errorMessage');
    const successMessageDiv = document.getElementById('successMessage');

    let fetchedPreferences = []; // To store the fetched preferences data

    // --- Helper Functions ---
    function displayMessage(element, message, isError = true) {
        element.textContent = message;
        element.style.display = 'block';
        // Hide the other message type
        if (isError) {
            successMessageDiv.style.display = 'none';
        } else {
            errorMessageDiv.style.display = 'none';
        }
    }

    function clearMessages() {
        errorMessageDiv.style.display = 'none';
        successMessageDiv.style.display = 'none';
        errorMessageDiv.textContent = '';
        successMessageDiv.textContent = '';
    }

    function setLoadingState(isLoading, buttonText = 'Submit Ratings') {
        submitButton.disabled = isLoading;
        submitButton.textContent = isLoading ? 'Processing...' : buttonText;
    }

    // --- Core Logic ---

    // 1. Fetch Preferences from Backend
    async function fetchPreferences() {
        clearMessages();
        preferencesListDiv.innerHTML = '<p class="loading-text">Loading preferences...</p>'; // Show loading indicator
        setLoadingState(true); // Disable submit button while loading

        // Retrieve userId stored during registration
        const userId = localStorage.getItem('userId');
        if (!userId) {
            displayMessage(errorMessageDiv, "User ID not found. Please register or log in again.");
            preferencesListDiv.innerHTML = ''; // Clear loading text
            // Optional: Redirect to registration/login page
            // window.location.href = '/register.html';
            return;
        }

        try {
            const response = await fetch(`${API_URL}/preferences_to_rate`);

            if (!response.ok) {
                // Try to get error message from backend response if possible
                let errorMsg = `HTTP error! Status: ${response.status}`;
                try {
                    const errData = await response.json();
                    errorMsg = errData.error || errorMsg;
                } catch (e) { /* Ignore if response is not JSON */ }
                throw new Error(errorMsg);
            }

            const data = await response.json();

            if (data && data.preferences && data.preferences.length > 0) {
                fetchedPreferences = data.preferences; // Store for later use
                renderPreferences(fetchedPreferences);
                setLoadingState(false); // Enable submit button
            } else {
                preferencesListDiv.innerHTML = '<p>No preferences found to rate.</p>';
                // Keep button disabled if there's nothing to submit
            }

        } catch (error) {
            console.error("Error fetching preferences:", error);
            displayMessage(errorMessageDiv, `Failed to fetch preferences: ${error.message}`);
            preferencesListDiv.innerHTML = ''; // Clear loading text
            // Keep button disabled on error
        }
    }

    // 2. Render Preferences in the Form
    function renderPreferences(preferences) {
        preferencesListDiv.innerHTML = ''; // Clear loading text or previous items
        preferences.forEach(pref => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'preference-item';

            const label = document.createElement('label');
            label.htmlFor = `pref-${pref.id}`;
            label.textContent = `${pref.name}:`;

            const input = document.createElement('input');
            input.type = 'number';
            input.id = `pref-${pref.id}`;
            // Use a data attribute to easily retrieve the preference ID later
            input.dataset.preferenceId = pref.id;
            input.min = '0';
            input.max = '10';
            input.value = '0'; // Default rating
            input.required = true; // HTML5 validation

            itemDiv.appendChild(label);
            itemDiv.appendChild(input);
            preferencesListDiv.appendChild(itemDiv);
        });
    }

    // 3. Handle Form Submission
    ratingsForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default HTML form submission
        clearMessages();
        setLoadingState(true, 'Submitting...');

        const userId = localStorage.getItem('userId');
        if (!userId) {
            displayMessage(errorMessageDiv, "User ID missing. Cannot submit ratings.");
            setLoadingState(false);
            return;
        }

        const ratings = {};
        const ratingInputs = preferencesListDiv.querySelectorAll('input[type="number"]');
        let formIsValid = true;
        let totalRatings = 0;

        ratingInputs.forEach(input => {
            const prefId = input.dataset.preferenceId; // Get ID from data attribute
            const value = parseInt(input.value, 10);

            // Basic validation (though 'required', min, max handle some)
            if (isNaN(value) || value < 0 || value > 10) {
                formIsValid = false;
                input.style.border = '1px solid red'; // Highlight invalid input
            } else {
                ratings[prefId] = value;
                input.style.border = '1px solid #ccc'; // Reset border
            }

            if (value !== 0) {
                totalRatings++;
            }
        });

        if (totalRatings < 15 || totalRatings > 25) {
            displayMessage(errorMessageDiv, "Por favor, debes evaluar entre 15 y 25 preferencias.");
            setLoadingState(false);
            return;
        }


        if (!formIsValid) {
            displayMessage(errorMessageDiv, "Please ensure all ratings are valid numbers between 0 and 10.");
            setLoadingState(false);
            return;
        }

        // Construct payload for the backend
        const payload = {
            userId: userId,
            ratings: ratings
        };

        // Send ratings to the backend
        try {
            // *** Make sure you have a '/submit_ratings' endpoint in your backend ***
            const response = await fetch(`${API_URL}/submit_ratings`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json(); // Try to parse JSON response

            if (!response.ok) {
                 throw new Error(result.error || `Server error: ${response.status}`);
            }

            displayMessage(successMessageDiv, "Ratings submitted successfully! Redirecting...", false);

            // Redirect to recommendations page (or dashboard) after a delay
            setTimeout(() => {
                // *** CHANGE '/recommendations.html' TO YOUR ACTUAL NEXT PAGE ***
                window.location.href = 'index.html';
            }, 1500); // 1.5 second delay

            // Don't reset loading state here as we are redirecting

        } catch (error) {
            console.error("Error submitting ratings:", error);
            displayMessage(errorMessageDiv, `Failed to submit ratings: ${error.message}`);
            setLoadingState(false); // Re-enable button on error
        }
    });

    // --- Initial Load ---
    fetchPreferences();

}); // End DOMContentLoaded
