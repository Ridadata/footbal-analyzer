/**
 * scripts.js
 * Main JavaScript file for the Football Data Visualization project
 */

document.addEventListener("DOMContentLoaded", function () {
  // Common elements that might be present on multiple pages
  const loadingSpinner = document.getElementById("loading-spinner");
  const leagueSelect = document.getElementById("league-select");
  const manualRefreshBtn = document.getElementById("manual-refresh");

  // Initialize loading spinner if it exists
  if (loadingSpinner) {
    loadingSpinner.style.display = "none";
  }

  // Handle league selection for filtering
  if (leagueSelect) {
    // If this is the league search form on the home page
    const leagueSearchForm = document.getElementById("league-search-form");
    if (leagueSearchForm) {
      leagueSearchForm.addEventListener("submit", function(e) {
        e.preventDefault();
        const leagueId = leagueSelect.value;
        if (leagueId) {
          window.location.href = `/league/${leagueId}/live-matches`;
        } else {
          alert("Please select a league first.");
        }
      });
    }

    // If this is the league filter form on the live matches page
    const leagueFilterForm = document.getElementById("league-filter-form");
    if (leagueFilterForm) {
      leagueFilterForm.addEventListener("submit", function(e) {
        e.preventDefault();
        const leagueId = leagueSelect.value;
        if (leagueId) {
          window.location.href = `/league/${leagueId}/live-matches`;
        } else {
          window.location.href = '/live-matches';
        }
      });

      // Fetch leagues for the dropdown if we're on the live matches page
      fetchLeagues();
    }
  }

  // Handle manual refresh button
  if (manualRefreshBtn) {
    manualRefreshBtn.addEventListener("click", function() {
      location.reload();
    });
  }

  // Set up auto-refresh for live match pages
  const isLiveMatchPage = document.querySelector('.live-matches') ||
                          document.querySelector('.match-details');
  if (isLiveMatchPage) {
    // Auto-refresh every 60 seconds
    setInterval(function() {
      location.reload();
    }, 60000);
  }

  // Initialize tab functionality on match details page
  initTabs();

  // Initialize charts if we're on the match details page
  initCharts();

  /**
   * Fetches leagues from the API and populates the league select dropdown
   */
  async function fetchLeagues() {
    if (!leagueSelect) return;

    try {
      const response = await fetch('/api/leagues');
      if (!response.ok) {
        throw new Error('Failed to fetch leagues');
      }

      const data = await response.json();
      if (data && data.response) {
        // Clear existing options except the first one (All Leagues)
        while (leagueSelect.options.length > 1) {
          leagueSelect.remove(1);
        }

        // Add leagues to the dropdown
        data.response.forEach(item => {
          const league = item.league;
          const country = item.country;
          if (league && league.id) {
            const option = document.createElement('option');
            option.value = league.id;
            option.textContent = `${league.name} (${country.name})`;

            // Check if we need to pre-select this league
            const currentLeagueId = getCurrentLeagueId();
            if (currentLeagueId && league.id.toString() === currentLeagueId) {
              option.selected = true;
            }

            leagueSelect.appendChild(option);
          }
        });
      }
    } catch (error) {
      console.error('Error fetching leagues:', error);
    }
  }

  /**
   * Gets the current league ID from the URL if available
   */
  function getCurrentLeagueId() {
    const path = window.location.pathname;
    const match = path.match(/\/league\/(\d+)\/live-matches/);
    return match ? match[1] : null;
  }

  /**
   * Initializes tab functionality on the match details page
   */
  function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    if (!tabButtons.length) return;

    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
      button.addEventListener('click', () => {
        // Remove active class from all buttons and panes
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.remove('active'));

        // Add active class to clicked button and corresponding pane
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        const tabPane = document.getElementById(tabId);
        if (tabPane) {
          tabPane.classList.add('active');
        }
      });
    });
  }

  /**
   * Initializes charts on the match details page if Chart.js is available
   */
  function initCharts() {
    // Check if we're on the match details page and have Chart.js available
    if (!window.Chart || !document.querySelector('.match-details')) return;

    // The charts are initialized in the match_details.html template
    // using inline JavaScript with the data from the backend
  }

  /**
   * Utility to format a date string
   */
  function formatDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    return date.toLocaleString();
  }

  /**
   * Utility to create a loading indicator
   */
  function showLoading(element) {
    if (!element) return;

    element.innerHTML = `
      <div class="loading-indicator">
        <div class="spinner"></div>
        <p>Loading data...</p>
      </div>
    `;
  }

  /**
   * Utility to show an error message
   */
  function showError(element, message) {
    if (!element) return;

    element.innerHTML = `
      <div class="error-message">
        <p>${message || 'An error occurred. Please try again.'}</p>
      </div>
    `;
  }
});
