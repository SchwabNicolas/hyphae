window.addEventListener("load", function () {
    initTreeView();
})

function initTreeView() {
    let treeview = document.getElementById("treeview");

    fetchData("").then((data) => {
        for (let i = 0; i < data.length; i++) {
            renderNode(data[i])
        }
    });
}

function renderNode(taxon) {
    let html =
        ```
            <div class="mb-1 tree-node active">
                <button type="button" class="btn toggle-node">
                    <i class="fas fa-chevron-right"></i>
                </button>
            <b><i>%current_name%</i></b>%authors% (%year_of_publication%)
            </div>
        ```

}

async function fetchData(slug) {
    let url = window.location.origin + '/taxonomy/api/list-taxon-children/'
    if (slug !== "") {
        url += "?slug=" + slug
    }

    return fetch(url)
        .then((response) => {
            return response.json().then((data) => {
                return data;
            }).catch((error) => {
                console.error('Error:', error);
                // displayAlert("ERROR", "Error")
            })
        });
}