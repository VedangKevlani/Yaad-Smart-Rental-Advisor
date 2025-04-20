<template>
  <section class="landing-content fade-in">
    

    <div class="hero slide-up">

      <div class="flex items-center justify-center h-screen text-center">
        <div>
          <h1 class="title">Find Your Perfect Rental in Kingston</h1>

          <p class="subtitle">Smart. Fast. AI-Powered. Let Yaad analyze listings so you don’t have to.</p>
        </div>
      </div>

      <img src="@/assets/img/home.jpg" alt="Apartment Image" class="hero-image">
    </div>


    <div class="features" id="features">
      <div class="feature-box slide-up">
        <div class="feature-icon">🏙️</div>
        <h3>Enter Property Details</h3>
        <p>ill in the address and basic property information to get started.</p>
      </div>
      <div class="feature-box slide-up">
        <div class="feature-icon">📊</div>
        <h3>AI Analyzes the Data</h3>
        <p>Our algorithms evaluate the property against market data and investment metrics.</p>
      </div>
      <div class="feature-box slide-up">
        <div class="feature-icon">✅</div>
        <h3>You Get Smart Insights</h3>
        <p>Receive a detailed analysis of the property's investment potential.</p>
      </div>
    </div>

    <div class="cta-section slide-up" id="signup">
      <h2>Ready to Find Your Dream Rental?</h2>
      <p>Sign up and start analyzing listings with the power of AI.</p>
      <RouterLink to="/signup">
  <button class="cta-button">Create an Account</button>
</RouterLink>

    </div>
  </section>
</template>
