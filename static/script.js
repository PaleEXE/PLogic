// Function to display results on the webpage
function displayResult(data) {
    const resultElement = document.getElementById('result');
    resultElement.innerHTML = '';
    resultElement.classList.remove('error');

    // Display the evaluated expression
    if (data.expression) {
        const expressionElement = document.createElement('h3');
        expressionElement.textContent = `Expression: ${data.expression}`;
        resultElement.appendChild(expressionElement);
    }

    // Display the truth table in a table format
    if (data.truth_table) {
        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');

        // Create table header
        const headerRow = document.createElement('tr');
        Object.keys(data.truth_table[0]).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create table body
        data.truth_table.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(value => {
                const td = document.createElement('td');
                // Check if the value is an object
                td.textContent = (typeof value === 'object') ? JSON.stringify(value) : value; // Convert object to string
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        resultElement.appendChild(table);
    }

    // Display equality result of expressions
    if (data.are_equal !== undefined) {
        const equalityElement = document.createElement('p');
        equalityElement.textContent = `Expressions are ${data.are_equal ? 'equal' : 'not equal'}.`;
        resultElement.appendChild(equalityElement);
    }

    // Display conditions used in the evaluation
    if (data.conditions) {
        const conditionsElement = document.createElement('h4');
        conditionsElement.textContent = 'Conditions:';
        resultElement.appendChild(conditionsElement);
        const conditionsList = document.createElement('ul');
        Object.entries(data.conditions).forEach(([key, value]) => {
            const li = document.createElement('li');
            li.textContent = `${key}: ${value}`;
            conditionsList.appendChild(li);
        });
        resultElement.appendChild(conditionsList);
    }
}

// Function to evaluate an expression
async function evaluateExpression() {
    const expression = document.getElementById("expression").value;
    try {
        const response = await axios.post("http://127.0.0.1:8000/evaluate", { expression });
        displayResult(response.data);
    } catch (error) {
        console.error("Error evaluating expression:", error);
        document.getElementById('result').classList.add('error');
        document.getElementById('result').textContent = error.response?.data?.detail || 'Error occurred while evaluating expression.';
    }
}

// Function to compare two expressions
async function compareExpressions() {
    const expression1 = document.getElementById("expression1").value;
    const expression2 = document.getElementById("expression2").value;
    try {
        const response = await axios.post("http://127.0.0.1:8000/compare", [expression1, expression2]);
        displayResult(response.data);
    } catch (error) {
        console.error("Error comparing expressions:", error);
        document.getElementById('result').classList.add('error');
        document.getElementById('result').textContent = error.response?.data?.detail || 'Error occurred while comparing expressions.';
    }
}

// Function to evaluate a where condition
async function whereCondition() {
    const expression = document.getElementById("whereExpression").value;
    const conditions = document.getElementById("conditions").value;

    // Convert `a:1, b:0` to a JSON object
    const parsedConditions = conditions.split(',')
        .map(pair => pair.trim().split(':'))
        .reduce((obj, [key, value]) => {
            obj[key.trim()] = parseInt(value.trim());
            return obj;
        }, {});

    try {
        const response = await axios.post("http://127.0.0.1:8000/where", {
            expression,
            conditions: parsedConditions
        });
        displayResult(response.data);
    } catch (error) {
        console.error("Error in where condition:", error);
        document.getElementById('result').classList.add('error');
        document.getElementById('result').textContent = error.response?.data?.detail || 'Error occurred while evaluating where condition.';
    }
}