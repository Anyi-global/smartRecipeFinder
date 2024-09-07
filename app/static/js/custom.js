function searchBooks() {
    const query = document.getElementById('query').value;

    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';

            if (data.items && data.items.length > 0) {
                data.items.forEach(book => {
                    const title = book.volumeInfo.title;
                    const author = book.volumeInfo.authors ? book.volumeInfo.authors.join(', ') : 'Unknown Author';
                    const thumbnail = book.volumeInfo.imageLinks ? book.volumeInfo.imageLinks.thumbnail : '';
                    const link = book.volumeInfo.infoLink; // Extract the link to the book on Google Books

                    const bookDiv = document.createElement('div');
                    bookDiv.classList.add('col-md-4');
                    bookDiv.innerHTML = `
                        <div class="card mb-4">
                            <img src="${thumbnail}" class="card-img-top" alt="${title} thumbnail">
                            <div class="card-body">
                                <h6 class="card-title">${title}</h6>
                                <p class="card-text">Author: ${author}</p>
                                <a href="${link}" class="btn btn-primary" target="_blank">Read Book</a>
                            </div>
                        </div>
                    `;

                    resultsDiv.appendChild(bookDiv);
                });
            } else {
                resultsDiv.innerHTML = '<p>No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
