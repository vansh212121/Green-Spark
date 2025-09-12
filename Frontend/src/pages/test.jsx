import React from "react";
import { useSelector } from "react-redux";
import { useGetApplianceByIdQuery } from "@/features/api/applianceApi";
import { selectAccessToken } from "@/features/authSlice";

const Test = () => {
  // --- CRITICAL STEP ---
  // Please replace this placeholder with a REAL appliance_id (UUID) from your database.
  const applianceIdToTest = "92fa40a5-dd18-4763-9142-e1cbce1f1333";

  const accessToken = useSelector(selectAccessToken);

  // Use the `skip` option to wait for the accessToken to be available.
  const { data, error, isLoading, isError } = useGetApplianceByIdQuery(
    applianceIdToTest,
    {
      skip: !accessToken || applianceIdToTest.startsWith("REPLACE"),
    }
  );

  return (
    <div
      style={{ padding: "2rem", fontFamily: "monospace", lineHeight: "1.6" }}
    >
      <h1
        style={{
          fontSize: "2rem",
          borderBottom: "2px solid #ccc",
          paddingBottom: "0.5rem",
        }}
      >
        Testing: Get Appliance By ID
      </h1>
      <p>
        Attempting to fetch appliance with ID:{" "}
        <strong>{applianceIdToTest}</strong>
      </p>
      <p>
        Current Access Token Status:{" "}
        <strong>{accessToken ? "Available" : "Not Available"}</strong>
      </p>

      <hr style={{ margin: "1rem 0" }} />

      {/* 1. Loading State */}
      {isLoading && (
        <div style={{ color: "blue" }}>
          <h2>Status: Loading...</h2>
          <p>Making API request to /api/v1/appliances/{applianceIdToTest}</p>
        </div>
      )}

      {/* 2. Error State */}
      {isError && (
        <div style={{ color: "red", border: "2px solid red", padding: "1rem" }}>
          <h2>Status: Error Occurred!</h2>
          <p>
            The API request failed. See the details below and in your browser's
            Network tab.
          </p>
          <pre
            style={{
              backgroundColor: "#fbe9e7",
              padding: "1rem",
              whiteSpace: "pre-wrap",
              wordBreak: "break-all",
            }}
          >
            {JSON.stringify(error, null, 2)}
          </pre>
        </div>
      )}

      {/* 3. Success State */}
      {data && (
        <div
          style={{ color: "green", border: "2px solid green", padding: "1rem" }}
        >
          <h2>Status: Success!</h2>
          <p>Successfully received data from the backend.</p>
          <pre
            style={{
              backgroundColor: "#e8f5e9",
              padding: "1rem",
              whiteSpace: "pre-wrap",
              wordBreak: "break-all",
            }}
          >
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default Test;
