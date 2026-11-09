// Lightweight homepage enhancements.
document.documentElement.classList.add("js-ready");

// Keep the footer year current without requiring a third-party library.
const year = document.getElementById("current-year");
if (year) year.textContent = new Date().getFullYear();

// Set this to the deployed Django service URL when the backend is published.
const CONTACT_API_BASE_URL = "";

const contactForm = document.getElementById("contact-form");
if (contactForm) {
  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = document.getElementById("contact-status");
    const submitButton = contactForm.querySelector('button[type="submit"]');

    if (!CONTACT_API_BASE_URL) {
      status.textContent = "The message service is not connected yet. Please use the email link below for now.";
      status.className = "form-status is-error";
      return;
    }

    const formData = new FormData(contactForm);
    const payload = Object.fromEntries(formData.entries());
    status.textContent = "Sending your message…";
    status.className = "form-status";
    submitButton.disabled = true;

    try {
      const response = await fetch(`${CONTACT_API_BASE_URL.replace(/\/$/, "")}/api/contact/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Unable to send your message.");
      status.textContent = result.message || "Thanks. Your message has been received.";
      status.className = "form-status is-success";
      contactForm.reset();
    } catch (error) {
      status.textContent = error.message || "Something went wrong. Please email me directly.";
      status.className = "form-status is-error";
    } finally {
      submitButton.disabled = false;
    }
  });
}
