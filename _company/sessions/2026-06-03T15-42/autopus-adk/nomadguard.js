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
        'A': { basic: 19, premium: 49, desc: 'Volume Focus (최저 장벽 진입 유도)' },
        'B': { basic: 29, premium: 79, desc: 'Value Focus (추천 요금제 시나리오)' },
        'C': { basic: 39, premium: 129, desc: 'Premium Focus (고단가/전문가 타겟)' }
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
            'ES': '스페인',
            'TH': '태국',
            'DE': '독일',
            'SE': '스웨덴'
        };
        const countryName = countryMap[data.targetCountry] || '거주국';

        // 1. Stay Duration Risk
        if (data.stayDuration === 'over183') {
            riskScore += 35;
            penaltyAmount += Math.round(data.monthlyIncome * 12 * 0.25); // 25% of annual income penalty
            warnings.push({
                title: `${countryName} 세무거주자 확정 리스크 (183일 초과)`,
                desc: `연간 183일 이상 체류 시 전 세계 소득에 대한 납세 의무가 현지에 발생합니다. 미신고 시 최대 150%의 가산세 및 이중과세가 부과될 수 있습니다.`
            });
        } else if (data.stayDuration === 'under183') {
            riskScore += 15;
            penaltyAmount += 850;
            warnings.push({
                title: `${countryName} 임시 거주 및 소득 귀속 위험`,
                desc: `90일 이상 임차 계약 또는 정기 현지 송금 흔적이 발견되는 경우, 체류 일수와 관계없이 세법상 거주자로 판정될 소지가 생깁니다.`
            });
        }

        // 2. Employment Type vs Visa
        if (data.employmentType === 'freelancer') {
            riskScore += 15;
            penaltyAmount += 1200;
            warnings.push({
                title: '비법인 임시 상거래 및 세무 라이선스 누락',
                desc: `${countryName} 내에서 적법한 1인 기업 등록 또는 프리랜서 세금 등록증 없이 원격 소득을 수령할 경우 무등록 무허가 영업 행위로 처벌받을 수 있습니다.`
            });
        } else {
            riskScore += 20;
            penaltyAmount += 3500;
            warnings.push({
                title: `${countryName} 내 고정사업장(PE) 간주 및 기업 벌금`,
                desc: `해외 고용주의 풀타임 직원으로서 현지 거주하면서 상시 근무할 경우, 본사가 해당 국가에 세무상 '고정사업장(Permanent Establishment)'을 둔 것으로 오인받아 본사에 막대한 법인세 패널티가 부과될 수 있습니다.`
            });
        }

        // 3. Tax Status
        if (data.taxStatus === 'home' || data.taxStatus === 'none') {
            riskScore += 15;
            warnings.push({
                title: '이중 납세 또는 국가 간 정보 공유망(CRS) 불일치',
                desc: `대한민국과 ${countryName} 간의 금융정보자동교환협정(CRS)에 의해 국외 계좌 잔액 및 지출 정보가 불일치 시 탈세 조사 대상이 될 수 있습니다.`
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
            riskTitleHeading.textContent = '치명적 법률 및 이중과세 적신호';
            riskScoreCircle.style.stroke = 'var(--accent-danger)';
            riskScoreText.style.color = 'var(--accent-danger)';
        } else {
            riskTitleHeading.textContent = '주의가 요구되는 컴플라이언스 공백';
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
        priceBasicDisplay.innerHTML = `$${prices.basic}<span>/월</span>`;
        pricePremiumDisplay.innerHTML = `$${prices.premium}<span>/월</span>`;

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
            const group = e.target.getAttribute('data-value') || e.target.id.split('-').pop().toUpperCase();
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
        modalSuccessTitle.textContent = plan === 'basic' ? 'Basic 멤버십 활성화 성공!' : 'Premium AI 멤버십 활성화 성공!';
        modalSuccessDesc.textContent = plan === 'basic'
            ? `실시간 비자 캘린더 및 세무 위기 감지 대시보드가 정상 개방되었습니다. 월 구독 가격 $${pricingGroups[currentPriceGroup].basic}으로 시작됩니다.`
            : `AI 예측 시나리오 엔진과 24시간 비상 법률 라인 등 프리미엄 혜택 전체가 활성화되었습니다. 월 구독 가격 $${pricingGroups[currentPriceGroup].premium}으로 시작됩니다.`;

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
        currentTierBadge.querySelector('span').textContent = userTier.toUpperCase() + ' 플랜 이용 중';

        dbMembershipTitle.innerHTML = userTier === 'basic' 
            ? `<i class="fa-solid fa-shield-halved" style="color: var(--accent-indigo);"></i> Basic Member`
            : `<i class="fa-solid fa-crown" style="color: var(--accent-gold);"></i> Premium AI Member`;

        // Update Overview elements using survey values
        const countryMap = { 'ES': '스페인', 'TH': '태국', 'DE': '독일', 'SE': '스웨덴' };
        const visaMap = { 'freelancer': '프리랜서 라이선스', 'employee': '해외근무 비법인 직원' };
        
        dbCurrentCountryTxt.textContent = countryMap[surveyData.targetCountry] || '체류국';
        dbVisaTypeTxt.textContent = visaMap[surveyData.employmentType] || '일반 임시 거주';

        // Set simulated countdown days based on survey stay duration
        if (surveyData.stayDuration === 'over183') {
            dbMetricDays.textContent = '19 일 남음';
            dbMetricDays.parentElement.parentElement.className = 'metric-card critical';
        } else if (surveyData.stayDuration === 'under183') {
            dbMetricDays.textContent = '84 일 남음';
            dbMetricDays.parentElement.parentElement.className = 'metric-card monitoring';
        } else {
            dbMetricDays.textContent = '전혀 문제없음';
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
        currentTierBadge.querySelector('span').textContent = 'Trial 상태';

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
                    <strong>스웨덴(SveaTax 규정) 모의 세무 위기 감지:</strong><br>
                    <span style="font-size:0.9rem; color:var(--text-secondary);">
                        연간 수입 환산 kr ${(income * 12 * 10.5).toLocaleString('sv-SE')} SEK 기준으로, 183일 초과 체류 시 <strong>SveaTax 세무 모델</strong>과 연합됩니다.<br>
                        자기고용세(Egenavgifter ~28.97%) 및 지방세(Kommunalskatt ~32%) 의무 부과 대상으로 판정됩니다. 
                        과세이월(Periodiseringsfond 30%) 제도 및 Schablonavdrag 25% 공제 설정을 통하지 않을 경우 실효세율은 약 52.3%로 폭등할 리스크가 있습니다.
                    </span>
                </div>
            `;
        } else if (target === 'TH') {
            resHTML += `
                <div style="border-left: 4px solid var(--accent-success); padding-left: 0.75rem; margin-bottom: 0.5rem;">
                    <strong>태국 디지털 이주 검토:</strong><br>
                    <span style="font-size:0.9rem; color:var(--text-secondary);">
                        월 소득 $${income.toLocaleString()} 기준으로 태국 LTR(Long-Term Resident) 비자 원격 근로자 부류 발급이 권장됩니다. 
                        90일 체류 시 비자 패널티는 $0이나, 무비자 관광 입국 후 원격근무를 183일 이상 지속할 경우 국외원천소득 유입에 대한 국내세법 개정안(2024~2026 개정)에 따라 현지 세율 최고 35%로 소득 추적을 받을 위험이 있습니다.
                    </span>
                </div>
            `;
        } else if (target === 'ES') {
            resHTML += `
                <div style="border-left: 4px solid var(--accent-purple); padding-left: 0.75rem; margin-bottom: 0.5rem;">
                    <strong>스페인 이주 컴플라이언스 진단:</strong><br>
                    <span style="font-size:0.9rem; color:var(--text-secondary);">
                        월 소득 $${income.toLocaleString()} 수준에서 스페인 디지털 노마드 비자(DNV)를 신청할 경우, 최저 요건인 스페인 최저임금(SMI)의 200%인 월 €2,680 조건을 넉넉히 충족합니다.<br>
                        이 비자를 발급받으면 특별세율(Beckham Law 변형) 혜택을 취득하여 최대 5년간 일반 47% 소득세 대신 24%의 단일 단일세율을 안전하게 영위할 수 있어 가장 추천하는 컴플라이언스 루트입니다.
                    </span>
                </div>
            `;
        } else {
            resHTML += `
                <div style="border-left: 4px solid var(--accent-indigo); padding-left: 0.75rem; margin-bottom: 0.5rem;">
                    <strong>독일 프리랜서(Freiberufler) 위기 진단:</strong><br>
                    <span style="font-size:0.9rem; color:var(--text-secondary);">
                        독일 체류 시 183일 기준 충족 시 소득세(Einkommensteuer) 누진세율(최고 42%)이 그대로 적용됩니다. 
                        또한 연방 세무소(Finanzamt)에 사업 등록 번호(Steuernummer)를 발급받지 않고 한국 개인 통장으로 달러 소득을 인출할 경우 벌금 최고 $4,500 및 탈세 혐의로 영구 입국 제한 조치될 수 있으므로 조기 비자 갱신이 필요합니다.
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
