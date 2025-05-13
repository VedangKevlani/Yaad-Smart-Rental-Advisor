<script setup>
import { useFinancialTools } from '@/assets/js/investments.js'

const {
  loanAmount,
  interestRate,
  loanTerm,
  loanResult,
  calculateLoan,

  investmentAmount,
  annualReturn,
  years,
  investmentResult,
  calculateInvestmentReturn,

  monthlyRent,
  homePrice,
  mortgageRate,
  ownershipYears,
  rentVsBuyResult,
  calculateRentVsBuy,

  annualRentalIncome,
  propertyCost,
  rentalYieldResult,
  calculateRentalYield,

  rentalIncome,
  monthlyExpenses,
  cashFlowResult,
  calculateCashFlow
} = useFinancialTools()
</script>


<template>
     <div class="container tool-box-container">
        <div class="tool-box">
            <h3>Loan Calculator</h3>
            <input type="number" class="tool-input" id="loanAmount" v-model="loanAmount" placeholder="Enter Loan Amount" />
            <input type="number" class="tool-input" id="interestRate" v-model="interestRate" placeholder="Enter Interest Rate (%)" />
            <input type="number" class="tool-input" id="loanTerm" v-model="loanTerm" placeholder="Enter Loan Term (Years)" />
            <button class="tool-button" @click="calculateLoan">Calculate Loan</button>
            <div class="result" id="loanResult" >{{ loanResult }}</div>
        </div>

        <div class="tool-box">
            <h3>Investment Return Calculator</h3>
            <input type="number" class="tool-input" id="investmentAmount" v-model="investmentAmount" placeholder="Enter Investment Amount" />
            <input type="number" class="tool-input" id="annualReturn" v-model="annualReturn" placeholder="Enter Annual Return (%)" />
            <input type="number" class="tool-input" id="years" v-model="years" placeholder="Enter Number of Years" />
            <button class="tool-button" @click="calculateInvestmentReturn">Calculate Return</button>
            <div class="result" id="investmentResult">{{ investmentResult }}</div>
        </div>

        <div class="tool-box">
            <h3>Rent vs Buy Calculator</h3>
            <input type="number" class="tool-input" id="monthlyRent"  v-model="monthlyRent" placeholder="Monthly Rent ($)">
            <input type="number" class="tool-input" id="homePrice"  v-model="homePrice" placeholder="Home Price ($)">
            <input type="number" class="tool-input" id="mortgageRate"  v-model="mortgageRate" placeholder="Mortgage Interest Rate (%)">
            <input type="number" class="tool-input" id="ownershipYears"  v-model="ownershipYears" placeholder="Years You Plan to Stay">
            <button class="tool-button" @click="calculateRentVsBuy">Compare</button>
            <div class="result" id="rentVsBuyResult">{{ rentVsBuyResult }}</div>
        </div>

        <div class="tool-box">
            <h3>Rental Yield Calculator</h3>
            <input type="number" class="tool-input" id="annualRentalIncome" v-model="annualRentalIncome" placeholder="Annual Rental Income ($)">
            <input type="number" class="tool-input" id="propertyCost" v-model="propertyCost" placeholder="Property Purchase Price ($)">
            <button class="tool-button" @click="calculateRentalYield">Calculate Yield</button>
            <div class="result" id="rentalYieldResult">{{ rentalYieldResult }}</div>
        </div>

        <div class="tool-box">
            <h3>Cash Flow Calculator</h3>
            <input type="number" class="tool-input" id="rentalIncome" v-model="rentalIncome" placeholder="Monthly Rental Income ($)">
            <input type="number" class="tool-input" id="monthlyExpenses" v-model="monthlyExpenses" placeholder="Total Monthly Expenses ($)">
            <button class="tool-button" @click="calculateCashFlow">Calculate Cash Flow</button>
            <div class="result" id="cashFlowResult">{{ cashFlowResult }}</div>
        </div>
    </div>
</template>
