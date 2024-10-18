// Base URL for the backend
const BASE_URL = "https://plogic.onrender.com"; // Replace with your actual backend URL

// Function to evaluate an expression
async function evaluateExpression() {
    const expression = document.getElementById("expression").value;
    try {
        const response = await axios.post(`${BASE_URL}/evaluate`, { expression });
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
        const response = await axios.post(`${BASE_URL}/compare`, [expression1, expression2]);
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
        const response = await axios.post(`${BASE_URL}/where`, {
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
