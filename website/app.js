
const burger_style = document.querySelector(".burger-style");
const navbar_menu = document.querySelector(".navbar-menu"); 
burger_style.addEventListener("click", () => {
    burger_style.classList.toggle("active");
    navbar_menu.classList.toggle("active");
});
function find_trajectories() {
    let variable = document.getElementById('date_input').value;//variable is set in yyyy-mm-dd format even though the form is different on input
    if(variable){
        document.getElementById('date_alert').innerHTML = 'Tracing trajectories for: ' + variable;
        //need to call function here that will trace the trajectories?
        console.log(variable);
    } else { //should be impossible unless the user submits before entering a date
        document.getElementById('date_alert').innerHTML = 'Please enter a valid date';
        console.log("Invalid");
    }
}
