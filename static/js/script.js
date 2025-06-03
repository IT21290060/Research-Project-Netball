document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('videoFile');
    const resultContainer = document.getElementById('results');
    const loadingIndicator = document.getElementById('loading');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const skillsList = document.getElementById('skillsList');
    const positionResult = document.getElementById('position');
    const positionImageDisplay = document.getElementById('positionImageDisplay');
    const positionImage = document.getElementById('positionImage');
    const positionLogo = document.getElementById('positionLogo'); // Logo element
    const fileNameDisplay = document.querySelector('.file-name');

    // Allowed video file extensions
    const allowedExtensions = ['mp4', 'avi', 'mov', 'mkv'];

    // Event listener for form submission
    uploadForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const file = fileInput.files[0];

        // Validate file input
        if (!file) {
            alert('Please select a video file.');
            return;
        }

        // Validate file extension
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (!allowedExtensions.includes(fileExtension)) {
            alert('Invalid file type. Allowed formats: MP4, AVI, MOV, MKV');
            return;
        }

        // Reset UI
        resultContainer.style.display = 'none';
        loadingIndicator.style.display = 'block';
        errorMessage.style.display = 'none';

        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Send video to the server for analysis
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            // Handle response errors
            if (!response.ok) throw new Error('Error processing the video.');

            // Parse response data
            const data = await response.json();

            // Display results
            displayResults(data);
        } catch (error) {
            // Show error message
            showError(error.message);
        } finally {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
        }
    });

    // Function to display analysis results
    function displayResults(data) {
        const { skills, position, video_id } = data;

        // Validate data
        if (!skills || !position) {
            showError('Prediction failed. Please try again.');
            return;
        }

        // Populate skills list
        skillsList.innerHTML = '';
        skills.forEach(skill => {
            const skillItem = document.createElement('li');
            skillItem.className = 'skill-item';
            skillItem.innerHTML = `
                <div class="skill-bar" style="width: ${skill.value}%"></div>
                <span class="skill-name">${skill.name}</span>
                <span class="skill-value">${skill.value}%</span>
            `;
            skillsList.appendChild(skillItem);
        });

        // Display predicted position
        positionResult.textContent = position;
        resultContainer.style.display = 'block';

        // Display uploaded video
        const videoDisplay = document.getElementById('videoDisplay');
        const uploadedVideo = document.getElementById('uploadedVideo');
        if (videoDisplay && uploadedVideo) {
            videoDisplay.style.display = 'block';
            uploadedVideo.src = `/uploads/${video_id}`;
        }

        // Display position-specific image
        displayPositionImage(position);

        // Display position logo
        displayPositionLogo(position);
    }

    // Function to display the position-specific image
    function displayPositionImage(position) {
        // Map positions to their corresponding image filenames
        const positionImages = {
            "Goal Attack": "goal_attack.jpg",
            "Goal Keeper": "goal_keeper.jpg",
            "Goal Shooter": "goal_shooter.jpg",
            "Goal Defence": "goal_defence.jpg",
            "Wing Attack": "wing_attack.jpg",
            "Wing Defence": "wing_defence.jpg",
            "Center": "center.jpg"
        };

        // Set the image source based on the predicted position
        if (positionImages[position] && positionImageDisplay && positionImage) {
            positionImage.src = `/static/image/${positionImages[position]}`;
            positionImageDisplay.style.display = 'block';
        } else {
            if (positionImageDisplay) positionImageDisplay.style.display = 'none';
        }
    }

    // Function to display the position logo
    function displayPositionLogo(position) {
        // Map positions to their corresponding logo filenames
        const positionLogos = {
            "Goal Attack": "goal_attack_logo.jpg",
            "Goal Keeper": "goal_keeper_logo.jpg",
            "Goal Shooter": "goal_shooter_logo.jpg",
            "Goal Defence": "goal_defence_logo.jpg",
            "Wing Attack": "wing_attack_logo.jpg",
            "Wing Defence": "wing_defence_logo.jpg",
            "Center": "center_logo.jpg"
        };

        // Set the logo source based on the predicted position
        if (positionLogos[position] && positionLogo) {
            positionLogo.src = `/static/image/${positionLogos[position]}`;
            positionLogo.style.display = 'block'; // Show the logo
        } else {
            if (positionLogo) positionLogo.style.display = 'none'; // Hide the logo
        }
    }

    // Function to show error messages
    function showError(message) {
        if (errorText) errorText.textContent = message;
        if (errorMessage) errorMessage.style.display = 'block';
    }

    // Event listener for file input change
    fileInput.addEventListener('change', () => {
        if (fileNameDisplay) {
            fileNameDisplay.textContent = fileInput.files[0]?.name || 'No file selected';
        }
    });
});

$(document).ready(function () {
    $(".sub-btn").click(function () {
      $(this).next(".sub-menu").slideToggle();
    });
    $(".more-btn").click(function () {
      $(this).next(".more-menu").slideToggle();
    });
  });
  
  var menu = document.querySelector(".menu");
  var menuBtn = document.querySelector(".menu-btn");
  var closeBtn = document.querySelector(".close-btn");
  
  menuBtn.addEventListener("click", () => {
    menu.classList.add("active");
  });
  closeBtn.addEventListener("click", () => {
    menu.classList.remove("active");
  });
  
  window.addEventListener("scroll", function () {
    var header = this.document.querySelector("header");
    header.classList.toggle("sticky", window.scrollY > 0);
  });