const burger_style = document.querySelector(".burger-style3");
const navbar_menu = document.querySelector(".navbar-menu-mobile3");

burger_style.addEventListener("click", () => {
    burger_style.classList.toggle("active");
    navbar_menu.classList.toggle("active");
});