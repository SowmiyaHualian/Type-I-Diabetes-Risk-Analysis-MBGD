(() => {
  const AUTH_KEY = 'userLoggedIn';
  const USER_KEY = 'user';
  const USERS_KEY = 'registeredUsers';
  const FORM_KEY = 'riskFormData';
  const ANALYSIS_KEY = 'riskAnalysis';

  const routeToFile = {
    '/': 'index.html',
    '/login': 'login.html',
    '/register': 'register.html',
    '/about': 'about.html',
    '/contact': 'contact.html',
    '/dashboard': 'dashboard.html',
    '/result': 'result.html',
  };

  const fileToRoute = {
    '': '/',
    'index.html': '/',
    'login.html': '/login',
    'register.html': '/register',
    'about.html': '/about',
    'contact.html': '/contact',
    'dashboard.html': '/dashboard',
    'result.html': '/result',
  };

  const enforceAuthEarly = () => {
    const route = getCurrentRoute();
    const requiresAuthEarly = ['/dashboard', '/result'].includes(route);
    if (requiresAuthEarly && !isLoggedIn()) {
      window.location.href = routeToFile['/login'];
    }
  };

  const getCurrentRoute = () => {
    const fileName = window.location.pathname.split('/').pop();
    return fileToRoute[fileName] || '/';
  };

  const isLoggedIn = () => {
    if (localStorage.getItem(AUTH_KEY) === 'true') return true;
    const serverAuth = document.body?.getAttribute('data-server-auth');
    return serverAuth === 'true';
  };

  const getUser = () => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  };

  const loadUsers = () => {
    const raw = localStorage.getItem(USERS_KEY);
    try {
      return raw ? JSON.parse(raw) : [];
    } catch (err) {
      console.error('Failed to parse users', err);
      return [];
    }
  };

  const saveUsers = (users) => {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
  };

  const findUserByEmail = (email) => {
    const users = loadUsers();
    return users.find((u) => u.email.toLowerCase() === email.toLowerCase()) || null;
  };

  const login = (user) => {
    localStorage.setItem(AUTH_KEY, 'true');
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  };

  const logout = () => {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
  };

  const caduceusSvg = (className, color) => {
    return `<img src="https://i.ebayimg.com/images/g/SCsAAOSwOwJjapHJ/s-l400.jpg" alt="Caduceus Logo" class="${className} rounded-full object-cover" />`;
  };

  const renderNavbar = () => {
    const container = document.getElementById('navbar');
    if (!container) return;

    const loggedIn = isLoggedIn();
    const currentRoute = getCurrentRoute();

    const navLinks = loggedIn
      ? [
          { name: 'Home', path: '/' },
          { name: 'Assessment', path: '/dashboard' },
          { name: 'About', path: '/about' },
          { name: 'Contact', path: '/contact' },
        ]
      : [
          { name: 'Home', path: '/' },
          { name: 'About', path: '/about' },
          { name: 'Contact', path: '/contact' },
        ];

    const linkClass = (path) =>
      currentRoute === path
        ? 'text-[#3AB8C1] bg-[#0F6C74]/20'
        : 'text-slate-300 hover:text-[#3AB8C1] hover:bg-[#0F6C74]/15';

    const navLinksHtml = navLinks
      .map(
        (link) =>
          `<a href="${routeToFile[link.path]}" class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${linkClass(
            link.path
          )}">${link.name}</a>`
      )
      .join('');

    const userName = (() => {
      const stored = getUser();
      if (stored?.name) return stored.name;
      const bodyName = document.body?.dataset?.userName;
      if (bodyName) return bodyName;
      return '';
    })();

    const userEmail = (() => {
      const stored = getUser();
      if (stored?.email) return stored.email;
      const bodyEmail = document.body?.dataset?.userEmail;
      if (bodyEmail) return bodyEmail;
      return '';
    })();

    const userDisplay = userName || userEmail;

    const userMenu = loggedIn
      ? `
        <div class="relative" id="user-menu">
          <button id="user-menu-button" class="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white transition-all">
            <div class="w-9 h-9 rounded-full bg-gradient-to-br from-[#3AB8C1] to-[#0F6C74] text-white flex items-center justify-center font-semibold">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A9 9 0 1118.88 6.196M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </div>
            <div class="text-left leading-tight">
              <div class="text-xs text-slate-200">Signed in</div>
              <div class="text-sm font-semibold">${userDisplay || 'Account'}</div>
            </div>
            <svg class="w-4 h-4 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </button>
          <div id="user-dropdown" class="hidden absolute right-0 mt-2 w-44 rounded-lg bg-white text-slate-800 shadow-lg border border-slate-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-slate-100">
              <p class="text-xs text-slate-500">Signed in as</p>
              <p class="text-sm font-semibold text-[#083A40] truncate">${userDisplay || 'Account'}</p>
            </div>
            <button data-logout class="w-full text-left px-4 py-3 text-sm hover:bg-slate-100 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1" /></svg>
              Logout
            </button>
          </div>
        </div>
      `
      : `
        <a href="${routeToFile['/login']}" class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${linkClass(
          '/login'
        )}">Login</a>
        <a href="${routeToFile['/register']}" class="px-5 py-2 bg-[#0F6C74] text-white text-sm font-semibold rounded-lg transition-all duration-300 hover:bg-[#084A52] hover:shadow-lg hover:shadow-[#0F6C74]/40">Register</a>
      `;

    const authLinksHtml = userMenu;

    const mobileLinksHtml = navLinks
      .map(
        (link) =>
          `<a href="${routeToFile[link.path]}" class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${linkClass(
            link.path
          )}">${link.name}</a>`
      )
      .join('');

    const mobileAuthHtml = loggedIn
      ? `<button data-logout class="w-full px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-lg text-left">Logout</button>`
      : `
        <a href="${routeToFile['/login']}" class="px-4 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-[#3AB8C1] hover:bg-[#0F6C74]/15 transition-all">Login</a>
        <a href="${routeToFile['/register']}" class="px-4 py-2 bg-[#0F6C74] text-white text-sm font-semibold rounded-lg text-center">Register</a>
      `;

    container.innerHTML = `
      <nav class="fixed top-0 left-0 right-0 z-50 bg-[#083A40] border-b border-[#0F6C74]/20 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <a href="${routeToFile['/']}" class="flex items-center gap-3 group">
              <div class="relative">
                <div class="absolute inset-0 rounded-full bg-[#3AB8C1]/20 blur-md group-hover:bg-[#3AB8C1]/35 transition-all duration-300"></div>
                <div class="relative rounded-full bg-gradient-to-br from-[#F5FBFC] to-[#E8F5F7] p-1.5 border border-[#0F6C74]/30">
                  ${caduceusSvg('w-9 h-9', '#0F6C74')}
                </div>
              </div>
              <span class="text-white font-bold text-sm tracking-wide leading-tight">T1D care</span>
            </a>

            <div class="hidden md:flex items-center gap-1">
              ${navLinksHtml}
              <div class="w-px h-6 bg-[#0F6C74]/40 mx-2"></div>
              ${authLinksHtml}
            </div>

            <button id="nav-toggle" class="md:hidden text-slate-300 hover:text-[#3AB8C1] p-2 transition-colors" aria-label="Toggle menu">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>

          <div id="nav-mobile" class="md:hidden hidden pb-4 border-t border-[#0F6C74]/20 mt-2 pt-4 animate-fade-in">
            <div class="flex flex-col gap-2">
              ${mobileLinksHtml}
              <div class="h-px bg-[#0F6C74]/30 my-2"></div>
              ${mobileAuthHtml}
            </div>
          </div>
        </div>
      </nav>
    `;

    const toggle = document.getElementById('nav-toggle');
    const mobileMenu = document.getElementById('nav-mobile');
    if (toggle && mobileMenu) {
      toggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
      });
    }

    const logoutButtons = container.querySelectorAll('[data-logout]');
    logoutButtons.forEach((button) => {
      button.addEventListener('click', () => {
        logout();
        window.location.href = routeToFile['/login'];
      });
    });

    const userMenuButton = container.querySelector('#user-menu-button');
    const userDropdown = container.querySelector('#user-dropdown');
    if (userMenuButton && userDropdown) {
      userMenuButton.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('hidden');
      });
      document.addEventListener('click', (e) => {
        if (!userDropdown.classList.contains('hidden') && !userMenuButton.contains(e.target)) {
          userDropdown.classList.add('hidden');
        }
      });
    }
  };

  const guardProtected = () => {
    const route = getCurrentRoute();
    const requiresAuth = document.body.getAttribute('data-requires-auth') === 'true' || ['/dashboard', '/result'].includes(route);
    if (requiresAuth && !isLoggedIn()) {
      window.location.href = routeToFile['/login'];
    }
  };

  const setupLoginForm = () => {
    const form = document.getElementById('login-form');
    if (!form || form.dataset.serverPost === 'true') return;

    const errorBox = document.getElementById('login-error');

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = form.querySelector('#email').value.trim();
      const password = form.querySelector('#password').value.trim();

      if (!email || !password) {
        errorBox.textContent = 'Please fill in all fields';
        errorBox.classList.remove('hidden');
        return;
      }

      if (!email.includes('@')) {
        errorBox.textContent = 'Please enter a valid email';
        errorBox.classList.remove('hidden');
        return;
      }

      const existingUser = findUserByEmail(email);

      if (!existingUser) {
        errorBox.textContent = 'Account not found. Please register first.';
        errorBox.classList.remove('hidden');
        return;
      }

      if (existingUser.password !== password) {
        errorBox.textContent = 'Incorrect password.';
        errorBox.classList.remove('hidden');
        return;
      }

      login({ email: existingUser.email, name: existingUser.name });
      window.location.href = routeToFile['/dashboard'];
    });

    form.addEventListener('input', () => {
      errorBox.classList.add('hidden');
      errorBox.textContent = '';
    });
  };

  const setupRegisterForm = () => {
    const form = document.getElementById('register-form');
    if (!form || form.dataset.serverPost === 'true') return;

    const errorBox = document.getElementById('register-error');

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = form.querySelector('#name').value.trim();
      const email = form.querySelector('#email').value.trim();
      const password = form.querySelector('#password').value.trim();
      const confirmPassword = form.querySelector('#confirmPassword').value.trim();

      if (!name || !email || !password || !confirmPassword) {
        errorBox.textContent = 'Please fill in all fields';
        errorBox.classList.remove('hidden');
        return;
      }

      if (!email.includes('@')) {
        errorBox.textContent = 'Please enter a valid email';
        errorBox.classList.remove('hidden');
        return;
      }

      if (password.length < 6) {
        errorBox.textContent = 'Password must be at least 6 characters';
        errorBox.classList.remove('hidden');
        return;
      }

      if (password !== confirmPassword) {
        errorBox.textContent = 'Passwords do not match';
        errorBox.classList.remove('hidden');
        return;
      }

      const existingUser = findUserByEmail(email);
      if (existingUser) {
        errorBox.textContent = 'Account already exists. Please login.';
        errorBox.classList.remove('hidden');
        return;
      }

      const users = loadUsers();
      users.push({ name, email: email.toLowerCase(), password });
      saveUsers(users);

      login({ email: email.toLowerCase(), name });
      window.location.href = routeToFile['/dashboard'];
    });

    form.addEventListener('input', () => {
      errorBox.classList.add('hidden');
      errorBox.textContent = '';
    });
  };

  const setFieldError = (fieldId, message) => {
    const errorEl = document.querySelector(`[data-error="${fieldId}"]`);
    const inputEl = document.getElementById(fieldId);
    if (!errorEl || !inputEl) return;

    if (message) {
      errorEl.textContent = message;
      errorEl.classList.remove('hidden');
      inputEl.classList.remove('border-slate-300');
      inputEl.classList.add('border-red-500');
    } else {
      errorEl.textContent = '';
      errorEl.classList.add('hidden');
      inputEl.classList.remove('border-red-500');
      inputEl.classList.add('border-slate-300');
    }
  };

  const setSymptomError = (message) => {
    const errorEl = document.querySelector('[data-error="symptoms"]');
    if (!errorEl) return;
    if (message) {
      errorEl.textContent = message;
      errorEl.classList.remove('hidden');
    } else {
      errorEl.textContent = '';
      errorEl.classList.add('hidden');
    }
  };

  const calculateRisk = (data) => {
    let indicatorCount = 0;
    const factors = [];

    const fastingGlucose = parseFloat(data.fastingGlucose);
    const randomGlucose = parseFloat(data.randomGlucose);
    const hba1c = parseFloat(data.hba1c);

    if (fastingGlucose >= 126) {
      indicatorCount++;
      factors.push('Elevated fasting blood glucose levels');
    }
    if (randomGlucose >= 200) {
      indicatorCount++;
      factors.push('Elevated random blood glucose levels');
    }
    if (hba1c >= 6.5) {
      indicatorCount++;
      factors.push('Higher HbA1c levels');
    }

    if (data.ketonePresence === 'Present') {
      indicatorCount++;
      factors.push('Presence of ketones');
    }

    let symptomCount = 0;
    const reportedSymptoms = [];
    if (data.symptoms.polyuria) {
      symptomCount++;
      reportedSymptoms.push('Frequent urination (Polyuria)');
    }
    if (data.symptoms.polydipsia) {
      symptomCount++;
      reportedSymptoms.push('Excessive thirst (Polydipsia)');
    }
    if (data.symptoms.weightLoss) {
      symptomCount++;
      reportedSymptoms.push('Unexplained weight loss');
    }
    if (data.symptoms.fatigue) {
      symptomCount++;
      reportedSymptoms.push('Fatigue');
    }
    if (data.symptoms.blurredVision) {
      symptomCount++;
      reportedSymptoms.push('Blurred vision');
    }

    if (symptomCount >= 2) {
      indicatorCount++;
      factors.push(`Reported symptoms: ${reportedSymptoms.join(', ')}`);
    }

    if (data.cPeptideLevel) {
      const cPeptide = parseFloat(data.cPeptideLevel);
      if (cPeptide < 0.8) {
        indicatorCount++;
        factors.push('Low C-peptide levels (suggesting reduced insulin production)');
      }
    }

    if (data.autoantibodyResult === 'Positive') {
      indicatorCount++;
      factors.push('Positive autoantibody test results');
    }

    return {
      hasStrongIndicators: indicatorCount >= 3,
      indicatorCount,
      factors,
      symptomCount,
      reportedSymptoms,
    };
  };

  const setupDashboardForm = () => {
    const form = document.getElementById('dashboard-form');
    if (!form) return;

    const weightInput = form.querySelector('#weightKg');
    const heightInput = form.querySelector('#heightCm');
    const bmiInput = form.querySelector('#bmi');

    const clearButton = document.getElementById('dashboard-clear');

    const getSymptoms = () => {
      const symptoms = {};
      form.querySelectorAll('input[name^="symptoms."]').forEach((input) => {
        const name = input.name.split('.')[1];
        symptoms[name] = input.checked;
      });
      return symptoms;
    };

    const updateBmi = () => {
      if (!weightInput || !heightInput || !bmiInput) return;
      const weight = parseFloat(weightInput.value);
      const heightCm = parseFloat(heightInput.value);
      if (!weight || weight <= 0 || !heightCm || heightCm <= 0) {
        bmiInput.value = '';
        return;
      }
      const heightM = heightCm / 100;
      const bmi = weight / (heightM * heightM);
      const rounded = Math.round(bmi * 10) / 10;
      bmiInput.value = Number.isFinite(rounded) ? rounded.toFixed(1) : '';
    };

    if (weightInput) weightInput.addEventListener('input', updateBmi);
    if (heightInput) heightInput.addEventListener('input', updateBmi);

    const validate = (data) => {
      let isValid = true;

      if (!data.age || isNaN(data.age) || Number(data.age) <= 0) {
        setFieldError('age', 'Please enter a valid age');
        isValid = false;
      } else {
        setFieldError('age', '');
      }

      if (!data.weightKg || isNaN(data.weightKg) || Number(data.weightKg) <= 0) {
        setFieldError('weightKg', 'Please enter a valid weight');
        isValid = false;
      } else {
        setFieldError('weightKg', '');
      }

      if (!data.heightCm || isNaN(data.heightCm) || Number(data.heightCm) <= 0) {
        setFieldError('heightCm', 'Please enter a valid height');
        isValid = false;
      } else {
        setFieldError('heightCm', '');
      }

      updateBmi();

      if (!data.bmi || isNaN(data.bmi) || Number(data.bmi) <= 0) {
        setFieldError('bmi', 'BMI is auto-calculated from weight and height');
        isValid = false;
      } else {
        setFieldError('bmi', '');
      }

      if (!data.fastingGlucose || isNaN(data.fastingGlucose) || Number(data.fastingGlucose) < 0) {
        setFieldError('fastingGlucose', 'Please enter a valid fasting glucose value');
        isValid = false;
      } else {
        setFieldError('fastingGlucose', '');
      }

      if (!data.randomGlucose || isNaN(data.randomGlucose) || Number(data.randomGlucose) < 0) {
        setFieldError('randomGlucose', 'Please enter a valid random glucose value');
        isValid = false;
      } else {
        setFieldError('randomGlucose', '');
      }

      if (!data.hba1c || isNaN(data.hba1c) || Number(data.hba1c) < 0) {
        setFieldError('hba1c', 'Please enter a valid HbA1c value');
        isValid = false;
      } else {
        setFieldError('hba1c', '');
      }

      const hasSymptoms = Object.values(data.symptoms).some((val) => val === true);
      if (!hasSymptoms) {
        setSymptomError('Please select at least one symptom');
        isValid = false;
      } else {
        setSymptomError('');
      }

      return isValid;
    };

    if (form.dataset.serverPost === 'true') {
      // Let the server handle submission, but keep BMI auto-calc active
      return;
    }

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      updateBmi();

      const data = {
        gender: (form.querySelector('input[name="gender"]:checked') || {}).value || '',
        age: form.querySelector('#age').value.trim(),
        weightKg: form.querySelector('#weightKg') ? form.querySelector('#weightKg').value.trim() : '',
        heightCm: form.querySelector('#heightCm') ? form.querySelector('#heightCm').value.trim() : '',
        bmi: form.querySelector('#bmi').value.trim(),
        fastingGlucose: form.querySelector('#fastingGlucose').value.trim(),
        randomGlucose: form.querySelector('#randomGlucose').value.trim(),
        hba1c: form.querySelector('#hba1c').value.trim(),
        ketonePresence: form.querySelector('#ketonePresence').value,
        cPeptideLevel: form.querySelector('#cPeptideLevel').value.trim(),
        autoantibodyResult: form.querySelector('#autoantibodyResult').value,
        symptoms: getSymptoms(),
      };

      if (!validate(data)) {
        return;
      }

      const riskAnalysis = calculateRisk(data);
      sessionStorage.setItem(FORM_KEY, JSON.stringify(data));
      sessionStorage.setItem(ANALYSIS_KEY, JSON.stringify(riskAnalysis));
      window.location.href = routeToFile['/result'];
    });

    if (clearButton) {
      clearButton.addEventListener('click', () => {
        form.reset();
        updateBmi();
        ['age', 'weightKg', 'heightCm', 'bmi', 'fastingGlucose', 'randomGlucose', 'hba1c'].forEach((field) => setFieldError(field, ''));
        setSymptomError('');
      });
    }
  };

  const renderResultPage = () => {
    const container = document.getElementById('result-content');
    const noData = document.getElementById('no-data');
    if (!container || !noData) return;

    const formDataRaw = sessionStorage.getItem(FORM_KEY);
    const riskAnalysisRaw = sessionStorage.getItem(ANALYSIS_KEY);

    if (!formDataRaw || !riskAnalysisRaw) {
      container.classList.add('hidden');
      noData.classList.remove('hidden');
      return;
    }

    const formData = JSON.parse(formDataRaw);
    const riskAnalysis = JSON.parse(riskAnalysisRaw);

    const resultCard = document.getElementById('result-card');
    if (resultCard) {
      resultCard.innerHTML = riskAnalysis.hasStrongIndicators
        ? `
          <div class="bg-gradient-to-br from-[#0F6C74]/10 via-[#3AB8C1]/5 to-white border border-[#0F6C74]/30 rounded-2xl p-10 mb-8 shadow-sm">
            <div class="flex items-start gap-6">
              <div class="p-4 rounded-xl bg-[#0F6C74] flex-shrink-0">
                <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4v2m0 4v2M3 12a9 9 0 1118 0 9 9 0 01-18 0z" />
                </svg>
              </div>
              <div class="flex-1">
                <h2 class="text-2xl font-bold text-[#083A40] mb-3">Possible Early Indicators Observed</h2>
                <p class="text-slate-700 leading-relaxed mb-2">
                  Based on the health information provided, some patterns that are commonly associated with Type 1
                  Diabetes have been observed.
                </p>
                <p class="text-slate-600 text-sm">
                  This does not confirm the presence of the condition, but further medical evaluation may be helpful.
                </p>
              </div>
            </div>
          </div>
        `
        : `
          <div class="bg-gradient-to-br from-[#3AB8C1]/10 via-slate-50 to-white border border-[#3AB8C1]/30 rounded-2xl p-10 mb-8 shadow-sm">
            <div class="flex items-start gap-6">
              <div class="p-4 rounded-xl bg-[#3AB8C1] flex-shrink-0">
                <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1">
                <h2 class="text-2xl font-bold text-[#083A40] mb-3">No Strong Indicators Detected</h2>
                <p class="text-slate-700 leading-relaxed">
                  Based on the information provided, no strong indicators commonly associated with Type 1 Diabetes were
                  observed.
                </p>
              </div>
            </div>
          </div>
        `;
    }

    const glucoseElevated =
      parseFloat(formData.fastingGlucose) >= 126 || parseFloat(formData.randomGlucose) >= 200;

    const summary = document.getElementById('analysis-summary');
    if (summary) {
      summary.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-white rounded-xl border border-slate-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-slate-500 text-sm font-semibold">Blood Glucose Status</p>
                <p class="text-2xl font-bold text-[#083A40] mt-2">${glucoseElevated ? 'Elevated' : 'Normal Range'}</p>
              </div>
              <div class="p-3 rounded-lg ${glucoseElevated ? 'bg-red-100' : 'bg-green-100'}">
                <svg class="w-6 h-6 ${glucoseElevated ? 'text-red-600' : 'text-green-600'}" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                  <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 1 1 0 100 2H6a1 1 0 000-2h-.5A2.5 2.5 0 013.5 7.5h3a1 1 0 100-2h-1V5z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-slate-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-slate-500 text-sm font-semibold">Symptoms Count</p>
                <p class="text-2xl font-bold text-[#083A40] mt-2">${riskAnalysis.symptomCount} Reported</p>
              </div>
              <div class="p-3 rounded-lg bg-blue-100">
                <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                  <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-slate-200 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-slate-500 text-sm font-semibold">HbA1c Level</p>
                <p class="text-2xl font-bold text-[#083A40] mt-2">${formData.hba1c}%</p>
              </div>
              <div class="p-3 rounded-lg ${parseFloat(formData.hba1c) >= 6.5 ? 'bg-orange-100' : 'bg-slate-100'}">
                <svg class="w-6 h-6 ${parseFloat(formData.hba1c) >= 6.5 ? 'text-orange-600' : 'text-slate-600'}" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    const factorsList = document.getElementById('factors-list');
    if (factorsList) {
      let factorsHtml = '';

      factorsHtml += `
        <div class="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
          <div class="flex-shrink-0">
            <div class="flex items-center justify-center h-8 w-8 rounded-lg bg-[#0F6C74]">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5.5 13a3.5 3.5 0 01-.369-6.98 4 4 0 117.753-1.3A4.5 4.5 0 1113.5 13H11V9.413l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13H5.5z" />
              </svg>
            </div>
          </div>
          <div class="flex-1">
            <h3 class="font-semibold text-[#083A40] mb-1">Blood Glucose Levels</h3>
            <ul class="text-sm text-slate-600 space-y-1">
              <li>• Fasting: ${formData.fastingGlucose} mg/dL${parseFloat(formData.fastingGlucose) >= 126 ? ' (Elevated - threshold: >=126 mg/dL)' : ' (Normal range - threshold: >=126 mg/dL)'}</li>
              <li>• Random: ${formData.randomGlucose} mg/dL${parseFloat(formData.randomGlucose) >= 200 ? ' (Elevated - threshold: >=200 mg/dL)' : ' (Normal range - threshold: >=200 mg/dL)'}</li>
            </ul>
          </div>
        </div>
      `;

      factorsHtml += `
        <div class="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
          <div class="flex-shrink-0">
            <div class="flex items-center justify-center h-8 w-8 rounded-lg bg-[#0F6C74]">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
              </svg>
            </div>
          </div>
          <div class="flex-1">
            <h3 class="font-semibold text-[#083A40] mb-1">HbA1c Levels</h3>
            <p class="text-sm text-slate-600">Current: ${formData.hba1c}%${parseFloat(formData.hba1c) >= 6.5 ? ' (Higher levels - threshold: >=6.5%)' : ' (Within expected ranges - threshold: >=6.5%)'}</p>
          </div>
        </div>
      `;

      if (riskAnalysis.reportedSymptoms && riskAnalysis.reportedSymptoms.length > 0) {
        factorsHtml += `
          <div class="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center h-8 w-8 rounded-lg bg-[#0F6C74]">
                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-[#083A40] mb-1">Reported Symptoms</h3>
              <ul class="text-sm text-slate-600 space-y-1">
                ${riskAnalysis.reportedSymptoms.map((s) => `<li>• ${s}</li>`).join('')}
              </ul>
            </div>
          </div>
        `;
      }

      if (formData.ketonePresence === 'Present') {
        factorsHtml += `
          <div class="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center h-8 w-8 rounded-lg bg-orange-500">
                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18.868 3.644A9 9 0 115.656 18.854a9 9 0 0113.212-15.21zM9 5a4 4 0 100 8 4 4 0 000-8z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-[#083A40] mb-1">Ketone Presence</h3>
              <p class="text-sm text-slate-600">Ketones detected in analysis</p>
            </div>
          </div>
        `;
      }

      if (formData.cPeptideLevel) {
        const cPeptide = parseFloat(formData.cPeptideLevel);
        factorsHtml += `
          <div class="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center h-8 w-8 rounded-lg bg-[#3AB8C1]">
                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5 2a1 1 0 011-1h8a1 1 0 011 1v1h1a1 1 0 110 2v1h1a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v1a2 2 0 01-2 2h-1v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-1H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V6h1V2zm2 2v2h8V4H7z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-[#083A40] mb-1">C-Peptide Level</h3>
              <p class="text-sm text-slate-600">${formData.cPeptideLevel} ng/mL${cPeptide < 0.8 ? ' (Low - suggests reduced insulin production)' : ' (Normal range)'}</p>
            </div>
          </div>
        `;
      }

      if (formData.autoantibodyResult === 'Positive') {
        factorsHtml += `
          <div class="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <div class="flex-shrink-0">
              <div class="flex items-center justify-center h-8 w-8 rounded-lg bg-[#3AB8C1]">
                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-[#083A40] mb-1">Islet Autoantibody Test</h3>
              <p class="text-sm text-slate-600">Result: Positive</p>
            </div>
          </div>
        `;
      }

      factorsList.innerHTML = factorsHtml;
    }
  };

  const initPage = () => {
    enforceAuthEarly();
    guardProtected();
    renderNavbar();
    setupLoginForm();
    setupRegisterForm();
    setupDashboardForm();
    renderResultPage();
  };

  window.App = {
    initPage,
    isLoggedIn,
    login,
    logout,
    getUser,
  };
})();
