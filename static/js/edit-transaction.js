const transactionForm = document.querySelector("#edit-transaction-form");
const formError = document.querySelector("#form-error");
const formFields = document.querySelector("#transaction-fields");

function fillTransactionForm(transaction) {
    // Знаходимо поле суми у формі.
    const amountInput = transactionForm.querySelector("#amount");

    // Записуємо суму, отриману через API.
    amountInput.value = transaction.amount;

    transactionForm.querySelector("#type").value = transaction.type;
    transactionForm.querySelector("#date").value = transaction.date;
    transactionForm.querySelector("#category").value = transaction.category;

    
    transactionForm.querySelector("#description").value =
        transaction.description ?? "";
}

async function loadTransaction() {
    const apiUrl = transactionForm.dataset.apiUrl;

    const response = await fetch(apiUrl)

    if (!response.ok) {
        throw new Error(
            `Failed to load the transaction: ${response.status}`
        );
    }

    const transaction = await response.json();

    if (
        transaction === null ||
        typeof transaction !== "object" ||
        !Number.isInteger(transaction.id)
    ){
        throw new Error("The server returned incorrect transaction data.")
    }

    fillTransactionForm(transaction);
    formFields.disabled = false;
}

loadTransaction().catch((error) => {
    formError.textContent = error.message;
    formError.hidden = false;
})

transactionForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const apiUrl = transactionForm.dataset.apiUrl;
    const formData = new FormData(transactionForm);

    const amount = formData.get("amount");
    const type = formData.get("type");
    const date = formData.get("date");
    const category = formData.get("category");
    const description = formData.get("description");

    const transaction = {
        amount: amount,
        type: type,
        date: date,
        category: category,
        description: description,
    };

    formError.textContent = "";
    formError.hidden = true;

    const submitButton = transactionForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
        const response = await fetch(apiUrl, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(transaction),
        });  

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "Failed to update the operation");
        }
        window.location.assign("/");
    } catch (error) {
        formError.textContent = error.message;
        formError.hidden = false;
    } finally {
        submitButton.disabled = false;
    }

    
});
