function newElement(elementType = '', classes = [], innerText = '') {
    let element = document.createElement(elementType);
    for (const c of classes)
        element.classList.add(c);
    element.innerText = innerText;
    return element;
}

function addQuestionLabel(destElement, questionName = '', categoryIndex = '', questionIndex = '') {
    let label = newElement('label', [`category-${categoryIndex}`], questionName);
    label.for = `c${categoryIndex}q${questionIndex}`;
    destElement.appendChild(label);
    return label;
}

function addRangeInput(destElement, categoryIndex = '', questionIndex = '', subQuestion = false) {
    let range = newElement('input', [`category-${categoryIndex}`, 'form-control-range', 'slider'])
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
    let header = newElement('h3', [`category-${categoryIndex}`], headerText);
    destElement.appendChild(header);
    return header;
}

function addQuestion(fieldset, header = '', questionName = '', questionIndex = '', categoryIndex = '') {
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
    let fieldset = newElement('fieldset', [`category-${categoryIndex}`, 'form-fieldset']);
    fieldset.id = `category-${categoryIndex}-fieldset`;
    buildCategory(fieldset, category.questions, categoryIndex);

    let sectionHeader = newElement('h2', [`category-${categoryIndex}`], category.name);

    let section = newElement('section', [`category-${categoryIndex}`]);
    section.id = `category-${categoryIndex}-section`;
    section.appendChild(sectionHeader);
    section.appendChild(fieldset);

    formElement.appendChild(section);
}

function addSubmitButton(formElement, data) {
    let sumbitButton = newElement('input', ['btn', 'btn-outline-info']);
    sumbitButton.type = 'submit';
    sumbitButton.id = 'submit';
    sumbitButton.value = 'סיימתי';
    for (const categoryIndex in data)
        sumbitButton.classList.add(`category-${categoryIndex}`);
    formElement.appendChild(sumbitButton);
}

function buildForm(json) {
    let data = json['data'];
    let form = document.getElementById("form");
    for (const categoryIndex in data) {
        let category = data[categoryIndex];
        addCategory(form, category, categoryIndex);
    }
    addSubmitButton(form, data);
}

function moveToCategory(evt) {
    let categoryClass = evt.currentTarget.id;
    for (const elm of document.getElementById('form').children)
        elm.classList.add('hidden');
    for (const elm of document.getElementsByClassName(categoryClass))
        elm.classList.remove('hidden');
    if (categoryClass === 'all-categories')
        for (const elm of document.getElementById('form').children)
            elm.classList.remove('hidden');
}

function buildList(json) {
    let data = json['data'];
    let list = document.getElementById('categoryList');
    for (const categoryIndex in data) {
        let categoryName = data[categoryIndex].name;
        let li = newElement('li', ['list-group-item'], categoryName);
        li.id = `category-${categoryIndex}`;
        li.addEventListener('click', moveToCategory);
        list.appendChild(li);
    }
    let li = newElement('li', ['list-group-item'], 'הצג הכל');
    li.id = 'all-categories';
    li.addEventListener('click', moveToCategory);
    list.appendChild(li);
}

function get_user_answer() {
    try {
        fetch(`${window.origin}/user/user_answer`)
            .then(response => {
                if (!response.ok)
                    throw new Error();
                return response.json();
            })
            .then(json => fill_form(json))
            .catch(e => { });
    }
    catch { }
}

function fetch_data() {
    try {
        fetch(`${window.origin}/questions`)
            .then(response => {
                if (!response.ok)
                    throw new Error();
                return response.json();
            })
            .then(json => { buildForm(json); buildList(json); })
            .catch(e => { });
    }
    catch { }
}

function fill_form(json) {
    for (const questionId in json) {
        if (json.hasOwnProperty(questionId)) {
            const questionValue = json[questionId];
            document.getElementById(questionId).defaultValue = questionValue;
        }
    }
}

fetch_data();
get_user_answer();
