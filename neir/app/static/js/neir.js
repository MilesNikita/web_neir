document.addEventListener('DOMContentLoaded', function() {
    const detectBtn = document.getElementById('detect-btn');
    const resultImage = document.getElementById('result-image');
    const resultVideo = document.getElementById('result-video');
    const imageInput = document.getElementById('image-input');
    const inputType = document.getElementById('input-type');

    detectBtn.addEventListener('click', function() {
        const selectedInputType = inputType.value;
        if (selectedInputType === 'image') {
            const fileInput = document.getElementById('image-input');
            if (fileInput.files.length === 0) {
                alert('Пожалуйста, выберите изображение для обработки');
                return;
            }
            const formData = new FormData();
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
                resultImage.style.display = 'block';
                resultImage.src = data.processed_image;
                resultVideo.style.display = 'none';
                resultVideo.src = ''; // Очистка источника видео
            })
            .catch(error => console.error('Error:', error));
        } else if (selectedInputType === 'video') {
            const fileInput = document.getElementById('image-input');
            if (fileInput.files.length == 0){
                alert('Пожалуйста, выберите видео для обработки');
                return;
            }
            const formData = new FormData();
            formData.append('input_type', selectedInputType);
            formData.append('video', fileInput.files[0]);
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
                resultImage.style.display = 'none';
                resultVideo.style.display = 'block';
                resultVideo.src = data.processed_video;
                resultImage.src = ''; 
            })
            .catch(error => console.error('Error:', error));
        }
    });
    inputType.addEventListener('change', function() {
        imageInput.value = ''; 
        resultImage.style.display = 'none';
        resultImage.src = ''; 
        resultVideo.style.display = 'none';
        resultVideo.src = ''; 
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
