/**
 * Sets up the carousel on the debug page
 * to easily slide through images.
 */

window.onload = function () {
    var carousel = new Slider({
        images: '.carousel img',
        btnPrev: '.carousel .buttons .prev',
        btnNext: '.carousel .buttons .next',
        rate: 1500
    });

    //adds event listener to wait for keyboard inputs
    document.addEventListener("keydown", function(event) {
        if(event.key !== undefined) {
            //move with arrow keys
            if(event.code === "ArrowLeft") document.getElementById('previous').onclick();
            else if(event.code === "ArrowRight") document.getElementById('next').onclick();
        }
    });
};

function Slider(obj) {
    var show = 'showplease';
    this.images = document.querySelectorAll(obj.images);
    this.auto = obj.auto;
    this.btnPrev = obj.btnPrev;
    this.btnNext = obj.btnNext;
    this.rate = obj.rate;

    var i = 0;
    var slider = this;

    this.prev = function () {   //move to previous image
        slider.images[i].classList.remove(show);
        i = Math.max(0, Math.min(slider.images.length-1, --i)); //clamp to avoid confusion
        slider.images[i].classList.add(show);
    }

    this.next = function () {   //moves to the next image
        slider.images[i].classList.remove(show);
        i = Math.max(0, Math.min(slider.images.length-1, ++i)); //clamp to avoid confusion
        slider.images[i].classList.add(show);
    }

    document.querySelector(slider.btnPrev).onclick = slider.prev;   //attach methods to buttons
    document.querySelector(slider.btnNext).onclick = slider.next;
}