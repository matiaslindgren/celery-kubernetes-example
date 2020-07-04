function postStringPair() {
  const stringA = document.getElementById("string-a-input").value;
  const stringB = document.getElementById("string-b-input").value;
  const postData = {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({str_a: stringA, str_b: stringB})
  };
  fetch("/task", postData)
    .then(response => response.json())
    .then(data => {
      refreshTasksTable();
    }).catch(error => {
      console.error("Error when trying to POST user input to server:", error);
    });
}

function elementWithText(tag, text) {
  const e = document.createElement(tag);
  e.innerText = text;
  return e;
}

const taskKeys = ["id", "created", "finished", "result"];

function generateTableHeader() {
  const thead = document.createElement("thead");
  const tr = document.createElement("tr");
  for (let key of taskKeys) {
    tr.appendChild(elementWithText("th", key));
  }
  thead.appendChild(tr);
  return thead;
}

function removeAllChildren(e) {
  while (e.firstChild) {
    e.removeChild(e.firstChild);
  }
}

function refreshTasksTable() {
  fetch("/tasks-json")
    .then(response => response.json())
    .then(data => {
      const newTable = document.createElement("table");
      newTable.appendChild(generateTableHeader());
      const tbody = document.createElement("tbody");
      for (let task of data.all_tasks) {
        const tr = document.createElement("tr");
        for (let key of taskKeys) {
          tr.appendChild(elementWithText("td", task[key]));
        }
        tbody.appendChild(tr);
      }
      newTable.appendChild(tbody);
      const tableContainer = document.getElementById("tasks-table-container");
      removeAllChildren(tableContainer);
      tableContainer.appendChild(newTable);
    }).catch(error => {
      console.error("Error when trying to GET new contents for tasks table:", error);
    });
}

document.addEventListener("DOMContentLoaded", _ => {
  refreshTasksTable();
  const submitButton = document.getElementById("submit-button");
  submitButton.addEventListener("click", postStringPair);
  const refreshButton = document.getElementById("refresh-button");
  refreshButton.addEventListener("click", refreshTasksTable);
});
