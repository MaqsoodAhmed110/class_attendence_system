document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous results
        resultsDiv.innerHTML = '';

        // Add a loading message
        const loadingMessage = document.createElement('p');
        loadingMessage.textContent = 'Processing... Please wait.';
        loadingMessage.style.color = '#555';
        resultsDiv.appendChild(loadingMessage);

        const formData = new FormData(form);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to upload file. Please try again.');
            }

            const data = await response.json();

            // Remove the loading message
            resultsDiv.innerHTML = '';

            if (data.error) {
                resultsDiv.textContent = `Error: ${data.error}`;
                resultsDiv.style.color = 'red';
            } else if (data.predictions && data.predictions.length > 0) {
                resultsDiv.innerHTML = `<h3>Predictions:</h3>`;
                data.predictions.forEach(pred => {
                    resultsDiv.innerHTML += `
                        <p><strong>Label:</strong> ${pred.label}<br>
                        <strong>Confidence:</strong> ${pred.confidence}%<br>
                        <strong>Timestamp:</strong> ${pred.timestamp}</p>
                    `;
                });
            } else {
                resultsDiv.textContent = 'No predictions found.';
                resultsDiv.style.color = '#777';
            }
        } catch (error) {
            // Handle fetch errors
            resultsDiv.innerHTML = `<p style="color: red;">An error occurred: ${error.message}</p>`;
        }
    });
});
