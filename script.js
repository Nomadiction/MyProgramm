const pathInput = document.getElementById("path");
const idInput = document.getElementById("id");
const select = document.querySelector("select");
const resultText = document.getElementById("resultText");
const button = document.getElementById('start_button');
const output = document.getElementById('seed_phrase');

const values = [];


function updateResultText() {
  resultText.textContent = "Complete editing and press start..."
}

function handleClick(event) {
  event.preventDefault();
  if(!pathInput.value || !idInput.value || !select.value) {

    resultText.textContent = "Please fill out all fields";
    return;
  }
  writeToFile(values);
}

function writeToFile(data) {
  const json = JSON.stringify(data);
  const blob = new Blob([json], {type : 'application/json'});
  const dataURL = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = dataURL;
  link.download = 'data.json';
  link.click();

  resultText.textContent = "Data has been loaded please wait..."
}



pathInput.addEventListener('input', () => {
  // Получаем значение из элемента
  const pathValue = pathInput.value;
  // Удаляем предыдущие значения "EXTENSION PATH" из массива
  values.splice(
    values.findIndex(value => value.startsWith('EXTENSION')),
    values.filter(value => value.startsWith('EXTENSION')).length
  );
  // Добавляем новое значение "EXTENSION PATH" в массив
  values.push('EXTENSION: ' + pathValue);
  // Обновляем содержимое элемента resultText
  updateResultText();
});

idInput.addEventListener('input', () => {
  // Получаем значение из поля ввода
  const idValue = idInput.value;
  // Удаляем предыдущие значения "ID" из массива
  values.splice(
    values.findIndex(value => value.startsWith('ID')),
    values.filter(value => value.startsWith('ID')).length
  );
  // Добавляем новое значение "ID" в массив
  values.push('ID: ' + idValue);
  // Обновляем содержимое элемента resultText
  updateResultText();
});

select.addEventListener('change', (event) => {
  const selectedOption = event.target.value;
  // Удаляем предыдущие значения с префиксом "NUM" из массива
  values.splice(
    values.findIndex(value => value.startsWith('NUM')),
    values.filter(value => value.startsWith('NUM')).length
  );
  // Добавляем новое значение с префиксом "NUM" только если оно не существует в массиве
  if (!values.includes('NUM: ' + selectedOption)) {
    values.push('NUM: ' + selectedOption);
  }
  // Обновляем содержимое элемента resultText
  updateResultText();
});


button.addEventListener('click', handleClick);

resultText.textContent = "Process of bruting is running now"