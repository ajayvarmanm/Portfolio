// Lightweight homepage enhancements.
document.documentElement.classList.add("js-ready");

// Keep the footer year current without requiring a third-party library.
const year = document.getElementById("current-year");
if (year) year.textContent = new Date().getFullYear();
