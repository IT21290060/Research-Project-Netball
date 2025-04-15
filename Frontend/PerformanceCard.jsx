import React, { useEffect } from "react";
import inout1 from "./posesui/InOutUI/inout1.png";
import inout2 from "./posesui/InOutUI/inout2.png";
import inout3 from "./posesui/InOutUI/inout3.png";
import squat1 from "./posesui/squatUI/sqaut1.png";
import squat2 from "./posesui/squatUI/sqaut2.png";
import squat3 from "./posesui/squatUI/sqaut3.png";
import one360 from "./posesui/360DegreeUI/360do1.png";
import two360 from "./posesui/360DegreeUI/360do2.png";
import three360 from "./posesui/360DegreeUI/360do2-1.png";

import inout1dont from "./posesui/InOutUI/inoutdont1.png";
import squat1dont from "./posesui/squatUI/sqautdont1.png";
import squat2dont from "./posesui/squatUI/sqautdont2.png";
import one360dont from "./posesui/360DegreeUI/360dont1.png";
import two360dont from "./posesui/360DegreeUI/360dont2.png";

export default function PerformanceCard(data) {
  useEffect(() => {
    console.log(data);
    alert(data.data.exercise);
  });
  return (
    <div className="container mt-4">
      <div className="card bg-light shadow-sm p-3">
        <div className="card-body">
          <p className="fw-bold">
            Skill Type <span className="float-end">{data.data.exercise}</span>
          </p>
          <p className="fw-bold">
            Count{" "}
            <span className="float-end">{data.data.count || "N/A"} Times</span>
          </p>
          <p className="fw-bold">
            Strength{" "}
            <span className="float-end">{data.data.strength || "N/A"} </span>
          </p>
          <p className="fw-bold">
            Duration{" "}
            <span className="float-end">{data.data.duration || "N/A"} </span>
          </p>
        </div>
      </div>

      <div className="mt-3 text-center fw-bold text-white bg-success p-2 rounded">
        Improvements
      </div>
      <div className="card bg-light p-3 mt-1 text-center">
        {(data.data.exercise === "Coordination" ||data.data.exercise === "InOut Ladder Drill") && (
          <>
            <img src={inout1} style={{ width: "100%" }} /> <br />
            <img src={inout2} style={{ width: "100%" }} /> <br />
            <img src={inout3} style={{ width: "100%" }} />
          </>
        )}

        {(data.data.exercise === "Squats"||data.data.exercise === "Power")  && (
          <>
            {" "}
            <img src={squat1} style={{ width: "100%" }} /> <br />
            <img src={squat2} style={{ width: "100%" }} /> <br />
            <img src={squat3} style={{ width: "100%" }} />
          </>
        )}

        {(data.data.exercise === "360 Degree Rotation" ||data.data.exercise === "Balance") && (
          <>
            <img src={one360} style={{ width: "100%" }} /> <br />
            <img src={two360} style={{ width: "100%" }} /> <br />
            <img src={three360} style={{ width: "100%" }} />
          </>
        )}
      </div>

      <div className="mt-3 text-center fw-bold text-white bg-danger p-2 rounded">
        Faults
      </div>
      <div className="card bg-light p-3 mt-1 text-center">
        {(data.data.exercise === "Coordination" ||data.data.exercise === "InOut Ladder Drill") && (
          <>
            <img src={inout1dont} style={{ width: "100%" }} />
          </>
        )}

        {(data.data.exercise === "Squats" ||data.data.exercise === "Power")  && (
          <>
            <img src={squat1dont} style={{ width: "100%" }} /> <br />
            <img src={squat2dont} style={{ width: "100%" }} />
          </>
        )}

        {(data.data.exercise === "360 Degree Rotation" ||data.data.exercise === "Balance") && (
          <>
            <img src={one360dont} style={{ width: "100%" }} /> <br />
            <img src={two360dont} style={{ width: "100%" }} /> <br />
          </>
        )}
      </div>
    </div>
  );
}



