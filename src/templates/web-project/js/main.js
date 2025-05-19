// Main JavaScript file for test web project
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM fully loaded and parsed');
  
  // Get DOM elements
  const ctaButton = document.getElementById('cta-btn');
  const navLinks = document.querySelectorAll('.menu a');
  
  // Event listener for CTA button
  ctaButton.addEventListener('click', function() {
    alert('Thank you for your interest! This is a test project for Anthropic verification.');
  });
  
  // Smooth scroll for navigation links
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      const targetSection = document.querySelector(targetId);
      
      if (targetSection) {
        window.scrollTo({
          top: targetSection.offsetTop - 80,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Example of a utility function
  function debounce(func, delay) {
    let timer;
    return function(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => {
        func.apply(this, args);
      }, delay);
    };
  }
  
  // Example of using the utility function
  const handleScroll = debounce(() => {
    const scrollPosition = window.scrollY;
    
    // Add a class to the navigation when scrolled
    const nav = document.querySelector('nav');
    if (scrollPosition > 100) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }, 100);
  
  // Add scroll event listener
  window.addEventListener('scroll', handleScroll);
  
  // Feature detection example
  class FeatureDetection {
    constructor() {
      this.supports = {};
    }
    
    init() {
      this.supports.flexbox = this.testFlexbox();
      this.supports.grid = this.testGrid();
      console.log('Feature detection:', this.supports);
    }
    
    testFlexbox() {
      return 'flexBasis' in document.documentElement.style;
    }
    
    testGrid() {
      return 'grid' in document.documentElement.style;
    }
  }
  
  // Initialize feature detection
  const features = new FeatureDetection();
  features.init();
});
