const transactionForm = document.querySelector("#edit-transaction-form");
const formError = document.querySelector("#form-error");

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