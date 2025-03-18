// App.js
import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import FileUploadPage from "./FileUploadForm";
import TwoColumnLayout from "./TwoColumnLayout";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHome } from "@fortawesome/free-solid-svg-icons";

const App = () => {
  return (
    <Router>
      <div>
        {/* Navigation Links */}
        <nav style={styles.nav}>
          <ul style={{ listStyleType: "none" }}>
            <li>
              <Link to="/" style={styles.navLink}>
                <FontAwesomeIcon
                  icon={faHome}
                  style={{ fontSize: "30px", color: "blue" }}
                />
              </Link>
            </li>
          </ul>
        </nav>

        <Routes>
          <Route exact path="/" element={<FileUploadPage />} />
          <Route path="/two-column-layout" element={<TwoColumnLayout />} />
        </Routes>
      </div>
    </Router>
  );
};

const styles = {
  nav: {
    backgroundColor: "rgb(30, 58, 95)",
    paddingTop: "20px",
    paddingBottom: "5px",
    paddingLeft: "0px",
    marginLeft: "0px",
  },
  navLink: {
    color: "white",
    textDecoration: "none",
    marginRight: "15px",
    margin: "0px",
  },
};

export default App;
