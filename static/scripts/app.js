const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const cameraBtn = document.getElementById('cameraBtn');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const uploadForm = document.getElementById('uploadForm');
const cancelBtn = document.getElementById('cancelBtn');
const scanBtn = document.getElementById('scanBtn');
const loadingSection = document.getElementById('loadingSection');

let selectedFile = null;

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'rgba(255, 255, 255, 0.6)';
    uploadArea.style.background = 'rgba(255, 255, 255, 0.05)';
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'rgba(255, 255, 255, 0.4)';
    uploadArea.style.background = 'transparent';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'rgba(255, 255, 255, 0.4)';
    uploadArea.style.background = 'transparent';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

cameraBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } 
        });
        
        const video = document.createElement('video');
        video.srcObject = stream;
        video.autoplay = true;
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 20px;
        `;
        
        video.style.cssText = `
            max-width: 90%;
            max-height: 70vh;
            border-radius: 16px;
        `;
        
        const captureBtn = document.createElement('button');
        captureBtn.textContent = 'Capture';
        captureBtn.className = 'btn-primary';
        captureBtn.style.cssText = `
            padding: 1rem 3rem;
            font-size: 1.125rem;
        `;
        
        const closeBtn = document.createElement('button');
        closeBtn.textContent = 'Cancel';
        closeBtn.className = 'btn-secondary';
        closeBtn.style.cssText = `
            padding: 1rem 3rem;
            font-size: 1.125rem;
        `;
        
        modal.appendChild(video);
        modal.appendChild(captureBtn);
        modal.appendChild(closeBtn);
        document.body.appendChild(modal);
        
        captureBtn.addEventListener('click', () => {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            canvas.toBlob((blob) => {
                const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                handleFileSelect(file);
                stream.getTracks().forEach(track => track.stop());
                document.body.removeChild(modal);
            }, 'image/jpeg');
        });
        
        closeBtn.addEventListener('click', () => {
            stream.getTracks().forEach(track => track.stop());
            document.body.removeChild(modal);
        });
        
    } catch (error) {
        console.error('Camera access error:', error);
        alert('Unable to access camera. Please ensure camera permissions are granted.');
    }
});

function handleFileSelect(file) {
    if (!file.type.match('image.*')) {
        alert('Please select an image file');
        return;
    }
    
    selectedFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadArea.parentElement.style.display = 'none';
        previewSection.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

cancelBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    previewSection.style.display = 'none';
    uploadArea.parentElement.style.display = 'block';
});

scanBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    previewSection.style.display = 'none';
    loadingSection.style.display = 'block';
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    try {
        const response = await fetch('/api/scan/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            loadingSection.style.display = 'none';
            previewSection.style.display = 'block';
            return;
        }
        
        const resultsUrl = '/results/?data=' + encodeURIComponent(JSON.stringify(data));
        window.location.href = resultsUrl;
        
    } catch (error) {
        console.error('Scan error:', error);
        alert('An error occurred while scanning. Please try again.');
        loadingSection.style.display = 'none';
        previewSection.style.display = 'block';
    }
});
