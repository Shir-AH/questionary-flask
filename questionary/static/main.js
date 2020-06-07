function newElement(elementType = '', classes = [], innerText = '') {
    let element = document.createElement(elementType);
    for (const c of classes)
        element.classList.add(c);
    element.innerText = innerText;
    return element;
}

function addQuestionLabel(destElement, questionName = '', categoryIndex = '', questionIndex = '') {
    let label = newElement('label', [`category-${categoryIndex}`, 'new'], questionName);
    label.for = `c${categoryIndex}q${questionIndex}`;
    destElement.appendChild(label);
    return label;
}

function addRangeInput(destElement, categoryIndex = '', questionIndex = '', subQuestion = false) {
    // add a range input for a specific question.
    let range = newElement('input', [`category-${categoryIndex}`, 'form-control-range', 'slider', 'questionary-input', 'new'])
    range.type = 'range';
    let name = `c${categoryIndex}q${questionIndex}`;
    if (subQuestion)
        name += 's';
    range.name = name;
    range.id = name;
    destElement.appendChild(range);
    return range;
}

function addQuestionHeader(destElement, headerText = '', categoryIndex = '') {
    // receive a question element and add a header to it.
    let header = newElement('h3', [`category-${categoryIndex}`, 'new'], headerText);
    destElement.appendChild(header);
    return header;
}

function addQuestion(fieldset, header = '', questionName = '', questionIndex = '', categoryIndex = '') {
    // add a question to the fieldset recevied.
    let subQuestion = !(header);
    if (!subQuestion)
        addQuestionHeader(fieldset, header, categoryIndex);
    addQuestionLabel(fieldset, questionName, categoryIndex, questionIndex);
    addRangeInput(fieldset, categoryIndex, questionIndex, subQuestion);
}

function buildCategory(fieldset, categoryQuestions, categoryIndex) {
    for (const qIndex in categoryQuestions) {
        addQuestion(fieldset,
            header = `${categoryQuestions[qIndex].question}`,
            questionName = 'רצון',
            questionIndex = qIndex,
            categoryIndex = categoryIndex);
        fieldset.appendChild(newElement('br'));
        addQuestion(fieldset,
            header = '',
            questionName = 'ניסיון',
            questionIndex = qIndex,
            categoryIndex = categoryIndex);
    }
}

function addCategory(formElement, category, categoryIndex) {
    // add all of the form category elements (section, header, fieldset).
    let fieldset = newElement('fieldset', [`category-${categoryIndex}`, 'form-fieldset', 'new']);
    fieldset.id = `category-${categoryIndex}-fieldset`;
    buildCategory(fieldset, category.questions, categoryIndex);

    let sectionHeader = newElement('h2', [`category-${categoryIndex}`, 'new'], category.name);

    let section = newElement('section', [`category-${categoryIndex}`, 'new']);
    section.id = `category-${categoryIndex}-section`;
    section.appendChild(sectionHeader);
    section.appendChild(fieldset);

    formElement.appendChild(section);
}

function addSubmitButton(formElement) {
    let sumbitButton = newElement('input', ['btn', 'btn-outline-info', 'questionary-input', 'questionary-button']);
    sumbitButton.type = 'submit';
    sumbitButton.id = 'submit';
    sumbitButton.value = 'סיימתי';
    formElement.appendChild(sumbitButton);
}

function buildForm(json) {
    // build the form inputs using the questions data receive 
    let data = json['data'];
    let form = document.getElementById("form");
    for (const categoryIndex in data) {
        let category = data[categoryIndex];
        addCategory(form, category, categoryIndex);
    }
    addSubmitButton(form);
}

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

function buildList(questionsJson) {
    let data = questionsJson['data'];
    let list = document.getElementById('categoryList');
    for (const categoryIndex in data) {
        let categoryName = data[categoryIndex].name;
        let li = newElement('li', ['list-group-item', 'chosen'], categoryName);
        li.id = `category-${categoryIndex}`;
        li.addEventListener('click', toggleCategory);
        list.appendChild(li);
    }
    let li = newElement('li', ['list-group-item', 'chosen'], 'הצג הכל');
    li.id = 'all-categories';
    li.addEventListener('click', showAllCategories);
    list.appendChild(li);
}

function presentForm() {
    // freeze and disable all of the form elements, remove uneccassary elements.
    let formButton = document.getElementById('submit');
    formButton.remove();
    let formInputs = document.getElementsByClassName('questionary-input');
    for (const field of formInputs)
        field.disabled = true;
    // remove results that are not user-answered.
    // this both hides unanswered questions, and protects old users from future questions change.
    let newResults = document.getElementsByClassName('new');
    while (newResults.length > 0)
        newResults[0].parentNode.removeChild(newResults[0]);
}

async function getAnswers(freeze = false, answerId = null) {
    let currentAnswerId = answerId;
    if (answerId === null) {
        currentAnswerId = await fetch(`${window.origin}/user/user_answer_id`)
            .then(response => {
                if (!response.ok)
                    throw new Error();
                return response.json();
            })
            .then(json => json)
            .catch(() => -1);
    }
    if (currentAnswerId !== -1) {
        fetch(`${window.origin}/get_answers/${currentAnswerId}`)
            .then(response => {
                if (!response.ok)
                    throw new Error();
                return response.json();
            })
            .then(json => fillForm(json))
            .catch(e => console.log(e))
            .finally(() => { if (freeze) presentForm(); });
    }
}

function fetchQuestions(freeze = false, answerId = null) {
    fetch(`${window.origin}/questions`)
        .then(response => {
            if (!response.ok)
                throw new Error();
            return response.json();
        })
        .then(json => { buildForm(json); buildList(json); })
        .then(() => getAnswers(freeze, answerId))
        .catch(e => { });
}

function fillForm(json) {
    for (const questionId in json) {
        if (json.hasOwnProperty(questionId)) {
            const questionValue = json[questionId];
            document.getElementById(questionId).defaultValue = questionValue;
            let currentCategory = `category-${questionId.slice(1, 2)}`;
            let categoryElements = document.getElementsByClassName(currentCategory);
            for (const elm of categoryElements)
                elm.classList.remove('new');
        }
    }
}

function selectCategories() {
    // used when submitting the form. removing all of the hidden categories from the form, so they wont be saved.
    let hiddenElements = document.getElementsByClassName('hidden');
    while (hiddenElements.length > 0)
        hiddenElements[0].parentNode.removeChild(hiddenElements[0]);
    return true;
}