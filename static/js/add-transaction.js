const transactionForm = document.querySelector("#transaction-form");
const formError = document.querySelector("#form-error");
const categorySelect = document.querySelector("#category")

async function loadCategories() {
    const response = await fetch("api/categories");

    if (!response.ok) {
        throw new Error(
            `Failed to retrieve categories: ${response.status}`
        );
    }

    const categories = await response.json();

    if (
        !Array.isArray(categories) ||
        !categories.every((category) =>
            category !== null &&
        typeof category.name === "string" &&
        ["income", "expense"].includes(category.type)
        )
    ) {
        throw new Error("The server returned incorrect category data.");
    }

    if (categories.length === 0) {
        throw new Error("First, create a category in Settings.");
    }

    categorySelect.replaceChildren(
        new Option("Select a category", "")
    )

    for (const category of categories) {
        const option = new Option(
            `${category.name} (${category.type})`,
            category.name
        );
        categorySelect.append(option);
    }
}

loadCategories().catch((error) => {
    categorySelect.replaceChildren(
        new Option("Categories unavailable", "")
    );

    formError.textContent = error.message;
    formError.hidden = false;
});

transactionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    formError.textContent = "";
    formError.hidden = true;

    const submitButton = transactionForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    
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

    console.log(transaction);

    try {
        const response = await fetch("/api/transactions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            }, 
            body: JSON.stringify(transaction),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "Failed to add the operation");
        }
        window.location.assign("/");
    } catch (error) {
        formError.textContent = error.message;
        formError.hidden = false;
    } finally {
        submitButton.disabled = false;
    }
    
});