document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("upload-form");
  const videoUpload = document.getElementById("video-upload");
  const resultDiv = document.getElementById("result");
  const predictionText = document.getElementById("prediction-text");
  const feedbackText = document.getElementById("feedback-text");
  const probabilityText = document.getElementById("probability-text");  // New element to display probability

  // Adding event listener to handle the form submission
  uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();  // Prevent the default form submission

    // Check if a video file has been uploaded
    if (!videoUpload.files[0]) {
      alert("Please upload a video.");
      return; // If no file, return early
    }

    // Create a FormData object to send the video file to the backend
    const formData = new FormData();
    formData.append("video", videoUpload.files[0]);

    try {
      // Before sending the request, set the texts to "Processing..."
      predictionText.textContent = "Processing...";
      feedbackText.textContent = "";
      probabilityText.textContent = "";  // Reset the probability text

      // Send the video file to the backend for prediction
      const response = await fetch("/predict", {
        method: "POST",
        body: formData,  // Attach the video file to the request
      });

      // Check if the response from the backend is not OK (i.e., an error occurred)
      if (!response.ok) {
        throw new Error("Failed to get prediction from the server.");
      }

      // Parse the JSON response from the backend
      const data = await response.json();

      // Display the prediction, feedback, and probability
      resultDiv.style.display = "block";  // Ensure the result div is visible
      predictionText.textContent = `Prediction: ${data.prediction}`;
      feedbackText.textContent = `Feedback: ${data.feedback}`;
      probabilityText.textContent = `Probability: ${data.probability}`;  // Display the probability
    } catch (error) {
      // If there's an error, display it in the result section
      resultDiv.style.display = "block";  // Make the result section visible
      predictionText.textContent = "Error processing video.";
      feedbackText.textContent = error.message;  // Display the error message
    }
  });
});
