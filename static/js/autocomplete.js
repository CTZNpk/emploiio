document.addEventListener("DOMContentLoaded", function () {
    const autocompleteFields = document.querySelectorAll('input[data-autocomplete="true"], textarea[data-autocomplete="true"]');

    autocompleteFields.forEach(field => {
        const isMultiple = field.dataset.multipleValues === "true";
        const suggestionType = field.name;
        const suggestions = window.suggestionDatabase?.[suggestionType] || [];

        field.addEventListener("input", function () {
            const container = createSuggestionBox(field);
            container.innerHTML = "";

            const rawValue = field.value;
            const currentInput = isMultiple
                ? rawValue.split(",").pop().trim().toLowerCase()
                : rawValue.toLowerCase();

            if (!currentInput) return;

            const matches = suggestions.filter(s => s.toLowerCase().includes(currentInput));

            matches.slice(0, 10).forEach(match => {
                const item = document.createElement("div");
                item.classList.add("autocomplete-item");
                item.textContent = match;
                item.addEventListener("click", () => {
                    if (isMultiple) {
                        const parts = rawValue.split(",");
                        parts[parts.length - 1] = match;
                        field.value = parts.map(p => p.trim()).filter(Boolean).join(", ") + ", ";
                    } else {
                        field.value = match;
                    }
                    container.innerHTML = "";
                    field.focus();
                });
                container.appendChild(item);
            });
        });

        field.addEventListener("blur", () => {
            setTimeout(() => {
                const container = field.parentElement.querySelector(".autocomplete-box");
                if (container) container.remove();
            }, 200);
        });
    });

    function createSuggestionBox(input) {
        let box = input.parentElement.querySelector(".autocomplete-box");
        if (!box) {
            box = document.createElement("div");
            box.classList.add("autocomplete-box");
            box.style.position = "absolute";
            box.style.zIndex = "1000";
            box.style.background = "white";
            box.style.border = "1px solid #ccc";
            box.style.width = input.offsetWidth + "px";
            input.parentElement.appendChild(box);
        }
        return box;
    }
});