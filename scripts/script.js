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
    // → Nuevo bloque para visitas
    const visitsForm          = document.getElementById('visits-form');
    const visitsQuestionsDiv  = document.getElementById('visits-questions');
    const submitVisitsButton  = document.getElementById('submitVisitsButton');
    const visitsMessage       = document.getElementById('visits-message');


    // ► Aquí pegas tu nuevo bloque ◄
    // Elementos del dropdown de usuario
    const userSelect  = document.getElementById('userSelect');
    const userDetails = document.getElementById('userDetails');
    const prefsList   = document.getElementById('prefsList');
    const visitsList  = document.getElementById('visitsList');

    // 1) Rellenar el dropdown con usuarios
    async function populateUserSelect() {
      const resp = await fetch(`${API_URL}/get_individual_users`);
      const { users } = await resp.json();
      users.forEach(u => {
        const opt = document.createElement('option');
        opt.value = u.user_id;
        opt.textContent = `${u.name} (${u.user_id})`;
        userSelect.appendChild(opt);
      });
    }

    // 2) Al cambiar de usuario, mostrar preferencias y visitas
    userSelect.addEventListener('change', async () => {
      const uid = userSelect.value;
      if (!uid) return;
      userDetails.style.display = 'block';
      prefsList.innerHTML  = '<li>Cargando…</li>';
      visitsList.innerHTML = '<li>Cargando…</li>';

      // Fetch preferencias
      try {
        const res1 = await fetch(`${API_URL}/user_preferences/${uid}`);
        const { preferences } = await res1.json();
        prefsList.innerHTML = preferences.length
          ? preferences.map(p => `<li>${p.name} (Score: ${p.score})</li>`).join('')
          : '<li>No hay preferencias positivas.</li>';
      } catch {
        prefsList.innerHTML = '<li>Error al cargar preferencias.</li>';
      }

      // Fetch visitas
      try {
        const res2 = await fetch(`${API_URL}/user_visits/${uid}`);
        const { visits } = await res2.json();
        visitsList.innerHTML = visits.length
          ? visits.map(v => `<li>${v.name_item} – Val: ${v.valoracion}, Visitas: ${v.visitas}</li>`).join('')
          : '<li>No hay visitas registradas.</li>';
      } catch {
        visitsList.innerHTML = '<li>Error al cargar visitas.</li>';
      }
    });

    // Inicializar al cargar la página
    populateUserSelect();
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
  async function populateEvalUsers() {
    try {
        const response = await fetch(`${API_URL}/get_individual_users`);
        if (!response.ok) throw new Error('Failed to fetch users for evaluation.');
        const data = await response.json();
        const users = data.users || [];

        evalUsersSelect.innerHTML = ''; // Limpia anteriores
        users.forEach(user => {
            if (user && user.user_id && user.name) {
                const option = document.createElement('option');
                option.value = user.user_id;
                option.textContent = `${user.name} (${user.user_id})`;
                evalUsersSelect.appendChild(option);
            }
        });

        if (users.length === 0) {
            evalUsersSelect.innerHTML = '<option disabled>No users found</option>';
        }
    } catch (error) {
        console.error('Error loading evaluation users:', error);
        evalUsersSelect.innerHTML = '<option disabled>Error loading users</option>';
    }
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

    async function loadVisitsQuestions(userId) {
        const resp = await fetch(`${API_URL}/visits_to_rate?userId=${userId}`);
        const { items } = await resp.json();
        visitsQuestionsDiv.innerHTML = '';
        items.forEach(item => {
          visitsQuestionsDiv.innerHTML += `
            <div class="visit-question">
              <p>¿Has visitado "<strong>${item.name}</strong>"?</p>
              <select data-id-item="${item.id_item}" class="visit-select">
                <option value="">Seleccione</option>
                <option value="no">No</option>
                <option value="yes">Sí</option>
              </select>
              <div class="rating-input" style="display:none; margin-top:5px;">
                <label>Valoración (1–7):</label>
                <input type="number" min="1" max="7" data-id-item="${item.id_item}" class="rating-input-field">
              </div>
            </div>
          `;
        });
      }

    
      

    function displayMessage(element, message, isSuccess = false) {
        element.textContent = message;
        element.className = isSuccess ? 'form-message success' : 'form-message';
        element.style.display = 'block';
    }
  
    // --- Event Handlers ---

    async function handleLogin() {
        const userId = loginUserIdInput.value.trim();
        loginError.textContent = '';
    
        if (!userId) {
            loginError.textContent = 'Por favor, ingrese su ID de usuario.';
            return;
        }
    
        // Login “exitoso”
        currentUserId = userId;
        greetingDiv.textContent = `Welcome, User ${currentUserId}!`;
    
        // 1) Ocultamos SOLO los formularios de login/registro,
        //    NO todo #login-screen
        loginForm.style.display = 'none';
        individualRegisterForm.style.display = 'none';
        groupRegisterForm.style.display = 'none';
    
        // 2) Comprobamos si ya hay visitas registradas
        let hasVisits = false;
        try {
            const resp = await fetch(`${API_URL}/user_visits/${currentUserId}`);
            if (resp.ok) {
                const { visits } = await resp.json();
                hasVisits = Array.isArray(visits) && visits.length > 0;
            }
        } catch (err) {
            console.error('Error comprobando visitas:', err);
            // si falla la llamada, asumimos que tiene visitas para no bloquear el flujo
            hasVisits = true;
        }
    
        if (!hasVisits) {
            // 3) Usuario nuevo: mostramos el form de visitas dentro de #login-screen
            visitsForm.style.display = 'block';
            loadVisitsQuestions(currentUserId);
            return;
        }
    
        // 4) Usuario con visitas: cerramos #login-screen y entramos en la app
        loginScreen.style.display = 'none';
        showMainApp();
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
   // Create a card for each recommendation, using all returned fields
// --- Create Place Element Function ---

function createPlaceElement(item) {
    const placeDiv = document.createElement("div");
    placeDiv.classList.add("place");
  
    // Título
    const h3 = document.createElement("h3");
    h3.textContent = item.name;
    placeDiv.appendChild(h3);
  
    // Score híbrido
    const scoreP = document.createElement("p");
    scoreP.textContent = `Score combinado: ${item.hybrid_score.toFixed(3)}`;
    placeDiv.appendChild(scoreP);
  
    // Bloque de explicación
    const exp = document.createElement("div");
    exp.classList.add("explanation");
    let html = "";
  
    // ─── CONTENT ────────────────────────────────────
    if (item.sim_score !== undefined) {
      html += `
        <span style="color:#1976d2;">● Similitud preferencias:</span> ${item.sim_score.toFixed(3)}<br>
        <span style="color:#1976d2;">● Concordancia historial:</span> ${item.hist_score.toFixed(3)}<br>
        <span style="color:#1976d2;">● Popularidad (visitas):</span> ${item.vis_score.toFixed(3)}<br>
      `;
    }
  
    // ─── COLLABORATIVE ──────────────────────────────
    if (item.neighbor_count !== undefined) {
      html += `
        <span style="color:#ff5722;">■ Vecinos considerados:</span> ${item.neighbor_count}<br>
        <span style="color:#ff5722;">■ Media rating vecinos:</span> ${item.neighbor_mean_rating.toFixed(2)}<br>
      `;
    }
  
    // ─── DEMOGRAPHIC  (nuevo) ───────────────────────
    if (item.group !== undefined) {
      html += `
        <span style="color:#9c27b0;">◆ Grupo demográfico:</span> ${item.group}<br>
        <span style="color:#9c27b0;">◆ Justificación:</span> ${item.explanation}<br>
      `;
    }
  
    exp.innerHTML = html;
    placeDiv.appendChild(exp);
  
    return placeDiv;
  }
  
      
  
  
  // --- Display Recommendations Function ---
  function displayRecommendations(recommendations) {
    recommendationsDiv.innerHTML = ""; // Limpia
  
    if (!Array.isArray(recommendations) || recommendations.length === 0) {
      recommendationsDiv.innerHTML = "<p>No se encontraron recomendaciones.</p>";
      return;
    }
  
    recommendations.forEach(item => {
      const card = createPlaceElement(item);
      recommendationsDiv.appendChild(card);
    });
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

    visitsQuestionsDiv.addEventListener('change', e => {
        if (e.target.classList.contains('visit-select')) {
          const id = e.target.dataset.idItem;
          const ratingDiv = e.target.closest('.visit-question').querySelector('.rating-input');
          ratingDiv.style.display = e.target.value === 'yes' ? 'block' : 'none';
        }
      });
      submitVisitsButton.addEventListener('click', async () => {
        const visitsData = [];
        document.querySelectorAll('.visit-question').forEach(div => {
          const sel = div.querySelector('.visit-select');
          if (sel.value === 'yes') {
            const val = div.querySelector('.rating-input-field').value;
            visitsData.push({
              id_item:   parseInt(sel.dataset.idItem),
              valoracion: parseInt(val)
            });
          }
        });
        const resp = await fetch(`${API_URL}/submit_visits`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId: currentUserId,
            visits: visitsData
          })
        });
        const data = await resp.json();
        if (resp.ok) {
          visitsMessage.textContent = 'Visitas registradas correctamente.';
          visitsMessage.className = 'form-message success';
          setTimeout(() => {
            visitsForm.style.display = 'none';
            showMainApp();
            getRecommendations(currentUserId);
          }, 1000);
        } else {
          visitsMessage.textContent = `Error: ${data.error}`;
          visitsMessage.className = 'form-message';
        }
      });
      
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

