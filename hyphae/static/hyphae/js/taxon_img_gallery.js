window.addEventListener("load", function () {
    addEvents();
})

function addEvents() {
    let thumbs = document.getElementsByClassName("tax-img-thumb");
    for (let i = 0; i < thumbs.length; i++) {
        thumbs[i].addEventListener("click", onThumbClick);
    }
}

function onThumbClick(event) {
    let thumb = event.target;
    let imgUrl = thumb.dataset.img
    let taxImg = document.getElementById("taxImg")

    removeActive()

    taxImg.src = imgUrl
    thumb.classList.add("active")
}

function removeActive() {
    let thumbs = document.getElementsByClassName("tax-img-thumb");
    for (let i = 0; i < thumbs.length; i++) {
        thumbs[i].classList.remove("active")
    }
}