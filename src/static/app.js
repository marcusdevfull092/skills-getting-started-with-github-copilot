document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const modal = document.getElementById("confirmation-modal");
  const modalDetails = document.getElementById("modal-details");
  const closeModalBtn = document.getElementById("close-modal");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear activity dropdown options (keep only the default one)
      while (activitySelect.options.length > 1) {
        activitySelect.remove(1);
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Get current date and time
        const now = new Date();
        const dateTime = now.toLocaleString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit"
        });
        
        // Show confirmation modal
        modalDetails.innerHTML = `
          <p><strong>Email:</strong> ${email}</p>
          <p><strong>Activity:</strong> ${activity}</p>
          <p><strong>Date & Time:</strong> ${dateTime}</p>
        `;
        modal.classList.remove("hidden");
        
        // Update activities immediately after successful signup
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Close modal event
  closeModalBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  // Close modal when clicking outside the modal content
  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.classList.add("hidden");
    }
  });

  // Handle Sign Up for All Activities button
  const signupAllBtn = document.getElementById("signup-all-btn");
  signupAllBtn.addEventListener("click", async () => {
    const email = document.getElementById("email").value;

    if (!email) {
      messageDiv.textContent = "Please enter an email address";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      return;
    }

    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      const results = [];
      let successCount = 0;

      // Sign up for all activities
      for (const activityName of Object.keys(activities)) {
        try {
          const signupResponse = await fetch(
            `/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`,
            { method: "POST" }
          );

          const signupResult = await signupResponse.json();

          if (signupResponse.ok) {
            results.push(`✓ ${activityName}`);
            successCount++;
          } else {
            results.push(`✗ ${activityName}: ${signupResult.detail}`);
          }
        } catch (error) {
          results.push(`✗ ${activityName}: Error occurred`);
        }
      }

      // Get current date and time
      const now = new Date();
      const dateTime = now.toLocaleString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });

      // Show modal with results
      let detailsHTML = `
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Date & Time:</strong> ${dateTime}</p>
        <p><strong>Results:</strong></p>
      `;

      results.forEach((result) => {
        detailsHTML += `<p>${result}</p>`;
      });

      detailsHTML += `<p><strong>Total: ${successCount}/${Object.keys(activities).length} activities</strong></p>`;

      modalDetails.innerHTML = detailsHTML;
      modal.classList.remove("hidden");

      // Update activities immediately
      fetchActivities();

      // Show success or partial success message
      if (successCount > 0) {
        messageDiv.textContent = `Successfully signed up for ${successCount} activity/activities!`;
        messageDiv.className = "success";
      } else {
        messageDiv.textContent = "Could not sign up for any activities";
        messageDiv.className = "error";
      }
      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up for all activities. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
