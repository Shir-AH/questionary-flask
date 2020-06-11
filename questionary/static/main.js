function toggleSelectAll() {
    // bold select all when all categories are selected
    let liElements = document.getElementsByClassName('list-group-item');
    for (const elm of liElements)
        if (!elm.classList.contains('chosen'))
            document.getElementById('all-categories').classList.remove('chosen');
}

function toggleCategory(evt) {
    // hide category when it's list item is pressed.
    let categoryClass = evt.currentTarget.id;
    evt.currentTarget.classList.toggle('chosen');
    for (const elm of document.getElementsByClassName(categoryClass))
        elm.classList.toggle('hidden');
    toggleSelectAll();
}

function showAllCategories(evt) {
    // un-hide all categories
    let elements = document.getElementsByClassName('hidden');
    while (elements.length > 0)
        elements[0].classList.remove('hidden');
    for (const elm of document.getElementsByClassName('list-group-item'))
        elm.classList.add('chosen');
}

function selectCategories() {
    // used when submitting the form. removing all of the hidden categories from the form, so they wont be saved.
    let hiddenElements = document.getElementsByClassName('hidden');
    while (hiddenElements.length > 0)
        hiddenElements[0].parentNode.removeChild(hiddenElements[0]);
    return true;
}