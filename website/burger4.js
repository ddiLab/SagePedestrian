const burger_style = document.querySelector(".burger-style4");
const navbar_menu = document.querySelector(".navbar-menu-mobile4");

burger_style.addEventListener("click", () => {
    burger_style.classList.toggle("active");
    navbar_menu.classList.toggle("active");
});