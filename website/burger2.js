const burger_style = document.querySelector(".burger-style2");
const navbar_menu = document.querySelector(".navbar-menu-mobile2");

burger_style.addEventListener("click", () => {
    burger_style.classList.toggle("active");
    navbar_menu.classList.toggle("active");
});