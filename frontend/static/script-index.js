document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("upload-form");
  const videoInput = document.getElementById("video-upload");
  const dropArea = document.getElementById("drop-area");
  const fileNameDisplay = document.getElementById("file-name");
  const browseBtn = document.getElementById("browse-btn");

  // Click on drop area triggers file input
  dropArea.addEventListener("click", () => videoInput.click());

  // Handle file select via input
  videoInput.addEventListener("change", () => {
    if (videoInput.files.length > 0) {
      fileNameDisplay.textContent = `Selected: ${videoInput.files[0].name}`;
    } else {
      fileNameDisplay.textContent = "No file selected";
    }
  });

  // Highlight on drag
  ["dragenter", "dragover"].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropArea.classList.add("highlight");
    });
  });

  // Unhighlight on leave/drop
  ["dragleave", "drop"].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropArea.classList.remove("highlight");
    });
  });

  // Handle dropped file
  dropArea.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
      const dt = new DataTransfer();
      dt.items.add(file);
      videoInput.files = dt.files;

      // Trigger change manually
      const changeEvent = new Event("change", { bubbles: true });
      videoInput.dispatchEvent(changeEvent);
    }
  });

  // Clicking the browse button triggers file input
  browseBtn.addEventListener("click", () => {
    videoInput.click();
  });

  // Submit form
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!videoInput.files.length) {
      alert("Please upload a video file.");
      return;
    }

    const formData = new FormData();
    formData.append("video", videoInput.files[0]);

    try {
      const response = await fetch("/predict", {
        method: "POST",
        body: formData,
      });

      // If server responds with a JSON object with redirect_url
      if (response.ok) {
        const result = await response.json();

        if (result.redirect_url) {
          // ✅ Redirect to result page and URL will change!
          window.location.href = result.redirect_url;
        } else {
          alert("Upload successful, but no redirect URL received.");
        }
      } else {
        const errorText = await response.text();
        alert("Upload failed: " + errorText);
      }
    } catch (error) {
      alert("Error uploading video: " + error.message);
    }
  });
});
