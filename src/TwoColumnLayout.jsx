import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faTrash } from "@fortawesome/free-solid-svg-icons"; // Import the Plus and Trash icons
import PerformanceCard from "./PerformanceCard";
import { useLocation } from "react-router-dom";

const TwoColumnLayout = () => {
  const [file, setFile] = useState(null); // to store the selected file
  const [error, setError] = useState(""); // for error messages
  const location = useLocation();
  const responseData = location.state?.data || {};
  console.log(responseData);
  let port = 0;

  if (responseData.exercise == "In_out" || responseData.exercise === "InOut Ladder Drill") {
    port = 5000;
 }
 
 else if (responseData.exercise == "360_rotation"|| responseData.exercise === "Balance") {
    port = 5002;
 }
 else if (responseData.exercise == "Squat" || responseData.exercise === "Power") {
    port = 5001;
 }
  // Handle normal file upload
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError("");
    }
  };

  // Handle drag and drop functionality
  const onDrop = (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError("");
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    multiple: false,
    accept: ".jpg, .jpeg, .png, .pdf, .doc, .docx", // adjust this to the file types you want to accept
  });

  // Handle file deletion
  const handleDelete = () => {
    setFile(null);
  };

  // Handle form submission
  const handleDetect = () => {
    if (!file) {
      setError("Please upload a file before submitting.");
      return;
    }
    // Simulate a form submission or file detection logic
    console.log("File submitted:", file);
  };

  return (
    <div style={styles.container}>
      <div style={styles.formContainer}>
        <div style={styles.columns}>
          {/* Left Column (File Upload Section) */}
          <div style={styles.column}>
            <video controls width="100%">
              <source
                src={`http://127.0.0.1:${port}/uploads/${responseData.file}`}
                type="video/mp4"
              />
              Your browser does not support the video tag.
            </video>
          </div>

          {/* Right Column (Additional Content or Form Section) */}
          <div style={styles.column}>
            <PerformanceCard data={responseData} />
          </div>
        </div>
      </div>
    </div>
  );
};

// Inline styles for the component
const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",

    margin: "0", // Removes default margin from body
    backgroundColor: "#1e3a5f", // Dark blue background color
    color: "white",
  },
  formContainer: {
    padding: "20px",
    borderRadius: "8px",
    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
    backgroundColor: "white",
    width: "100%",
    maxWidth: "1000px", // Max-width for the whole form container
    margin: "20px", // Adds some margin around the form
    backgroundColor: "#1e3a5f", // Dark blue background color
  },
  columns: {
    display: "flex",
    justifyContent: "space-between",
    gap: "20px", // Space between columns
    flexWrap: "wrap", // Allow columns to wrap on smaller screens
  },
  column: {
    flex: "1 1 45%", // Allow columns to have equal width, but also wrap in smaller screens
    backgroundColor: "white",
    padding: "20px",
    borderRadius: "8px",
    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
  },
  dropzone: {
    border: "2px dashed #ccc",
    padding: "20px",
    textAlign: "center",
    cursor: "pointer",
    marginBottom: "20px", // Space between the drop zone and file input
    display: "flex", // Ensure that the dropzone is flexible
    justifyContent: "center", // Center the content horizontally
    alignItems: "center", // Center the content vertically
    minHeight: "200px", // Set a minimum height for the drop area
    width: "100%", // Ensure full width for the drop zone
    boxSizing: "border-box", // Include padding and border in width/height calculations
    backgroundColor: "#f5f5f5", // Light background for the drop area
  },
  iconContainer: {
    marginBottom: "10px",
  },
  plusIcon: {
    color: "blue", // Make the icon blue
  },
  chooseFileContainer: {
    marginTop: "20px",
  },
  chooseFileButton: {
    width: "100%", // Make button full width
  },
  fileInput: {
    marginTop: "20px",
    width: "100%",
  },
  fileInfo: {
    marginTop: "10px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "white",
    padding: "20px",
    color: "black",
    borderRadius: "20px",
  },
  deleteButton: {
    color: "red",
    background: "white",
    border: "none",
    padding: "5px 10px",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
  },
  deleteIcon: {
    marginRight: "5px", // Space between the icon and the text
  },
  error: {
    color: "red",
    marginTop: "10px",
  },
  detectButton: {
    marginTop: "20px",
    backgroundColor: "#4CAF50",
    color: "white",
    padding: "10px 20px",
    border: "none",
    cursor: "pointer",
    width: "100%", // Makes the button span the full width of the form
  },
  additionalText: {
    marginTop: "20px",
    color: "#333", // Dark text for additional content
  },
};

export default TwoColumnLayout;
