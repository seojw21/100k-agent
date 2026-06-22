// ==========================================================================
// SveaTax - JavaScript Logic & Tax Calculator Engine
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const revenueInput = document.getElementById('revenue-input');
    const revenueSlider = document.getElementById('revenue-slider');
    const expensesInput = document.getElementById('expenses-input');
    const expensesSlider = document.getElementById('expenses-slider');
    const pFondSlider = document.getElementById('p-fond-slider');
    const pFondVal = document.getElementById('p-fond-val');
    const schablonCheckbox = document.getElementById('schablon-deduction');
    
    // Result displays
    const netProfitVal = document.getElementById('net-profit-val');
    const netMonthlyVal = document.getElementById('net-monthly-val');
    const taxRateVal = document.getElementById('tax-rate-val');
    const totalTaxVal = document.getElementById('total-tax-val');
    
    // Breakdown displays
    const breakdownRevenue = document.getElementById('breakdown-revenue');
    const breakdownExpenses = document.getElementById('breakdown-expenses');
    const breakdownResult = document.getElementById('breakdown-result');
    const breakdownPFond = document.getElementById('breakdown-pfond');
    const breakdownSchablon = document.getElementById('breakdown-schablon');
    const breakdownTaxable = document.getElementById('breakdown-taxable');
    const breakdownEgen = document.getElementById('breakdown-egen');
    const breakdownKommunal = document.getElementById('breakdown-kommunal');
    
    // Chart displays
    const taxPercentLabel = document.getElementById('tax-percent-label');
    const profitPercentLabel = document.getElementById('profit-percent-label');
    const chartTaxBar = document.getElementById('chart-tax-bar');
    const chartProfitBar = document.getElementById('chart-profit-bar');
    
    // SRU Preview & Download
    const sruPreviewText = document.getElementById('sru-preview-text');
    const downloadSruBtn = document.getElementById('download-sru-btn');
    
    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');

    // --- Format Helper ---
    function formatSEK(value) {
        return new Intl.NumberFormat('sv-SE', {
            style: 'currency',
            currency: 'SEK',
            maximumFractionDigits: 0
        }).format(value).replace('kr', 'kr');
    }

    // --- Core Tax Calculation Engine ---
    function calculateTaxes() {
        const revenue = parseFloat(revenueInput.value) || 0;
        const expenses = parseFloat(expensesInput.value) || 0;
        const pFondPercent = parseFloat(pFondSlider.value) || 0;
        const useSchablon = schablonCheckbox.checked;

        // Result before tax (R3)
        const resultBeforeTax = Math.max(0, revenue - expenses);

        // Periodiseringsfond allocation (R7)
        const pFondAllocation = resultBeforeTax > 0 ? Math.round(resultBeforeTax * (pFondPercent / 100)) : 0;
        const resultAfterPFond = Math.max(0, resultBeforeTax - pFondAllocation);

        // Schablonavdrag (25% deduction for Egenavgifter calculation)
        const schablonDeduction = useSchablon && resultAfterPFond > 0 ? Math.round(resultAfterPFond * 0.25) : 0;

        // Taxable income (Underlag för egenavgifter)
        const taxableIncome = Math.max(0, resultAfterPFond - schablonDeduction);

        // Taxes
        // Egenavgifter 2026: ~28.97%
        const egenavgifter = Math.round(taxableIncome * 0.2897);
        // Kommunalskatt: average ~32%
        const kommunalskatt = Math.round(taxableIncome * 0.32);

        const totalTax = egenavgifter + kommunalskatt;
        const netProfit = Math.max(0, resultBeforeTax - totalTax);
        const monthlyNet = Math.round(netProfit / 12);
        const effectiveTaxRate = resultBeforeTax > 0 ? ((totalTax / resultBeforeTax) * 100).toFixed(1) : '0.0';

        // --- Update UI Text Elements ---
        netProfitVal.textContent = formatSEK(netProfit);
        netMonthlyVal.textContent = formatSEK(monthlyNet);
        taxRateVal.textContent = `${effectiveTaxRate}%`;
        totalTaxVal.textContent = formatSEK(totalTax);

        breakdownRevenue.textContent = formatSEK(revenue);
        breakdownExpenses.textContent = `- ${formatSEK(expenses)}`;
        breakdownResult.textContent = formatSEK(resultBeforeTax);
        breakdownPFond.textContent = `- ${formatSEK(pFondAllocation)}`;
        breakdownSchablon.textContent = `- ${formatSEK(schablonDeduction)}`;
        breakdownTaxable.textContent = formatSEK(taxableIncome);
        breakdownEgen.textContent = formatSEK(egenavgifter);
        breakdownKommunal.textContent = formatSEK(kommunalskatt);

        // --- Update Progress Chart ---
        let taxPercent = 0;
        let profitPercent = 100;
        if (resultBeforeTax > 0) {
            taxPercent = Math.round((totalTax / resultBeforeTax) * 100);
            profitPercent = 100 - taxPercent;
        }

        taxPercentLabel.textContent = `${taxPercent}%`;
        profitPercentLabel.textContent = `${profitPercent}%`;
        chartTaxBar.style.width = `${taxPercent}%`;
        chartProfitBar.style.width = `${profitPercent}%`;

        // --- Update SRU File Content ---
        updateSRUPreview(revenue, expenses, resultBeforeTax, pFondAllocation, schablonDeduction, taxableIncome, egenavgifter, kommunalskatt);
    }

    // --- Generate SRU Format ---
    function updateSRUPreview(revenue, expenses, resultBeforeTax, pFond, schablon, taxable, egen, kommunal) {
        const currentDateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        const currentTimeStr = new Date().toTimeString().slice(0, 8).replace(/:/g, '');
        
        const sruContent = `#HEADER
#PROGRAM "SveaTax Sweden Tax Helper"
#GEN ${currentDateStr} ${currentTimeStr}
#ORGNR 800101-1234
#ENHET enskild_firma
#BLANKETT NE_2026
#IDENT 800101-1234
#UPPGIFT 3010 "${revenue}"     ; R1: Nettoomsättning (Net Revenue)
#UPPGIFT 3020 "${expenses}"    ; R2: Övriga externa kostnader (Expenses)
#UPPGIFT 3030 "${resultBeforeTax}" ; R3: Bokfört resultat före bokslutsdispositioner
#UPPGIFT 3070 "${pFond}"       ; R7: Avsättning till periodiseringsfond
#UPPGIFT 3100 "${schablon}"    ; R10: Schablonavdrag för egenavgifter
#UPPGIFT 3110 "${taxable}"     ; R11: Underlag för egenavgifter (Taxable base)
#UPPGIFT 3120 "${egen}"        ; R12: Beräknade egenavgifter (Self-employment tax)
#UPPGIFT 3130 "${kommunal}"     ; R13: Beräknad kommunal inkomstskatt (Municipal tax)
#UPPGIFT 3140 "${resultBeforeTax - pFond}" ; R14: Skattepliktigt överskott (Net taxable surplus)
#FOOTER`;

        sruPreviewText.textContent = sruContent;
    }

    // --- Sync Input Sliders & Inputs ---
    function syncInputs(input, slider, isCurrency = true) {
        slider.addEventListener('input', (e) => {
            input.value = e.target.value;
            calculateTaxes();
        });

        input.addEventListener('input', (e) => {
            let val = parseFloat(e.target.value) || 0;
            if (val < 0) val = 0;
            slider.value = val;
            calculateTaxes();
        });
    }

    syncInputs(revenueInput, revenueSlider);
    syncInputs(expensesInput, expensesSlider);

    pFondSlider.addEventListener('input', (e) => {
        pFondVal.textContent = `${e.target.value}%`;
        calculateTaxes();
    });

    schablonCheckbox.addEventListener('change', calculateTaxes);

    // --- Download SRU file ---
    downloadSruBtn.addEventListener('click', () => {
        const text = sruPreviewText.textContent;
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'blanketter.sru';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // --- Theme Toggle ---
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }

    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        const isLight = document.body.classList.contains('light-theme');
        
        if (isLight) {
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
        } else {
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
        }
    });

    // Initial tax calculation
    calculateTaxes();
});
