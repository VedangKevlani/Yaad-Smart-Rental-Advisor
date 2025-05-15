<script setup>
import { useFinancialTools } from '@/assets/js/investments.js'
import { ref, computed, watch } from 'vue'

const showLoan = ref(false);
const showInvestment = ref(false);
const showRentVsBuy = ref(false);
const showRentalYield = ref(false);
const showCashFlow = ref(false);

const loanAmountInput = ref('');
const investmentAmountInput = ref('');
const monthlyRentInput = ref('');
const homePriceInput = ref('');
const annualRentalIncomeInput = ref('');
const propertyCostInput = ref('');
const rentalIncomeInput = ref('');
const monthlyExpensesInput = ref('');

const loanAmount = ref('');
const investmentAmount = ref('');
const monthlyRent = ref('');
const homePrice = ref('');
const annualRentalIncome = ref('');
const propertyCost = ref('');
const rentalIncome = ref('');
const monthlyExpenses = ref('');



// Computed property to show formatted string with $ and commas
const formattedLoanAmount = computed(() => {
  const num = parseFloat(loanAmountInput.value.replace(/,/g, ''));
  if (isNaN(num)) return '';
  return `$${num.toLocaleString()}`;
})

const formattedInvestmentAmount = computed(() => {
  const num = parseFloat(investmentAmountInput.value.replace(/,/g, ''));
  if (isNaN(num)) return '';
  return `$${num.toLocaleString()}`;
})

const formattedMonthlyRent = computed(() => {
  const num = parseFloat(monthlyRentInput.value.replace(/,/g, ''));
  if (isNaN(num)) return '';
  return `$${num.toLocaleString()}`;
})

const formattedHomePrice = computed(() => {
  const num = parseFloat(homePriceInput.value.replace(/,/g, ''));
  if (isNaN(num)) return '';
  return `$${num.toLocaleString()}`;
})

const formattedAnnualRentalIncome = computed(() => {
  const num = parseFloat(annualRentalIncomeInput.value.replace(/,/g, ''))
  if (isNaN(num)) return ''
  return `$${num.toLocaleString()}`
})

const formattedPropertyCost = computed(() => {
  const num = parseFloat(propertyCostInput.value.replace(/,/g, ''))
  if (isNaN(num)) return ''
  return `$${num.toLocaleString()}`
})

const formattedRentalIncome = computed(() => {
  const num = parseFloat(rentalIncomeInput.value.replace(/,/g, ''))
  if (isNaN(num)) return ''
  return `$${num.toLocaleString()}`
})

const formattedMonthlyExpenses = computed(() => {
  const num = parseFloat(monthlyExpensesInput.value.replace(/,/g, ''))
  if (isNaN(num)) return ''
  return `$${num.toLocaleString()}`
})



// Method to update loanAmount while stripping out symbols and formatting
const updateLoanAmount = (val) => {
  loanAmountInput.value = val.replace(/[^\d.]/g, '');
  loanAmount.value = loanAmountInput.value;
}

const updateInvestmentAmount = (val) => {
  investmentAmountInput.value = val.replace(/[^\d.]/g, '');
  investmentAmount.value = investmentAmountInput.value;
}

const updateMonthlyRent = (val) => {
  monthlyRentInput.value = val.replace(/[^\d.]/g, '');
  monthlyRent.value = monthlyRentInput.value;
}

const updateHomePrice = (val) => {
  homePriceInput.value = val.replace(/[^\d.]/g, '');
  homePrice.value = homePriceInput.value;
}

const updateAnnualRentalIncome = (val) => {
  annualRentalIncomeInput.value = val.replace(/[^\d.]/g, '')
  annualRentalIncome.value = annualRentalIncomeInput.value;
}

const updatePropertyCost = (val) => {
  propertyCostInput.value = val.replace(/[^\d.]/g, '')
  propertyCost.value = propertyCostInput.value;
}

const updateRentalIncome = (val) => {
  rentalIncomeInput.value = val.replace(/[^\d.]/g, '')
  rentalIncome.value = rentalIncomeInput.value;
}

const updateMonthlyExpenses = (val) => {
  monthlyExpensesInput.value = val.replace(/[^\d.]/g, '')
  monthlyExpenses.value = monthlyExpensesInput.value;
}

const {
  interestRate, loanTerm, loanResult, calculateLoan,

  annualReturn, years, investmentResult, calculateInvestmentReturn,

  mortgageRate, ownershipYears, rentVsBuyResult, calculateRentVsBuy,

  rentalYieldResult, calculateRentalYield,

  cashFlowResult, calculateCashFlow
} = useFinancialTools({ loanAmount, investmentAmount, monthlyRent, homePrice, annualRentalIncome, propertyCost, rentalIncome, monthlyExpenses })

watch(showLoan, (newVal) => {
  if (newVal) {
    loanAmountInput.value = '';
    interestRate.value = '';
    loanTerm.value = '';
    loanResult.value = '';
  }
});

