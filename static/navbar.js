const hamburger = document.querySelector(".hamburger");
const dropdown = document.querySelector(".dropdown");

hamburger.addEventListener("click", () => {
  dropdown.classList.toggle("active");
});