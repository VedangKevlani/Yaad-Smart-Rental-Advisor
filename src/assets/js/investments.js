import { ref } from "vue";

export const loanResult = ref("");
export const investmentResult = ref("");
export const rentVsBuyResult = ref("");
export const rentalYieldResult = ref("");
export const cashFlowResult = ref("");

export function useFinancialTools({
  loanAmount,
  investmentAmount,
  monthlyRent,
  homePrice,
  annualRentalIncome,
  propertyCost,
  rentalIncome,
  monthlyExpenses,
}) {
  const interestRate = ref("");
  const loanTerm = ref("");

  const annualReturn = ref("");
  const years = ref("");

  const mortgageRate = ref("");
  const ownershipYears = ref("");

  const calculateLoan = () => {
    const principal = parseFloat(loanAmount.value);
    console.log(principal);
    const rate = parseFloat(interestRate.value) / 100 / 12;
    const payments = parseFloat(loanTerm.value) * 12;

    const x = Math.pow(1 + rate, payments);
    const monthly = (principal * x * rate) / (x - 1);

    loanResult.value =
      !isNaN(monthly) && isFinite(monthly) && monthly > 0
        ? `Your monthly payment will be: $${monthly.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "Please enter valid values";
  };

  const calculateInvestmentReturn = () => {
    const principal = parseFloat(investmentAmount.value);
    const rate = parseFloat(annualReturn.value) / 100;
    const time = parseFloat(years.value);

    const future = principal * Math.pow(1 + rate, time);

    investmentResult.value =
      !isNaN(future) && future > 0
        ? `Your investment will grow to: $${future.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "Please enter valid values";
  };

  const calculateRentVsBuy = () => {
    const rent = parseFloat(monthlyRent.value) * 12;
    const price = parseFloat(homePrice.value);
    const rate = parseFloat(mortgageRate.value) / 100;
    const ownYears = parseFloat(ownershipYears.value);

    const rentTotal = rent * ownYears;
    const downPayment = price * 0.2;
    const interestPaid = (price - downPayment) * rate * (ownYears / 2); // approx. half the interest over that time
    const propertyTaxes = price * 0.01 * ownYears;
    const maintenance = price * 0.01 * ownYears;
    const sellingCost = price * Math.pow(1 + 0.03, ownYears) * 0.06; // 3% annual appreciation, 6% agent fee
    const equity = (price - downPayment) * (ownYears / 30); // rough principal paid

    const buyCost =
      downPayment +
      interestPaid +
      propertyTaxes +
      maintenance +
      sellingCost -
      equity;

    rentVsBuyResult.value =
      !isNaN(rentTotal) && !isNaN(buyCost)
        ? `${
            buyCost < rentTotal
              ? "Buying is cheaper long-term."
              : "Renting is cheaper long-term."
          } Rent total: $${rentTotal.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })} vs Buy estimate: $${buyCost.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "Please enter valid values";
  };

  const calculateRentalYield = () => {
    const income = parseFloat(annualRentalIncome.value);
    const cost = parseFloat(propertyCost.value);

    rentalYieldResult.value =
      !isNaN(income) && !isNaN(cost) && cost !== 0
        ? `Rental Yield: ${((income / cost) * 100).toFixed(2)}%`
        : "Please enter valid values";
  };

  const calculateCashFlow = () => {
    const income = parseFloat(rentalIncome.value);
    const expenses = parseFloat(monthlyExpenses.value);

    if (!isNaN(income) && !isNaN(expenses)) {
      const flow = income - expenses;
      const status = flow >= 0 ? "Profit" : "Loss";
      cashFlowResult.value = `Monthly Cash Flow: $${flow.toLocaleString(
        undefined,
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }
      )} (${status})`;
    } else {
      cashFlowResult.value = "Please enter valid values";
    }
  };

  return {
    // Inputs
    loanAmount,
    interestRate,
    loanTerm,
    investmentAmount,
    annualReturn,
    years,
    monthlyRent,
    homePrice,
    mortgageRate,
    ownershipYears,
    annualRentalIncome,
    propertyCost,
    rentalIncome,
    monthlyExpenses,

    // Results
    loanResult,
    investmentResult,
    rentVsBuyResult,
    rentalYieldResult,
    cashFlowResult,

    // Calculators
    calculateLoan,
    calculateInvestmentReturn,
    calculateRentVsBuy,
    calculateRentalYield,
    calculateCashFlow,
  };
}
