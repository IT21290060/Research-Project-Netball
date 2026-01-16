import React, { useState, useEffect, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faTrash } from "@fortawesome/free-solid-svg-icons";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const FileUploadForm = () => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [selectedExercise, setSelectedExercise] = useState("");
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const exercises = ["In Out", "360 Count", "Squats"];

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError("");
    }
  };

  useEffect(() => {
    if (file) {
      console.log(file);
      setFile(file);
    }
  }, [file]);

  const onDrop = (acceptedFiles) => {
    fileInputRef.current.value = "";
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError("");
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    multiple: false,
    accept: ".jpg, .jpeg, .png, .pdf, .doc, .docx,.mp4",
  });

  const handleDelete = () => {
    setFile(null);
    fileInputRef.current.value = "";
  };

  const handleDetect = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5004/predict",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      console.log(response.data);

      const exercise = response.data.exercise;
      setMessage(`Upload successful: ${JSON.stringify(exercise)}`);
      setSelectedExercise(exercise); // Update the selectedExercise state

      // Now handle further actions based on the exercise
      formData.append("exercise", exercise); // Use the `exercise` variable instead of relying on the state immediately

      if (exercise === "Zig_zag" || exercise === "In_out" ) {
        alert("herre");
        await handleInOutExercise(formData);
      } else if (exercise === "360_rotation") {
        await handle360RotationExercise(formData);
      } else if (exercise === "Squat"||exercise === "Power") {
        await handleSquatExercise(formData);
      }
    } catch (error) {
      setMessage(
        `Upload failed: ${error.response?.data?.error || error.message}`
      );
    }
  };

  const handleInOutExercise = async (formData) => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/inout",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setMessage(
        `Upload successful: ${JSON.stringify(response.data.exercise)}`
      );
      navigate("/two-column-layout", { state: { data: response.data } });
    } catch (error) {
      setMessage(
        `Upload failed: ${error.response?.data?.error || error.message}`
      );
    }
  };

  const handle360RotationExercise = async (formData) => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:5002/process_video",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setMessage(`Upload successful: ${JSON.stringify(response.data)}`);
      navigate("/two-column-layout", { state: { data: response.data } });
    } catch (error) {
      setMessage(
        `Upload failed: ${error.response?.data?.error || error.message}`
      );
    }
  };

  const handleSquatExercise = async (formData) => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:5001/analyze_video",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setMessage(`Upload successful: ${JSON.stringify(response.data)}`);
      navigate("/two-column-layout", { state: { data: response.data } });
    } catch (error) {
      setMessage(
        `Upload failed: ${error.response?.data?.error || error.message}`
      );
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.formContainer}>
        <form onSubmit={(e) => e.preventDefault()}>
          {/* Select Exercise */}

          {/* Drag and Drop Section */}
          <div {...getRootProps()} className="dropzone" style={styles.dropzone}>
            <input {...getInputProps()} />
            <div style={styles.iconContainer}>
              <FontAwesomeIcon
                icon={faPlus}
                size="3x"
                style={styles.plusIcon}
              />
              <p>Drag and Drop</p>
            </div>
          </div>

          {/* Normal file upload input */}
          <div style={styles.chooseFileContainer}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => document.getElementById("fileInput").click()}
              style={styles.chooseFileButton}
            >
              Choose File
            </button>
            <input
              id="fileInput"
              type="file"
              onChange={handleFileChange}
              style={styles.fileInput}
              ref={fileInputRef}
              hidden
            />
          </div>

          {/* Display selected file */}
          {file && (
            <div style={styles.fileInfo}>
              <b>{file.name}</b>
              <button
                type="button"
                onClick={handleDelete}
                style={styles.deleteButton}
              >
                <FontAwesomeIcon icon={faTrash} style={styles.deleteIcon} />
              </button>
            </div>
          )}

          {/* Error message */}
          {error && <p style={styles.error}>{error}</p>}

          {/* Detect button */}
          {message && <p>{message}</p>}
          <button
            type="button"
            onClick={handleDetect}
            style={styles.detectButton}
          >
            Detect
          </button>
        </form>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#1e3a5f",
    color: "white",
  },
  formContainer: {
    padding: "20px",
    borderRadius: "8px",
    backgroundColor: "#1e3a5f",
    width: "100%",
    maxWidth: "500px",
    margin: "20px",
  },
  chooseFileContainer: {
    textAlign: "center",
  },
  dropzone: {
    border: "2px dashed #ccc",
    padding: "20px",
    textAlign: "center",
    cursor: "pointer",
    marginBottom: "20px",
    minHeight: "200px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    flexDirection: "column",
  },
  selectBox: {
    width: "100%",
    padding: "10px",
    marginBottom: "20px",
    borderRadius: "5px",
  },
  fileInfo: {
    marginTop: "10px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "white",
    padding: "10px",
    color: "black",
    borderRadius: "20px",
  },
  deleteButton: {
    color: "red",
    background: "white",
    border: "none",
    padding: "5px 10px",
    cursor: "pointer",
  },
  error: { color: "red", marginTop: "10px" },
  detectButton: {
    marginTop: "20px",
    backgroundColor: "#4CAF50",
    color: "white",
    padding: "10px 20px",
    border: "none",
    cursor: "pointer",
    width: "100%",
  },
};

export default FileUploadForm;
