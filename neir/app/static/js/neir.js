document.addEventListener('DOMContentLoaded', function() {
    const detectBtn = document.getElementById('detect-btn');
    const resultImage = document.getElementById('result-image');

    detectBtn.addEventListener('click', function() {
        const selectedModel = document.getElementById('model').value;
        const selectedInputType = document.getElementById('input-type').value;
        const fileInput = document.getElementById('image-input');

        if (selectedModel === 'model1' && selectedInputType === 'image') {
            if (fileInput.files.length === 0) {
                alert('Пожалуйста, выберите изображение');
                return;
            }

            const formData = new FormData();
            formData.append('model', selectedModel);
            formData.append('input_type', selectedInputType);
            formData.append('image', fileInput.files[0]);

            fetch('/run_neural_network/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                resultImage.src = data.processed_image;
            })
            .catch(error => console.error('Error:', error));
        } else {
            fetch('/run_neural_network/', {
                method: 'POST',
                body: JSON.stringify({
                    model: selectedModel,
                    input_type: selectedInputType
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
            })
            .catch(error => console.error('Error:', error));
        }
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
