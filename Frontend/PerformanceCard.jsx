import React, { useEffect } from "react";

// ✅ Import images dynamically or via object mapping
const exerciseImages = {
  "InOut Ladder Drill": {
    high: [require("./posesui/InOutUI/high/inout1.png")],
    medium: [require("./posesui/InOutUI/medium/inout2.png"), require("./posesui/InOutUI/medium/inout3.png")],
    low: [require("./posesui/InOutUI/low/inout1.png"), require("./posesui/InOutUI/low/inout2.png"), require("./posesui/InOutUI/low/inout3.png")],
    faults: [require("./posesui/InOutUI/faults/inoutdont1.png")]
  },
  "Squats": {
    high: [require("./posesui/squatUI/high/squat1.png")],
    medium: [require("./posesui/squatUI/medium/squat1.png"), require("./posesui/squatUI/medium/squat2.png")],
    low: [require("./posesui/squatUI/low/squat1.png"), require("./posesui/squatUI/low/squat2.png"), require("./posesui/squatUI/low/squat3.png")],
    faults: [
      require("./posesui/squatUI/faults/squatdont1.png"),
      require("./posesui/squatUI/faults/squatdont2.png")
    ]
  },
  "360 Degree Rotation": {
    high: [require("./posesui/360DegreeUI/high/360do1.png")],
    medium: [require("./posesui/360DegreeUI/medium/360do1.png"), require("./posesui/360DegreeUI/medium/360do2.png")],
    low: [require("./posesui/360DegreeUI/low/360do1.png"), require("./posesui/360DegreeUI/low/360do2.png"), require("./posesui/360DegreeUI/low/360do3.png")],
    faults: [
      require("./posesui/360DegreeUI/faults/360dont1.png"),
      require("./posesui/360DegreeUI/faults/360dont2.png")
    ]
  }
};

export default function PerformanceCard({ data }) {
  useEffect(() => {
    // Check and log the values of exercise and strength to debug
    if (data) {
      console.log("Exercise:", data.exercise); // Log the exercise
      console.log("Strength:", data.strength); // Log the strength
    }
  }, [data]);

  const { exercise, strength, count, duration } = data;

  // Function to render images based on strength level
  const renderImprovements = () => {
    if (!exerciseImages[exercise]) {
      console.log("No images found for exercise:", exercise); // Log if no images are found for exercise
      return [];
    }
    const strengthLevel = strength?.toLowerCase();
    if (!strengthLevel) {
      console.log("Strength level is missing or invalid:", strength); // Log if strength is missing or invalid
      return [];
    }

    const images = exerciseImages[exercise][strengthLevel] || [];
    console.log("Images for improvements:", images); // Log images found for this combination
    return images;
  };

  const renderFaults = () => {
    if (!exerciseImages[exercise]) {
      console.log("No images found for exercise:", exercise); // Log if no images are found for exercise
      return [];
    }

    const faultImages = exerciseImages[exercise].faults || [];
    console.log("Images for faults:", faultImages); // Log fault images
    return faultImages;
  };

  return (
    <div className="container mt-4">
      <div className="card bg-light shadow-sm p-3">
        <div className="card-body">
          <p className="fw-bold">
            Skill Type <span className="float-end">{exercise}</span>
          </p>
          <p className="fw-bold">
            Count <span className="float-end">{count || "N/A"} Times</span>
          </p>
          <p className="fw-bold">
            Strength <span className="float-end">{strength || "N/A"}</span>
          </p>
          <p className="fw-bold">
            Duration <span className="float-end">{duration || "N/A"}</span>
          </p>
        </div>
      </div>

      {/* Improvements Section */}
      <div className="mt-3 text-center fw-bold text-white bg-success p-2 rounded">
        Improvements
      </div>
      <div className="card bg-light p-3 mt-1 text-center">
        {renderImprovements().map((img, idx) => (
          <img key={idx} src={img} alt="Improvement" style={{ width: "100%", marginBottom: "8px" }} />
        ))}
      </div>

      {/* Faults Section */}
      <div className="mt-3 text-center fw-bold text-white bg-danger p-2 rounded">
        Faults
      </div>
      <div className="card bg-light p-3 mt-1 text-center">
        {renderFaults().map((img, idx) => (
          <img key={idx} src={img} alt="Fault" style={{ width: "100%", marginBottom: "8px" }} />
        ))}
      </div>
    </div>
  );
}
