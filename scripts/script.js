// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Define API URL at the top for consistency
    const API_URL = 'http://localhost:5000'; // Ensure this is correct

    // --- Get DOM Elements ---
    // (Keep all existing element references)
    const loginScreen = document.getElementById('login-screen');
    const loginForm = document.getElementById('login-form');
    const individualRegisterForm = document.getElementById('individual-register-form');
    const groupRegisterForm = document.getElementById('group-register-form');
    const mainAppContent = document.getElementById('main-app-content');
    const loginUserIdInput = document.getElementById('loginUserId');
    const loginButton = document.getElementById('loginButton');
    const loginError = document.getElementById('login-error');
    const showIndividualRegisterLink = document.getElementById('show-individual-register-link');
    const showGroupRegisterLink = document.getElementById('show-group-register-link');
    const registerUserIdInput = document.getElementById('registerUserId');
    const registerNameInput = document.getElementById('registerName');
    const registerAgeInput = document.getElementById('registerAge');
    const registerGenderInput = document.getElementById('registerGender');
    const registerJobInput = document.getElementById('registerJob');
    const registerChildrenInput = document.getElementById('registerChildren');
    const registerChildrenOldInput = document.getElementById('registerChildrenOld');
    const registerChildrenYoungInput = document.getElementById('registerChildrenYoung');
    const registerButton = document.getElementById('registerButton');
    const registerMessage = document.getElementById('register-message');
    const showLoginLinkFromIndividual = document.getElementById('show-login-link-from-individual');
    const groupRegisterNameInput = document.getElementById('groupRegisterName');
    const groupMembersSelect = document.getElementById('groupMembersSelect');
    const groupMembersLoadingError = document.getElementById('group-members-loading-error');
    const groupRegisterButton = document.getElementById('groupRegisterButton');
    const groupRegisterMessage = document.getElementById('group-register-message');
    const showLoginLinkFromGroup = document.getElementById('show-login-link-from-group');
    const greetingDiv = document.getElementById('greeting');
    const recommendationsDiv = document.getElementById('recommendations');
    const numRecommendationsSelect = document.getElementById('numRecommendations');
    const recommendationTypeCheckboxes = document.querySelectorAll('input[name="recommendationType"]');

    // --- State Variables ---
    let N = parseInt(numRecommendationsSelect.value);
    let group_recommendations_flag = false;
    let currentUserId = null;
    let groupData = null;

    numRecommendationsSelect.addEventListener('change', handleNChange);

    // --- Helper Functions ---

    function showLoginForm() {
        loginForm.style.display = 'block';
        individualRegisterForm.style.display = 'none';
        groupRegisterForm.style.display = 'none';
        mainAppContent.style.display = 'none';
        loginScreen.style.display = 'flex';
        clearMessages();
    }

    function showIndividualRegisterForm() {
        loginForm.style.display = 'none';
        individualRegisterForm.style.display = 'block';
        groupRegisterForm.style.display = 'none';
        mainAppContent.style.display = 'none';
        loginScreen.style.display = 'flex';
        clearMessages();
    }

    async function showGroupRegisterForm() {
        console.log("Attempting to show group registration form...");
        loginForm.style.display = 'none';
        individualRegisterForm.style.display = 'none';
        groupRegisterForm.style.display = 'block';
        mainAppContent.style.display = 'none';
        loginScreen.style.display = 'flex';
        clearMessages();
        groupMembersLoadingError.style.display = 'none';
        groupMembersSelect.innerHTML = '<option value="" disabled>Loading available users...</option>';
        groupMembersSelect.disabled = true; // Explicitly disable select while loading
        groupRegisterButton.disabled = true;
        console.log("Group form shown, select disabled, button disabled. Fetching users...");

        try {
            const users = await fetchIndividualUsers();
            console.log("Users fetched successfully:", users);
            populateUserDropdown(users);
            // Enable button ONLY if users were loaded successfully AND there are users to select
            groupRegisterButton.disabled = !users || users.length === 0;
            console.log(`Group register button disabled state: ${groupRegisterButton.disabled}`);

        } catch (error) {
            console.error("Error fetching or populating users:", error);
            groupMembersLoadingError.textContent = `Failed to load users: ${error.message}. Cannot register group.`;
            groupMembersLoadingError.style.display = 'block';
            groupMembersSelect.innerHTML = '<option value="" disabled>Error loading users</option>';
            groupMembersSelect.disabled = true; // Keep select disabled on error
            groupRegisterButton.disabled = true; // Keep button disabled on error
            console.log("Error loading users. Select and button remain disabled.");
        }
    }

    async function fetchIndividualUsers() {
        console.log(`Fetching individual users from ${API_URL}/get_individual_users`);
        const response = await fetch(`${API_URL}/get_individual_users`);
        console.log(`Fetch response status: ${response.status}`);
        if (!response.ok) {
            let errorMsg = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                console.error("Error response data:", errorData);
                errorMsg = errorData.error || errorData.message || errorMsg;
            } catch (e) { console.error("Could not parse error response JSON", e) }
            throw new Error(errorMsg);
        }
        const data = await response.json();
        console.log("Raw data received from /get_individual_users:", data);
        // Adjust based on backend response structure - IMPORTANT!
        const userList = data.users || data || [];
        console.log("Parsed user list:", userList);
        return userList;
    }

    function populateUserDropdown(users) {
        groupMembersSelect.innerHTML = ''; // Clear existing options
        console.log("Populating user dropdown with:", users);

        if (!users || users.length === 0) {
            console.log("No users found or provided.");
            groupMembersSelect.innerHTML = '<option value="" disabled>No individual users found</option>';
            groupMembersSelect.disabled = true; // Keep disabled if no users
            console.log("Select populated with 'No users found' and remains disabled.");
            return;
        }

        let optionsAdded = 0;
        users.forEach((user, index) => {
            console.log(`Processing user ${index}:`, user);
            if (user && user.user_id !== undefined && user.user_id !== null && user.name) { // Check user_id exists and is not null/undefined
                 const option = document.createElement('option');
                 option.value = user.user_id;
                 option.textContent = `${user.name} (${user.user_id})`;
                 groupMembersSelect.appendChild(option);
                 optionsAdded++;
                 console.log(`Added option: value="${option.value}", text="${option.textContent}"`);
            } else {
                console.warn(`Skipping invalid user object at index ${index}:`, user);
            }
        });

        // Enable the select ONLY if valid options were actually added
        if (optionsAdded > 0) {
            groupMembersSelect.disabled = false;
            console.log(`Successfully added ${optionsAdded} options. Select element ENABLED.`);
        } else {
            groupMembersSelect.innerHTML = '<option value="" disabled>No valid users found</option>';
            groupMembersSelect.disabled = true;
            console.log("No valid options were added. Select populated with 'No valid users' and remains disabled.");
        }
    }

    function showMainApp() {
        loginScreen.style.display = 'none';
        mainAppContent.style.display = 'block';
        clearMessages();
    }

    function clearMessages() {
        loginError.textContent = '';
        registerMessage.textContent = '';
        registerMessage.className = 'form-message';
        groupRegisterMessage.textContent = '';
        groupRegisterMessage.className = 'form-message';
        groupMembersLoadingError.textContent = '';
        groupMembersLoadingError.style.display = 'none';
    }

    function displayMessage(element, message, isSuccess = false) {
        element.textContent = message;
        element.className = isSuccess ? 'form-message success' : 'form-message';
        element.style.display = 'block';
    }

    // --- Event Handlers ---

    function handleLogin() {
        const userId = loginUserIdInput.value.trim();

        loginError.textContent = ''; // Clear previous errors
        loginError.classList.remove('success'); // Ensure not green

        if (!userId) {
            loginError.textContent = 'Por favor, ingrese su ID de usuario.';
            return;
        }

        // --- !!! IMPORTANT: LOGIN VALIDATION ---
        // Replace this with your actual validation logic (e.g., API call to /login)

        // Login Successful
        currentUserId = userId;
        greetingDiv.textContent = `Welcome, User ${currentUserId}!`;

        loginScreen.style.display = 'none';
        mainAppContent.style.display = 'block';

        recommendationsDiv.innerHTML = '<p>Loading recommendations...</p>';
        getRecommendations(currentUserId);

    }

    async function handleIndividualRegister(event) {
        event.preventDefault();
        clearMessages();
        // (Keep validation and data gathering as before)
        const userId = registerUserIdInput.value.trim();
        const name = registerNameInput.value.trim();
        const age = registerAgeInput.value.trim();
        const gender = registerGenderInput.value.trim().toUpperCase();
        const job = registerJobInput.value.trim();
        const children = registerChildrenInput.value.trim();
        const childrenOld = registerChildrenOldInput.value.trim();
        const childrenYoung = registerChildrenYoungInput.value.trim();
        group_recommendations_flag = false;

        if (!userId || !name || !age || !gender || !job || !children) {
            displayMessage(registerMessage, 'Por favor, rellene todos los campos obligatorios.'); return;
        }
        if (!['M', 'F'].includes(gender)) {
             displayMessage(registerMessage, 'Gender must be M or F.'); return;
        }
         if (!['0', '1'].includes(children)) {
             displayMessage(registerMessage, 'Children field must be 0 or 1.'); return;
        }
        // Add more validation if needed (e.g., age/job are numbers)

        const registrationData = {
            user_id: userId, name: name, age: parseInt(age), gender: gender, job: parseInt(job),
            children: parseInt(children), children_old: childrenOld ? parseInt(childrenOld) : null,
            children_young: childrenYoung ? parseInt(childrenYoung) : null, is_group: false
        };
        console.log("Attempting individual registration with data:", registrationData);

        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(registrationData)
            });
            const data = await response.json();
            console.log("Individual registration response:", data);

            if (response.ok) {
                console.log("Individual registration successful. Redirecting to rate preferences...");
                displayMessage(registerMessage, data.message || 'Registration successful! Redirecting...', true);
                localStorage.setItem('userId', userId); // Store ID for rating page
                setTimeout(() => { window.location.href = 'rate_preferences.html'; }, 1500);
            } else {
                console.error("Individual registration failed:", data.message || data.error);
                displayMessage(registerMessage, data.message || data.error || 'Registration failed.');
            }
        } catch (error) {
            console.error('Individual Registration Fetch Error:', error);
            displayMessage(registerMessage, 'An error occurred during registration.');
        }
    }

    async function handleGroupRegister(event) {
        event.preventDefault();
        clearMessages();
        // (Keep validation and data gathering as before)
        const groupName = groupRegisterNameInput.value.trim();
        const selectedMemberOptions = Array.from(groupMembersSelect.selectedOptions);
        const selectedMemberIds = selectedMemberOptions.map(option => option.value);
        group_recommendations_flag = true;
        console.log("Selected member IDs:", selectedMemberIds); // Log selected IDs

        if (!groupName) {
            displayMessage(groupRegisterMessage, 'Por favor, rellene todos los campos (Ctrl+Click para seleccionar varios usuarios).'); return;
        }
        if (selectedMemberIds.length === 0) {
            // Check if the select is actually enabled and has options
            if (groupMembersSelect.disabled || groupMembersSelect.options.length === 0 || groupMembersSelect.options[0]?.disabled) {
                 displayMessage(groupRegisterMessage, 'Cannot register group: Members list is not available or empty.');
            } else {
                 displayMessage(groupRegisterMessage, 'Please select at least one member for the group.');
            }
            return;
        }

        groupData = {
            name: groupName,
            is_group: true, members: selectedMemberIds
        };
        console.log("Attempting group registration with data:", groupData);

        greetingDiv.textContent = `Welcome, User ${groupName}!`;

        loginScreen.style.display = 'none';
        mainAppContent.style.display = 'block';

        recommendationsDiv.innerHTML = '<p>Loading recommendations...</p>';
        getGroupRecommendations(groupData);
    }

    function handleNChange() {
        N = parseInt(numRecommendationsSelect.value); // Update the global N
        console.log("Number of recommendations changed to:", N);
        if (group_recommendations_flag && groupData) {
            getGroupRecommendations(groupData);
        }
        else{
            if (currentUserId) { // Only fetch if a user is logged in
                getRecommendations(currentUserId);
            }
        }
    }

    // --- Recommendation Fetching and Display Logic ---

    function displayGreeting(name) {
        if (greetingDiv) {
            greetingDiv.textContent = `Welcome, ${name}!`;
        }
    }

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

    async function getGroupRecommendations(group_data) {

        const typeCheckboxes = document.querySelectorAll('input[name="recommendationType"]:checked');
        const selectedTypes = Array.from(typeCheckboxes).map(checkbox => checkbox.value);

        console.log(`Fetching ${N} recommendations for group ${group_data.name} (Types: ${selectedTypes.join(', ') || 'None'})`);

        if (selectedTypes.length === 0) {
            console.warn("No recommendation type selected.");
            // Decide if you want to proceed or show a message
            // recommendationsDiv.innerHTML = "<p>Please select at least one recommendation type.</p>";
            // return;
        }

        recommendationsDiv.innerHTML = '<p>Loading recommendations...</p>';

        try {
            const response = await fetch("http://127.0.0.1:5000/group_recommendations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    users: group_data.members,
                    group_name: group_data.name,
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


    
    
    function handleTypeChange() {
        if (group_recommendations_flag && groupData) {
            getGroupRecommendations(groupData);
        }
        else{
            if (currentUserId) { // Only fetch if a user is logged in
                getRecommendations(currentUserId);
            }
        }
    }

    // --- Add Event Listeners ---
    // (Keep structure as before)
    if (showIndividualRegisterLink) { showIndividualRegisterLink.addEventListener('click', (e) => { e.preventDefault(); showIndividualRegisterForm(); }); }
    if (showGroupRegisterLink) { showGroupRegisterLink.addEventListener('click', async (e) => { e.preventDefault(); await showGroupRegisterForm(); }); }
    if (showLoginLinkFromIndividual) { showLoginLinkFromIndividual.addEventListener('click', (e) => { e.preventDefault(); showLoginForm(); }); }
    if (showLoginLinkFromGroup) { showLoginLinkFromGroup.addEventListener('click', (e) => { e.preventDefault(); showLoginForm(); }); }
    if (loginButton) { loginButton.addEventListener('click', handleLogin); }
    if (registerButton) { registerButton.addEventListener('click', handleIndividualRegister); }
    if (groupRegisterButton) { groupRegisterButton.addEventListener('click', handleGroupRegister); }
    if (numRecommendationsSelect) { numRecommendationsSelect.addEventListener('change', handleNChange); }
    if (recommendationTypeCheckboxes) { recommendationTypeCheckboxes.forEach(checkbox => { checkbox.addEventListener('change', handleTypeChange); }); }

    // --- Initial State ---
    // (Keep structure as before)
    const storedUserId = localStorage.getItem('userId');
    const storedUserName = localStorage.getItem('userName');
    if (storedUserId && storedUserName) {
        console.log(`Found stored user: ${storedUserName} (${storedUserId}). Showing main app.`);
        currentUserId = storedUserId;
        displayGreeting(storedUserName);
        showMainApp();
        fetchRecommendations();
    } else {
        console.log("No stored user found. Showing login form.");
        showLoginForm();
    }

}); // End DOMContentLoaded
