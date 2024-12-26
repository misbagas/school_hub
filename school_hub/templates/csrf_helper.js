function getCsrfToken() {
    const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrf_token='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}

function submitFormWithCSRF() {
    const csrfToken = getCsrfToken();
    const formData = new FormData(document.querySelector('form'));

    fetch('/login', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken  // Flask-WTF expects 'X-CSRFToken' header
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
