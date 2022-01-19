window.addEventListener("load", function () {
    let isCNBasionymCheckbox = document.getElementById("id_bn-is_current_name_basionym")

    isCNBasionymCheckbox.addEventListener('click', toggleIsCNBasionymCheckbox)
});

function toggleIsCNBasionymCheckbox(event) {
    let basionymFieldset = document.getElementById("basionymFieldset")
    let checkbox = event.currentTarget
    if (checkbox.checked) {
        basionymFieldset.setAttribute("disabled", "true")
    } else {
        basionymFieldset.removeAttribute("disabled")
    }
}