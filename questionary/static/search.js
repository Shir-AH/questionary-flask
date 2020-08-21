function search() {
    let srcelm = document.getElementById("searchField");
    let search_str = srcelm.value;
    let search_url = `${window.location.origin}/search/${search_str}`;
    window.location.replace(search_url);
}

function setSearchEvent() {
    // set the event for the search field
    document.getElementById('searchField').onkeydown = (event) => {
        if (event.keyCode == 13) {
            search();
        }
    }
}