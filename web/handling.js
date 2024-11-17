class VideoConsole {
    constructor() {
        this.initializeElements();
        this.setupEventListeners();
        this.files = {
            subtitle: null,
            audio: null
        };
    }

    initializeElements() {
        this.elements = {
            videoLength: document.getElementById('videoLength'),
            videoWidth: document.getElementById('videoWidth'),
            videoHeight: document.getElementById('videoHeight'),
            subtitleUpload: document.getElementById('subtitleUpload'),
            audioUpload: document.getElementById('audioUpload'),
            generateBtn: document.getElementById('generateBtn'),
            videoPreview: document.getElementById('videoPreview'),
            statusBar: document.getElementById('statusBar')
        };
    }

    setupEventListeners() {
        this.setupFileUpload('subtitleUpload', 'subtitle');
        this.setupFileUpload('audioUpload', 'audio');
        this.elements.generateBtn.addEventListener('click', () => this.generateVideo());
    }

    setupFileUpload(elementId, fileType) {
        const element = this.elements[elementId];
        
        element.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = fileType === 'subtitle' ? '.srt,.vtt,.txt' : '.mp3,.wav';
            input.onchange = (e) => this.handleFileUpload(e, fileType);
            input.click();
        });

        element.addEventListener('dragover', (e) => {
            e.preventDefault();
            element.style.backgroundColor = 'var(--color-mid)';
        });

        element.addEventListener('dragleave', (e) => {
            e.preventDefault();
            element.style.backgroundColor = 'var(--color-mid-dark)';
        });

        element.addEventListener('drop', (e) => {
            e.preventDefault();
            element.style.backgroundColor = 'var(--color-mid-dark)';
            const file = e.dataTransfer.files[0];
            this.handleFileUpload({ target: { files: [file] } }, fileType);
        });
    }

    handleFileUpload(event, fileType) {
        const file = event.target.files[0];
        if (file) {
            this.files[fileType] = file;
            this.elements[`${fileType}Upload`].textContent = file.name;
            this.updateStatus(`${fileType} file uploaded: ${file.name}`);
        }
    }

    async generateVideo() {
        this.updateStatus('Preparing video generation...');
        
        const formData = new FormData();
        formData.append('videoLength', this.elements.videoLength.value);
        formData.append('videoWidth', this.elements.videoWidth.value);
        formData.append('videoHeight', this.elements.videoHeight.value);
        
        if (this.files.subtitle) formData.append('subtitle', this.files.subtitle);
        if (this.files.audio) formData.append('audio', this.files.audio);
        console.log(formData)
        try {
            this.updateStatus('Sending request to server...');
            const response = await fetch("http://127.0.0.1:7231/api/generate-video", {
                method: 'POST',
                credentials: "include",
                body: formData,
            });

            if (!response.ok) throw new Error('oh no! you stupid.');
            
            const data = await response.json();
            if(data.status == "success"){
                this.updateStatus('Video generated successfully!');

                // generate video from tuple
    
                const videoElement = document.createElement("video");
                videoElement.controls = false;
                videoElement.style.width = "100%";
                videoElement.style.height = "100%";
    
                const videoBlob = this.base64ToBlob(
                    data.video_data.content,
                    "video/mp4;base64"
                );

                console.log(videoBlob)
                this.videoPath = data.video_data.path


                const videoUrl = URL.createObjectURL(videoBlob);

                
                console.log(videoUrl)
                videoElement.src = videoUrl
    
                const pewcontainer = this.elements.videoPreview.parentElement;
                pewcontainer.removeChild(this.elements.videoPreview);
                pewcontainer.appendChild(videoElement);
                this.elements.videoPreview = videoElement
    
    
   
    
    
                this.elements.videoPreview.src = data.videoUrl;
            } else {
                throw new Error(data.message || "uknown error occured")
            }
           
        } catch (error) {
            this.updateStatus(`Error: ${error.message}`);
        }
    }

    base64ToBlob(base64, mimetype) {
        const byteCharacter = atob(base64)
        const byteNumbers = new Array(byteCharacter.length);

        for(let i = 0; i < byteCharacter.length; i++){
            byteNumbers[1] = byteCharacter.charCodeAt(i)
        }

        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: mimetype });

    }

    updateStatus(message) {
        this.elements.statusBar.textContent = message;
    }
}

// Initialize the console when the page loads
window.addEventListener('DOMContentLoaded', () => {
    new VideoConsole();
});