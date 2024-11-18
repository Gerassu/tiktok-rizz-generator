class VideoConsole {

    constructor() {

        this.initializeElements();
        this.setupEventListeners();
        this.files = {
            subtitle: null,
            audio: null
        };

    }

    // Get page elements 

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

    // Setup upload using both click and drag & drop

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

    // Handle file upload 

    handleFileUpload(event, fileType) {

        const file = event.target.files[0];

        if (file) {
            this.files[fileType] = file;
            this.elements[`${fileType}Upload`].textContent = file.name;
            this.updateStatus(`${fileType} file uploaded: ${file.name}`);
        }

    }

    // Fetch to API server, update message status, decode and ecode data.video_data.content to videoplayer

    async generateVideo() {

        this.updateStatus('Preparing video generation...');
        
        const formData = new FormData();

        // Currently Useless

        formData.append('videoLength', this.elements.videoLength.value);
        formData.append('videoWidth', this.elements.videoWidth.value);
        formData.append('videoHeight', this.elements.videoHeight.value);
        
        // Subtitle file is not necessary / unused

        if (this.files.subtitle) formData.append('subtitle', this.files.subtitle);
        if (this.files.audio) formData.append('audio', this.files.audio);

        //console.log(formData)


        // Fetch to API, check response status then decode/encode

        try {

            this.updateStatus('Sending request to server...');

            const response = await fetch("http://192.168.1.9:7231/api/generate-video", {

                method: 'POST',
                credentials: "include",
                body: formData,

            });


            if (!response.ok) throw new Error('error generating video. Check API server');

            const data = await response.json();

            if(data.status == "success"){

                this.updateStatus('Video generated successfully!');

                const reader = new FileReader();

                //console.log(data.video_data.content)

                // Create new blob from content response

                const videoBlob = this.base64ToBlob(

                    data.video_data.content,
                    "video/mp4"

                );

                // Manage create .mp4 blob, add a new object url

                const VideoUrl = URL.createObjectURL(videoBlob)

                // Update the videoplayer to display blob

                const videoElement = document.getElementById("videoPlayer");;

                videoElement.src = VideoUrl;

                videoElement.onload = function (){

                    URL.revokeObjectURL(videoBlob);

                }

                reader.readAsDataURL(videoBlob)

                //      Handles automatic download, useful when testing
                /*const downloadLink = document.createElement('a');
                downloadLink.href = VideoUrl;
                downloadLink.download = 'test.mp4';
                document.body.appendChild(downloadLink);
                downloadLink.click();*/
                

            } else {

                throw new Error(data.message || "uknown error occured")

            }
           
        } catch (error) {

            this.updateStatus(`Error: ${error.message}`);

        }

    }

    // Managed encoding and decoding of JSON response; dont touch since it randomly started outputting non corrupted files

    base64ToBlob(base64, mimetype) {

        const byteCharacters = atob(base64);

        const byteNumbers = new Array(byteCharacters.length);

        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);

        return new Blob([byteArray], {type: mimetype});

    }

    // Update text below video
    
    updateStatus(message) {

        this.elements.statusBar.textContent = message;

    }

}


// Initialize the console when the page loads

window.addEventListener('DOMContentLoaded', () => {

    new VideoConsole();

});