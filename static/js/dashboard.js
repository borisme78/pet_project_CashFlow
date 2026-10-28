const transactionsBody = document.querySelector("#transactions-body");
const balanceElement = document.querySelector("#total-balance");
const expensesElement = document.querySelector("#total-expenses");
const incomeElement = document.querySelector("#total-income");
const categoriesGrid = document.querySelector("#categories-grid");
const typeFilter = document.querySelector("#transaction-type-filter");
const categoryFilter = document.querySelector("#transaction-category-filter");

let allTransactions = [];

// Завантажуємо транзакції з Flask API.
async function loadTransactions() {
  const response = await fetch("/api/transactions");

  if (!response.ok) {
    throw new Error(`Failed to load operations: ${response.status}`);
  }

  const transactions = await response.json();
  allTransactions = transactions;
  const expensesByCategory = calculateExpensesByCategory(transactions);
  console.log("Expenses by category:", expensesByCategory);

  const labels = Object.keys(expensesByCategory);
  const amounts = Object.values(expensesByCategory);
  renderExpensesChart(labels, amounts);
  console.log(labels, amounts);
  updateSummary(transactions);
  console.log(transactions);

  const visibleTransactions = filterTransactions(
    allTransactions,
    typeFilter.value
  );
  renderTransaction(visibleTransactions);
}

  


function renderTransaction(transactions) {
    // Прибираємо попередній вміст перед побудовою таблиці.
  transactionsBody.textContent = "";

  if (transactions.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 6;
    if (allTransactions.length === 0) {
      cell.textContent = "There are no transactions yet.";
    }
    else {
      cell.textContent = "No transactions match the selected filter.";
    }

    row.append(cell);
    transactionsBody.append(row);

    return;
  }

  for (const transaction of transactions) {
    // Створюємо рядок для поточної транзакції.
    const row = document.createElement("tr");

    const dateCell = document.createElement("td");
    dateCell.textContent = transaction.date;
    row.append(dateCell);

    const categoryCell = document.createElement("td");
    categoryCell.textContent = transaction.category;
    row.append(categoryCell);

    const typeCell = document.createElement("td");
    typeCell.textContent = transaction.type;
    row.append(typeCell);

    // Форматуємо суму для відображення у гривнях.
    const amountCell = document.createElement("td");
    amountCell.className = transaction.type;
    amountCell.textContent = `${Number(transaction.amount).toFixed(2)} ₴`;
    row.append(amountCell);

    const descriptionCell = document.createElement("td");
    descriptionCell.textContent = transaction.description;
    row.append(descriptionCell);

    // Додаємо перехід до форми редагування.
    const actionsCell = document.createElement("td");
    const editLink = document.createElement("a");
    editLink.textContent = "Edit";
    editLink.className = "btn-action";
    editLink.href = `/edit/${transaction.id}`;
    actionsCell.append(editLink);

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.className = "btn-action delete";

    // Видаляємо операцію через API після підтвердження.
    deleteButton.addEventListener("click", async () => {
      if (!confirm("Delete transaction?")) {
        return;
      }

      // Блокуємо повторні натискання на час запиту.
      deleteButton.disabled = true;

      try {
        const response = await fetch(`/api/transactions/${transaction.id}`, {
          method: "DELETE",
        });

        if (!response.ok) {
          throw new Error(`Failed to delete: ${response.status}`);
        }

        // Прибираємо рядок лише після успішної відповіді сервера.
        await loadTransactions();
      } catch (error) {
        alert(error.message);
      } finally {
        deleteButton.disabled = false;
      }
  });

  actionsCell.append(deleteButton);
  row.append(actionsCell);
  transactionsBody.append(row); 
  }
}


function updateSummary(transactions) {
    let income = 0;
    let expenses = 0;

    for(const transaction of transactions) {
        const amount = Number(transaction.amount);

        if (transaction.type === "income") {
            income += amount;
        } else if (transaction.type === "expense") {
            expenses += amount; 
        }
    }
    const balance = income - expenses;

    incomeElement.textContent = `${income.toFixed(2)} ₴`;
    expensesElement.textContent = `${expenses.toFixed(2)} ₴`;
    balanceElement.textContent = `${balance.toFixed(2)} ₴`;
}

// Показуємо помилку завантаження в усіх шести стовпцях.
loadTransactions().catch((error) => {
  balanceElement.textContent = "Unavailable";
  expensesElement.textContent = "Unavailable";
  incomeElement.textContent = "Unavailable";
  transactionsBody.textContent = "";

  const row = document.createElement("tr");
  const cell = document.createElement("td");

  cell.colSpan = 6;
  cell.textContent = error.message;

  row.append(cell);
  transactionsBody.append(row);
});



async function loadCategories() {
  const response = await fetch("/api/categories");

  if (!response.ok) {
    throw new Error(`Failed: ${response.status}`);

  }
  const categories = await response.json();

  console.log(categories);
  
  categoriesGrid.textContent = "";

  if (categories.length === 0){
    categoriesGrid.textContent = "There are no categories yet.";
    return;
  }
  for ( const category of categories) {

    const option = document.createElement("option");
    option.value = category.name;
    option.textContent = category.name;


    const icon = document.createElement("div");
    icon.className = `icon-circle ${category.type}`;
    
    const initial = document.createElement("span");
    initial.textContent = category.name.charAt(0).toUpperCase();

    const card = document.createElement("div");
    card.className = "category-card";

    const info = document.createElement("div");
    info.className = "category-info";

    const name = document.createElement("span");
    name.className = "cat-name";
    name.textContent = category.name;

    const type = document.createElement("span");
    type.className = "cat-type";
    if (category.type === "income") {
      type.textContent = "Income";
    }
    else {
      type.textContent = "Expense";
    }


    icon.append(initial);
    info.append(name, type);
    card.append(icon, info);
    categoriesGrid.append(card);
    categoryFilter.append(option);

  }
  
}


loadCategories().catch((error) => {
  categoriesGrid.textContent = "Failed to load categories.";
  console.error(error);
});


function calculateExpensesByCategory(transactions) {
  const total = {};

  for (const transaction of transactions) {
    if (transaction.type === "expense") {
      const category = transaction.category;
      const amount = Number(transaction.amount);
      if (total[category] === undefined) {
        total[category] = 0;
      }
      total[category] += amount;
    }
  }
  return total;

}

let expensesChart = null;

function renderExpensesChart(labels, amount) {
  if (expensesChart !== null) {
    expensesChart.data.labels = labels;
    expensesChart.data.datasets[0].data = amount;
    expensesChart.update();
    return;
  }
  const canvas = document.querySelector("#dynamicsChart");

  expensesChart = new Chart(canvas, {
    type: "bar",
    data : {
      labels: labels,
      datasets: [{
        label: "Expenses, ₴", 
        data: amount,
        backgroundColor: "#00bcd4"
      }], 
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}

typeFilter.addEventListener('change', () => {
  const visibleTransactions = filterTransactions(allTransactions, typeFilter.value);
  renderTransaction(visibleTransactions);
});

function filterTransactions(transactions, selectType, selectedCategory) {
  if (selectType === "") {
    return transactions;
  }

  return transactions.filter((transaction) => {
    return transaction.type === selectType;
  });
}