// --- Evaluación y Gráficos ---
const evaluateButton = document.getElementById('evaluateButton');
const thrRecommendedInput = document.getElementById('thrRecommended');
const thrRelevantInput   = document.getElementById('thrRelevant');
const evalUsersSelect    = document.getElementById('evalUsers');
populateEvalUsers();
// Instancia vacías para luego destruir si vuelves a dibujar
let prChart, f1Chart, maeChart;

evaluateButton.addEventListener('click', async () => {
  const selectedOptions = Array.from(evalUsersSelect.selectedOptions);
  const userIds = selectedOptions.map(o => o.value);
  const types   = Array.from(document.querySelectorAll('input[name="recommendationType"]:checked'))
                         .map(cb => cb.value);
  const n       = parseInt(numRecommendationsSelect.value);
  const thrRec = parseFloat(
    thrRecommendedInput.value.trim().replace(',', '.')
  );
  const thrRel = parseFloat(
    thrRelevantInput.value.trim().replace(',', '.')
  );

  if (userIds.length === 0) {
    alert('Selecciona al menos un usuario para evaluar.');
    return;
  }
  if (types.length === 0) {
    alert('Selecciona al menos un tipo de recomendación.');
    return;
  }

  try {
    console.log("Intentando hacer fetch a:", `${API_URL}/evaluate`);
    console.log("Body que se envía:", {
      userIds: userIds,
      recommendation_types: types,
      num_recommendations: n,
      threshold_recommended: thrRec,
      threshold_relevant: thrRel
    });

    const resp = await fetch(`${API_URL}/evaluate`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        userIds: userIds,
        recommendation_types: types,
        num_recommendations: n,
        threshold_recommended: thrRec,
        threshold_relevant: thrRel
      })
    });

    console.log("Estado HTTP:", resp.status);

    if (!resp.ok) {
      const errorResponse = await resp.text();
      console.error("Respuesta de error recibida:", errorResponse);
      throw new Error(`Fetch fallido: ${resp.status} - ${errorResponse}`);
    }

    const { metrics } = await resp.json();
    console.log("Métricas recibidas:", metrics);

    // Prepara etiquetas y datasets
    const algos = Object.keys(metrics);
    const labels = userIds;
    const prDatasets = [], f1Datasets = [], maeDatasets = [];

    algos.forEach(algo => {
      const precisions = labels.map(uid => metrics[algo][uid].precision);
      const recalls    = labels.map(uid => metrics[algo][uid].recall);
      const f1s        = labels.map(uid => metrics[algo][uid].f1);
      const maes       = labels.map(uid => metrics[algo][uid].mae ?? 0);

      prDatasets.push({
        label: `${algo} - Precisión`,
        data: precisions,
        fill: false,
        tension: 0.1
      });
      prDatasets.push({
        label: `${algo} - Recall`,
        data: recalls,
        fill: false,
        tension: 0.1
      });
      f1Datasets.push({
        label: algo,
        data: f1s,
        fill: false,
        tension: 0.1
      });
      maeDatasets.push({
        label: algo,
        data: maes,
        fill: false,
        tension: 0.1
      });
    });

    if (prChart) prChart.destroy();
    if (f1Chart) f1Chart.destroy();
    if (maeChart) maeChart.destroy();

    prChart = new Chart(
      document.getElementById('precisionRecallChart').getContext('2d'),
      {
        type: 'line',
        data: { labels, datasets: prDatasets },
        options: {
          plugins: { title: { display: true, text: 'Precisión y Recall por Usuario' } },
          scales: { y: { beginAtZero: true, max: 1 } }
        }
      }
    );

    f1Chart = new Chart(
      document.getElementById('f1Chart').getContext('2d'),
      {
        type: 'line',
        data: { labels, datasets: f1Datasets },
        options: {
          plugins: { title: { display: true, text: 'F1-Score por Usuario' } },
          scales: { y: { beginAtZero: true, max: 1 } }
        }
      }
    );

    maeChart = new Chart(
      document.getElementById('maeChart').getContext('2d'),
      {
        type: 'line',
        data: { labels, datasets: maeDatasets },
        options: {
          plugins: { title: { display: true, text: 'MAE por Usuario' } },
          scales: { y: { beginAtZero: true } }
        }
      }
    );

  } catch (err) {
    console.error('❌ Error en evaluación:', err);
    alert('❌ Error al obtener métricas: ' + err.message);
  }
});


}); // End DOMContentLoaded