watch(showInvestment, (newVal) => {
  if (newVal) {
    investmentAmountInput.value = '';
    annualReturn.value = '';
    years.value = '';
    investmentResult.value = '';
  }
});

watch(showRentVsBuy, (newVal) => {
  if (newVal) {
    monthlyRentInput.value = '';
    homePriceInput.value = '';
    mortgageRate.value = '';
    ownershipYears.value = '';
    rentVsBuyResult.value = '';
  }
});

watch(showRentalYield, (newVal) => {
  if (newVal) {
    annualRentalIncomeInput.value = '';
    propertyCostInput.value = '';
    rentalYieldResult.value = '';
  }
});

watch(showCashFlow, (newVal) => {
  if (newVal) {
    rentalIncomeInput.value = '';
    monthlyExpensesInput.value = '';
    cashFlowResult.value = '';
  }
});


</script>



<template>
  <div class="investment-tools-root">
    <div class="header">
      <div class="start">
        <svg width="64" height="64" viewBox="0 0 60 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="8" y="24" width="48" height="32" stroke="#40a7c3" stroke-width="2" />
          <path d="M16 40L24 32L32 40L40 32L48 40" stroke="#40a7c3" stroke-width="2" stroke-linejoin="round" />
          <path d="M32 24V16" stroke="#40a7c3" stroke-width="2" stroke-linecap="round" />
          <circle cx="32" cy="12" r="4" stroke="#40a7c3" stroke-width="2" />
        </svg>

        <h1 class="intro">Welcome to the Investment Tools Section!! </h1>
      </div>

      <h5>This section provides a number of calculators, each with specific functionality as it relates to rental
        property. Here is a breakdown of what each calculator does: </h5>
      <div class="container mt-4">
 <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
  <div class="col">
    <div class="card h-100 shadow-sm">
      <div class="card-body">
        <p class="card-text">
          The loan calculator computes the monthly mortgage payment based on the loan amount, interest rate, and
          loan term, helping property buyers estimate their monthly financial commitment.
        </p>
      </div>
    </div>
  </div>
  <div class="col">
    <div class="card h-100 shadow-sm">
      <div class="card-body">
        <p class="card-text">
          The investment return calculator estimates the future value of an investment based on compound interest,
          helping property investors understand how their invested capital may grow over time.
        </p>
      </div>
    </div>
  </div>
  <div class="col">
    <div class="card h-100 shadow-sm">
      <div class="card-body">
        <p class="card-text">
          The rent vs buy calculator helps potential homebuyers compare the long-term financial costs of renting
          versus buying a property over a specified ownership period.
        </p>
      </div>
    </div>
  </div>

  <!-- Row 2 with one placeholder in column 2 -->
  <div class="col">
    <div class="card h-100 shadow-sm">
      <div class="card-body">
        <p class="card-text">
          The rental yield calculator computes the rental yield, a key metric that shows the return on investment
          from rental income relative to the property's cost.
        </p>
      </div>
    </div>
  </div>

  <!-- Placeholder to push next card to column 3 -->
  <div class="col d-none d-lg-block">
    <div class="card h-100 border-0 bg-transparent"></div>
  </div>

  <div class="col">
    <div class="card h-100 shadow-sm">
      <div class="card-body">
        <p class="card-text">
          The cash flow calculator helps property owners determine their monthly cash flow by comparing rental
          income against monthly expenses.
        </p>
      </div>
    </div>
  </div>
</div>



