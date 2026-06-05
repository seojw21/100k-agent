// ==========================================================================
// NomadGuard AI - Core Logic, Risk Engine, and WTP Pricing Simulator
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // State Variables
    let currentStep = 1;
    let userTier = 'trial'; // trial, basic, premium
    let currentPriceGroup = localStorage.getItem('abGroup') || 'B'; // Default to B (Value focus)
    let surveyData = {};

    // Pricing structures for A/B tests
    const pricingGroups = {
        'A': { basic: 19, premium: 49, desc: 'Volume Focus (lowest entry barrier)' },
        'B': { basic: 29, premium: 79, desc: 'Value Focus (recommended scenario)' },
        'C': { basic: 39, premium: 129, desc: 'Premium Focus (high-value expert target)' }
    };

    // --- DOM Elements ---
    // Sections
    const surveySection = document.getElementById('survey-section');
    const riskReportSection = document.getElementById('risk-report-section');
    const paywallSection = document.getElementById('paywall-section');
    const dashboardSection = document.getElementById('dashboard-app-section');

    // Survey
    const surveyForm = document.getElementById('risk-survey-form');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnSubmit = document.getElementById('btn-submit');
    const optionCards = document.querySelectorAll('.option-card');
    const employmentHidden = document.getElementById('employment-type');

    // Risk Report displays
    const riskScoreCircle = document.getElementById('risk-score-circle');
    const riskScoreText = document.getElementById('risk-score-text');
    const riskTitleHeading = document.getElementById('risk-title-heading');
    const riskDescText = document.getElementById('risk-desc-text');
    const riskPenaltyVal = document.getElementById('risk-penalty-val');
    const riskDetailsContainer = document.getElementById('risk-details-container');
    const btnGoToPaywall = document.getElementById('btn-go-to-paywall');
    const btnBackToSurvey = document.getElementById('btn-back-to-survey');

    // Paywall
    const priceBasicDisplay = document.getElementById('price-basic-display');
    const pricePremiumDisplay = document.getElementById('price-premium-display');
    const btnBuyBasic = document.getElementById('btn-buy-basic');
    const btnBuyPremium = document.getElementById('btn-buy-premium');

    // Dashboard
    const currentTierBadge = document.getElementById('current-tier-badge');
    const dbMembershipTitle = document.getElementById('db-membership-title');
    const sidebarOverview = document.getElementById('db-nav-overview');
    const sidebarMonitoring = document.getElementById('db-nav-monitoring');
    const sidebarSimulator = document.getElementById('db-nav-simulator');
    const panelOverview = document.getElementById('panel-overview');
    const panelMonitoring = document.getElementById('panel-monitoring');
    const panelSimulator = document.getElementById('panel-simulator');
    const dbMetricDays = document.getElementById('db-metric-days');
    const dbCurrentCountryTxt = document.getElementById('db-current-country-txt');
    const dbVisaTypeTxt = document.getElementById('db-visa-type-txt');
    const simulatorLockedWrapper = document.getElementById('simulator-locked-wrapper');
    const simulatorActiveWrapper = document.getElementById('simulator-active-wrapper');
    const btnResetDemo = document.getElementById('btn-reset-demo');
    const btnUpgradeFromSim = document.getElementById('btn-upgrade-from-sim');

    // A/B Testing HUD Elements
    const abHud = document.getElementById('ab-hud');
    const btnHudMinimize = document.getElementById('btn-hud-minimize');
    const hudBody = document.getElementById('hud-body');
    const btnGroupA = document.getElementById('btn-group-a');
    const btnGroupB = document.getElementById('btn-group-b');
    const btnGroupC = document.getElementById('btn-group-c');
    const hudPriceBasic = document.getElementById('hud-price-basic');
    const hudPricePremium = document.getElementById('hud-price-premium');

    // Success Modal
    const purchaseSuccessModal = document.getElementById('purchase-success-modal');
    const modalSuccessTitle = document.getElementById('modal-success-title');
    const modalSuccessDesc = document.getElementById('modal-success-desc');
    const btnModalClose = document.getElementById('btn-modal-close');

    // --- Core Navigation logic for Survey ---
    function updateSurveyStep() {
        // Show/hide content panels
        document.querySelectorAll('.survey-step-content').forEach((panel, index) => {
            if (index === (currentStep - 1)) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });

        // Update step indicators
        document.querySelectorAll('.step-indicator').forEach((ind, index) => {
            const stepNum = index + 1;
            ind.className = 'step-indicator';
            if (stepNum === currentStep) {
                ind.classList.add('active');
            } else if (stepNum < currentStep) {
                ind.classList.add('completed');
                ind.innerHTML = '<i class="fa-solid fa-check"></i>';
            } else {
                ind.textContent = stepNum;
            }
        });

        // Toggle nav buttons
        btnPrev.disabled = (currentStep === 1);
        if (currentStep === 3) {
            btnNext.style.display = 'none';
            btnSubmit.style.display = 'inline-flex';
        } else {
            btnNext.style.display = 'inline-flex';
            btnSubmit.style.display = 'none';
        }
    }

    btnNext.addEventListener('click', () => {
        if (currentStep < 3) {
            currentStep++;
            updateSurveyStep();
        }
    });

    btnPrev.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            updateSurveyStep();
        }
    });

    // Custom option card handler (Step 2 cards)
    optionCards.forEach(card => {
        card.addEventListener('click', () => {
            optionCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            employmentHidden.value = card.getAttribute('data-value');
        });
    });

    // --- Risk Assessment Logic (Aha-Moment Generator) ---
    btnSubmit.addEventListener('click', () => {
        // Collect form data
        surveyData = {
            citizenship: document.getElementById('citizenship').value,
            targetCountry: document.getElementById('target-country').value,
            monthlyIncome: parseFloat(document.getElementById('monthly-income').value) || 0,
            employmentType: employmentHidden.value,
            stayDuration: document.getElementById('stay-duration').value,
            taxStatus: document.getElementById('tax-status').value
        };

        calculateRiskAndRender(surveyData);
    });

    function calculateRiskAndRender(data) {
        let riskScore = 30; // base score
        let penaltyAmount = 0;
        let warnings = [];

        const countryMap = {
            'ES': 'Spain',
            'TH': 'Thailand',
            'DE': 'Germany',
            'SE': 'Sweden'
        };
        const countryName = countryMap[data.targetCountry] || 'your host country';

        // 1. Stay Duration Risk
        if (data.stayDuration === 'over183') {
            riskScore += 35;
            penaltyAmount += Math.round(data.monthlyIncome * 12 * 0.25); // 25% of annual income penalty
            warnings.push({
                title: `${countryName}: Tax Residency Threshold Breach (183+ Days)`,
                desc: `Staying over 183 days in a calendar year typically triggers worldwide income tax obligations in ${countryName}. Failure to file can result in penalties of up to 150% of unpaid taxes plus double-taxation exposure.`
            });
        } else if (data.stayDuration === 'under183') {
            riskScore += 15;
            penaltyAmount += 850;
            warnings.push({
                title: `${countryName}: Temporary Residence & Income Attribution Risk`,
                desc: `If you hold a local rental agreement or receive regular domestic bank transfers, tax authorities may classify you as a de facto resident regardless of actual days spent — exposing you to local income tax.`
            });
        }

        // 2. Employment Type vs Visa
        if (data.employmentType === 'freelancer') {
            riskScore += 15;
            penaltyAmount += 1200;
            warnings.push({
                title: 'Unregistered Freelance Activity & Missing Tax License',
                desc: `Operating as a freelancer in ${countryName} without proper business registration or a freelancer tax ID constitutes unlicensed commercial activity, punishable by fines and potential visa revocation.`
            });
        } else {
            riskScore += 20;
            penaltyAmount += 3500;
            warnings.push({
                title: `${countryName}: Permanent Establishment (PE) Risk for Your Employer`,
                desc: `Working full-time as a remote employee while residing in ${countryName} could trigger a "Permanent Establishment" classification for your employer, exposing the company to significant corporate tax liabilities in this jurisdiction.`
            });
        }

        // 3. Tax Status
        if (data.taxStatus === 'home' || data.taxStatus === 'none') {
            riskScore += 15;
            warnings.push({
                title: 'Double Taxation & CRS Information Mismatch',
                desc: `Under the Common Reporting Standard (CRS) automatic exchange of financial information between your home country and ${countryName}, discrepancies in foreign account balances and transaction patterns may trigger a tax evasion investigation.`
            });
        }

        // Apply final caps
        riskScore = Math.min(riskScore, 98);
        penaltyAmount = Math.max(penaltyAmount, 450);

        // Render UI
        riskScoreText.textContent = `${riskScore}%`;
        riskPenaltyVal.textContent = `$${penaltyAmount.toLocaleString('en-US')}+`;

        // SVG circle stroke calculation
        // Circumference is 2 * PI * r = 2 * 3.14159 * 60 = 377
        const strokeDashoffset = 377 - (377 * riskScore) / 100;
        riskScoreCircle.style.strokeDashoffset = strokeDashoffset;

        // Custom Title
        if (riskScore >= 75) {
            riskTitleHeading.textContent = 'Critical Legal & Double-Taxation Red Flag';
            riskScoreCircle.style.stroke = 'var(--accent-danger)';
            riskScoreText.style.color = 'var(--accent-danger)';
        } else {
            riskTitleHeading.textContent = 'Compliance Gaps Requiring Attention';
            riskScoreCircle.style.stroke = 'var(--accent-gold)';
            riskScoreText.style.color = 'var(--accent-gold)';
        }

        // Warning Lists
        riskDetailsContainer.innerHTML = '';
        warnings.forEach(w => {
            const div = document.createElement('div');
            div.className = 'risk-detail-item warning';
            div.innerHTML = `
                <i class="fa-solid fa-circle-exclamation"></i>
                <div>
                    <div class="risk-detail-title">${w.title}</div>
                    <div class="risk-detail-desc">${w.desc}</div>
                </div>
            `;
            riskDetailsContainer.appendChild(div);
        });

        // Switch panel visibility
        surveySection.style.display = 'none';
        riskReportSection.style.display = 'block';
    }

    // --- Action Buttons ---
    btnGoToPaywall.addEventListener('click', () => {
        riskReportSection.style.display = 'none';
        paywallSection.style.display = 'block';
    });

    btnBackToSurvey.addEventListener('click', () => {
        paywallSection.style.display = 'none';
        riskReportSection.style.display = 'block';
    });

    // --- Pricing & A/B Testing Controller ---
    function updatePrices() {
        const prices = pricingGroups[currentPriceGroup];
        
        // Update paywall DOM elements
        priceBasicDisplay.innerHTML = `$${prices.basic}<span>/mo</span>`;
        pricePremiumDisplay.innerHTML = `$${prices.premium}<span>/mo</span>`;

        // Update HUD display
        hudPriceBasic.textContent = `$${prices.basic}`;
        hudPricePremium.textContent = `$${prices.premium}`;

        // Highlight active HUD button
        btnGroupA.classList.remove('active');
        btnGroupB.classList.remove('active');
        btnGroupC.classList.remove('active');
        if (currentPriceGroup === 'A') btnGroupA.classList.add('active');
        if (currentPriceGroup === 'B') btnGroupB.classList.add('active');
        if (currentPriceGroup === 'C') btnGroupC.classList.add('active');
    }

    // HUD handlers
    const abSelectorButtons = [btnGroupA, btnGroupB, btnGroupC];
    abSelectorButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const group = e.currentTarget.getAttribute('data-group');
            currentPriceGroup = group;
            localStorage.setItem('abGroup', group);
            updatePrices();
        });
    });

    // Animate minimize of HUD
    btnHudMinimize.addEventListener('click', () => {
        abHud.classList.toggle('minimized');
        if (abHud.classList.contains('minimized')) {
            btnHudMinimize.innerHTML = '<i class="fa-solid fa-flask"></i>';
            hudBody.style.display = 'none';
        } else {
            btnHudMinimize.innerHTML = '<i class="fa-solid fa-chevron-down"></i>';
            hudBody.style.display = 'flex';
        }
    });

    // --- Purchase checkout simulation ---
    btnBuyBasic.addEventListener('click', () => {
        showSuccessModal('basic');
    });

    btnBuyPremium.addEventListener('click', () => {
        showSuccessModal('premium');
    });

    function showSuccessModal(plan) {
        userTier = plan;
        modalSuccessTitle.textContent = plan === 'basic' ? 'Basic Membership Activated!' : 'Premium AI Membership Activated!';
        modalSuccessDesc.textContent = plan === 'basic'
            ? `Your real-time visa calendar and tax risk detection dashboard are now live. Billed at $${pricingGroups[currentPriceGroup].basic}/month.`
            : `Full AI predictive engine, 24/7 emergency legal hotline, and all premium features are now unlocked. Billed at $${pricingGroups[currentPriceGroup].premium}/month.`;

        purchaseSuccessModal.classList.add('active');
    }

    btnModalClose.addEventListener('click', () => {
        purchaseSuccessModal.classList.remove('active');
        paywallSection.style.display = 'none';
        activateDashboard();
    });

    // --- Dashboard Activator & Dynamic Configuration ---
    function activateDashboard() {
        dashboardSection.style.display = 'block';

        // Update header badges and displays
        currentTierBadge.className = `btn-tier-display ${userTier}`;
        currentTierBadge.querySelector('span').textContent = userTier.toUpperCase() + ' Plan Active';

        dbMembershipTitle.innerHTML = userTier === 'basic' 
            ? `<i class="fa-solid fa-shield-halved" style="color: var(--accent-indigo);"></i> Basic Member`
            : `<i class="fa-solid fa-crown" style="color: var(--accent-gold);"></i> Premium AI Member`;

        // Update Overview elements using survey values
        const countryMap = { 'ES': 'Spain', 'TH': 'Thailand', 'DE': 'Germany', 'SE': 'Sweden' };
        const visaMap = { 'freelancer': 'Freelancer License', 'employee': 'Remote Employee (unregistered)' };
        
        dbCurrentCountryTxt.textContent = countryMap[surveyData.targetCountry] || 'Host Country';
        dbVisaTypeTxt.textContent = visaMap[surveyData.employmentType] || 'Temporary Residence';

        // Set simulated countdown days based on survey stay duration
        if (surveyData.stayDuration === 'over183') {
            dbMetricDays.textContent = '19 days left';
            dbMetricDays.parentElement.parentElement.className = 'metric-card critical';
        } else if (surveyData.stayDuration === 'under183') {
            dbMetricDays.textContent = '84 days left';
            dbMetricDays.parentElement.parentElement.className = 'metric-card monitoring';
        } else {
            dbMetricDays.textContent = 'No concerns';
            dbMetricDays.parentElement.parentElement.className = 'metric-card safe';
        }

        // Apply visual lock check on simulator tab
        toggleSimulatorTierView();
        
        // Show Overview panel default
        showDashboardPanel('overview');
    }

    function toggleSimulatorTierView() {
        if (userTier === 'premium') {
            simulatorLockedWrapper.style.display = 'none';
            simulatorActiveWrapper.style.display = 'block';
        } else {
            simulatorLockedWrapper.style.display = 'flex';
            simulatorActiveWrapper.style.display = 'none';
        }
    }

    // Dashboard tab switching
    function showDashboardPanel(panelName) {
        document.querySelectorAll('.db-panel').forEach(panel => panel.classList.remove('active'));
        document.querySelectorAll('.sidebar-btn').forEach(btn => btn.classList.remove('active'));

        if (panelName === 'overview') {
            panelOverview.classList.add('active');
            sidebarOverview.classList.add('active');
        } else if (panelName === 'monitoring') {
            panelMonitoring.classList.add('active');
            sidebarMonitoring.classList.add('active');
        } else if (panelName === 'simulator') {
            panelSimulator.classList.add('active');
            sidebarSimulator.classList.add('active');
        }
    }

    sidebarOverview.addEventListener('click', () => showDashboardPanel('overview'));
    sidebarMonitoring.addEventListener('click', () => showDashboardPanel('monitoring'));
    sidebarSimulator.addEventListener('click', () => showDashboardPanel('simulator'));

    // Handle premium upgrades directly from simulator panel
    btnUpgradeFromSim.addEventListener('click', () => {
        dashboardSection.style.display = 'none';
        paywallSection.style.display = 'block';
    });

    // Reset Demo
    btnResetDemo.addEventListener('click', () => {
        userTier = 'trial';
        currentStep = 1;
        surveyForm.reset();
        
        // Show initial state
        dashboardSection.style.display = 'none';
        paywallSection.style.display = 'none';
        riskReportSection.style.display = 'none';
        surveySection.style.display = 'block';

        currentTierBadge.className = 'btn-tier-display trial';
        currentTierBadge.querySelector('span').textContent = 'Trial Mode';

        updateSurveyStep();
    });

    // --- Interactive Predictor (Premium Engine) ---
    const btnRunSim = document.getElementById('btn-run-sim');
    const simResultsBox = document.getElementById('sim-results-box');
    const simResultsText = document.getElementById('sim-results-text');

    btnRunSim.addEventListener('click', () => {
        const target = document.getElementById('sim-target-country').value;
        const income = parseFloat(document.getElementById('sim-monthly-income').value) || 0;
        const duration = document.getElementById('sim-stay-duration').value;

        let resHTML = '';

        if (target === 'SE') {
            resHTML += `
                <div style="border-left: 4px solid var(--accent-gold); padding-left: 0.75rem; margin-bottom: 0.5rem;">
                    <strong>Sweden (SveaTax Model) — Tax Crisis Detection:</strong><br>
                    <span style="font-size:0.9rem; color:var(--text-secondary);">
                        At an annualized income of kr ${(income * 12 * 10.5).toLocaleString('en-US')} SEK, staying over 183 days triggers integration with the <strong>SveaTax compliance model</strong>.<br>
                        You would be subject to self-employment contributions (Egenavgifter ~28.97%) and municipal income tax (Kommunalskatt ~32%). 
                        Without applying the Periodiseringsfond (30% deferral) and Schablonavdrag (25% deduction), your effective tax rate could spike to approximately 52.3%.
                    </span>
                </div>
            `;
        } else if (target === 'TH') {
            resHTML += `
                <div style="border-left: 4px solid var(--accent-success); padding-left: 0.75rem; margin-bottom: 0.5rem;">
                    <strong>Thailand — Digital Relocation Assessment:</strong><br>
                    <span style="font-size:0.9rem; color:var(--text-secondary);">
                        At $${income.toLocaleString()}/month, you qualify for Thailand's LTR (Long-Term Resident) visa under the remote worker category. 
                        A 90-day stay incurs $0 in visa penalties. However, continuing remote work beyond 183 days on a tourist visa could expose you to Thailand's revised 2024–2026 foreign-source income taxation rules, with local rates up to 35%.
                    </span>
                </div>
            `;
        } else if (target === 'ES') {
            resHTML += `
                <div style="border-left: 4px solid var(--accent-purple); padding-left: 0.75rem; margin-bottom: 0.5rem;">
                    <strong>Spain — Compliance Route Analysis:</strong><br>
                    <span style="font-size:0.9rem; color:var(--text-secondary);">
                        At $${income.toLocaleString()}/month, you comfortably exceed Spain's Digital Nomad Visa (DNV) minimum requirement of 200% of the SMI (approx. €2,680/month).<br>
                        Obtaining the DNV grants you access to the Beckham Law special tax regime — a flat 24% income tax rate for up to 5 years, instead of the standard progressive rate (up to 47%). This is the most recommended compliance route for your profile.
                    </span>
                </div>
            `;
        } else {
            resHTML += `
                <div style="border-left: 4px solid var(--accent-indigo); padding-left: 0.75rem; margin-bottom: 0.5rem;">
                    <strong>Germany — Freiberufler (Freelancer) Risk Assessment:</strong><br>
                    <span style="font-size:0.9rem; color:var(--text-secondary);">
                        Staying over 183 days in Germany subjects you to the full progressive income tax rate (Einkommensteuer, up to 42%). 
                        Additionally, if you receive USD income into a personal bank account without registering a tax ID (Steuernummer) with the local Finanzamt, you face penalties of up to $4,500 and potential permanent entry restrictions due to tax evasion charges.
                    </span>
                </div>
            `;
        }

        simResultsText.innerHTML = resHTML;
        simResultsBox.style.display = 'block';
    });

    // --- Initialize ---
    updateSurveyStep();
    updatePrices();
});
