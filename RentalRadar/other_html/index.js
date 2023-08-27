// JavaScript to dynamically create the property list
const propertyList = [
    'Down Payment %',
    'Current Mortgage Interest Rate',
    'Property Tax Rate',
    'Average Monthly Expenses',
    'Increase % in Expenses',
    'Increase % in Rent Income',
    'Increase % in Property Value'
];

const analyzeForm = document.getElementById('analyze-form');
const propertyListContainer = document.querySelector('.property-list');

propertyList.forEach(property => {
    const listItem = document.createElement('li');
    listItem.innerHTML = 
    `
        <label for="${property.toLowerCase().replace(/\s/g, '-')}">${property}:</label>
        <input type="text" id="${property.toLowerCase().replace(/\s/g, '-')}">
    `;
    propertyListContainer.appendChild(listItem);
});

const analyzeButton = document.getElementById('analyze-button');

analyzeButton.addEventListener('click', function () {
    analyzeForm.style.display = 'block';
});