</div>

    </div>

    <div class="container tool-box-container">
      <div class="button-group">
        <button class="btn submit-button" @click="showLoan = !showLoan">Calculate Loan</button>
        <button class="btn submit-button" @click="showInvestment = !showInvestment">Calculate Investment
          Return</button>
        <button class="btn submit-button" @click="showRentVsBuy = !showRentVsBuy">Compare Rent vs Buy</button>
        <button class="btn submit-button" @click="showRentalYield = !showRentalYield">Calculate Rental
          Yield</button>
        <button class="btn submit-button" @click="showCashFlow = !showCashFlow">Calculate Cash Flow</button>
      </div>

      <div class="tool-container">
        <!-- Loan Calculator -->
        <div class="tool-box" v-show="showLoan">
          <h3>Loan Calculator</h3>

          <div class="tool-row">
            <label class="tool-label">Loan Amount</label>
            <input type="text" class="tool-input" :value="formattedLoanAmount"
              @input="updateLoanAmount($event.target.value)" placeholder="Enter Loan Amount ($)" />
          </div>

          <div class="tool-row">
            <label class="tool-label">Interest Rate</label>
            <input type="number" class="tool-input" v-model="interestRate" placeholder="Enter Interest Rate (%)" />
          </div>

          <div class="tool-row">
            <label class="tool-label">Loan Term (Years)</label>
            <input type="number" class="tool-input" v-model="loanTerm" placeholder="Enter Loan Term (Years)" />
          </div>

          <button class="tool-button" @click="calculateLoan">Calculate Loan</button>
          <div class="result">{{ loanResult }}</div>
        </div>

        <!-- Investment Return Calculator -->
        <div class="tool-box" v-show="showInvestment">
          <h3>Investment Return Calculator</h3>

          <div class="tool-row">
            <label class="tool-label">Investment Amount</label>
            <input type="text" class="tool-input" :value="formattedInvestmentAmount"
              @input="updateInvestmentAmount($event.target.value)" placeholder="Enter Investment Amount($)" />
          </div>

          <div class="tool-row">
            <label class="tool-label">Annual Return</label>
            <input type="number" class="tool-input" v-model="annualReturn" placeholder="Enter Annual Return (%)" />
          </div>

          <div class="tool-row">
            <label class="tool-label">Number of Years</label>
            <input type="number" class="tool-input" v-model="years" placeholder="Enter Number of Years" />
          </div>


          <button class="tool-button" @click="calculateInvestmentReturn">Calculate Return</button>
          <div class="result">{{ investmentResult }}</div>
        </div>

        <!-- Rent vs Buy Calculator -->
        <div class="tool-box" v-show="showRentVsBuy">
          <h3>Rent vs Buy Calculator</h3>

          <div class="tool-row">
            <label class="tool-label">Monthly Rent</label>
            <input type="text" class="tool-input" :value="formattedMonthlyRent"
              @input="updateMonthlyRent($event.target.value)" placeholder="Monthly Rent ($)" />
          </div>

          <div class="tool-row">
            <label class="tool-label">Home Price</label>
            <input type="text" class="tool-input" :value="formattedHomePrice"
              @input="updateHomePrice($event.target.value)" placeholder="Home Price ($)" />
          </div>

          <div class="tool-row">
            <label class="tool-label">Interest Rate</label>
            <input type="number" class="tool-input" v-model="mortgageRate" placeholder="Mortgage Interest Rate (%)">
          </div>

          <div class="tool-row">
            <label class="tool-label">Years of Residency</label>
            <input type="number" class="tool-input" v-model="ownershipYears" placeholder="Years of Residency">
          </div>

          <button class="tool-button" @click="calculateRentVsBuy">Compare</button>
          <div class="result">{{ rentVsBuyResult }}</div>
        </div>

        <!-- Rental Yield Calculator -->
        <div class="tool-box" v-show="showRentalYield">
          <h3>Rental Yield Calculator</h3>

          <div class="tool-row">
            <label class="tool-label">Annual Rental Income</label>
            <input type="text" class="tool-input" :value="formattedAnnualRentalIncome"
              @input="updateAnnualRentalIncome($event.target.value)" placeholder="Annual Rental Income ($)" />
          </div>

          <div class="tool-row">
            <label class="tool-label">Property Cost</label>
            <input type="text" class="tool-input" :value="formattedPropertyCost"
              @input="updatePropertyCost($event.target.value)" placeholder="Property Cost ($)" />
          </div>


          <button class="tool-button" @click="calculateRentalYield">Calculate Yield</button>
          <div class="result">{{ rentalYieldResult }}</div>
        </div>

        <!-- Cash Flow Calculator -->
        <div class="tool-box" v-show="showCashFlow">
          <h3>Cash Flow Calculator</h3>

          <div class="tool-row">
            <label class="tool-label">Total Monthly Rental Income</label>
            <input type="text" class="tool-input" :value="formattedRentalIncome"
              @input="updateRentalIncome($event.target.value)" placeholder="Total Monthly Rental Income ($)" />
          </div>

          <div class="tool-row">
            <label class="tool-label">Total Montly Expenses</label>
            <input type="text" class="tool-input" :value="formattedMonthlyExpenses"
              @input="updateMonthlyExpenses($event.target.value)" placeholder="Total Monthly Expenses ($)" />
          </div>


          <button class="tool-button" @click="calculateCashFlow">Calculate Cash Flow</button>
          <div class="result">{{ cashFlowResult }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.button-group {
  align-self: flex-start;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-left: 20px;
  margin-right: 0;
}

.tool-container {
  margin: 0 10px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  gap: 30px;
  max-width: 100%;
}

.header {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1400px;
  margin: 80px auto;
  text-align: left;
  gap: 10px;
}

.intro {
  font-weight: 700;
  color: #40a7c3;
}

svg.tool-icon {
  color: #40a7c3;
}

h2 {
  font-weight: 300px;
  margin-bottom: 30px;
}

.start {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.tool-row {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
  width: 100%;
}

.tool-label {
  display: block;
  align-self: flex-start;
  margin-bottom: 4px;
  font-weight: 500;
  color: white;
}

.card {
  background-color: var(--primary);
  border: none;
  border-radius: 20px;
}

.dark-mode .card {
  background-color: var(--primary-dark);
}


.card-text {
  color: white;
  font-weight: 500;
}
</style>