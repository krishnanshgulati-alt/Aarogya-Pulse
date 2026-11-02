# Aarogya Pulse — Anemia Awareness Glove (student prototype)

This starter project contains:
- A responsive HTML/CSS/JavaScript dashboard.
- A Python FastAPI backend.
- A local SQLite database for sensor readings.
- A placeholder ML integration point for your teammate's model.
- An optional ESP32 Wi-Fi POST example using simulated values.

## Important safety and scientific limitation

This project does not diagnose anemia or detect blood loss. The MAX30102 estimates pulse and SpO2; those measurements do not establish hemoglobin concentration. The DS18B20 measures contact temperature and the MPU6050 measures movement. The ML integration is a placeholder until your teammate provides a model and the team validates its intended use.

Do not present simulated readings or a placeholder response as real health measurements or a diagnosis. For health concerns, users should seek appropriate professional assessment.

## Step 1 — Install software

Install:
1. Python 3.10 or newer (during installation on Windows, tick "Add Python to PATH").
2. Visual Studio Code.
3. Optional: Arduino IDE, only if testing the ESP32 sketch.

## Step 2 — Open this folder in VS Code

Extract the ZIP, then in VS Code choose File → Open Folder and select `anemia-awareness-glove`.

The folder should contain `backend`, `frontend`, `esp32`, and this README.

## Step 3 — Open a terminal in VS Code

Choose Terminal → New Terminal.

### Windows PowerShell

Run these commands one by one:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt in VS Code instead and run:

```bat
cd backend
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `py` is not recognized, try `python` instead.

## Step 4 — Start the backend and website

Make sure the terminal is in the `backend` folder and the virtual environment is activated. Run:

```bash
python -m uvicorn main:app --reload
```

You should see a local URL such as `http://127.0.0.1:8000`.

Open that address in your browser. The website and API are served by the same server.

Useful URLs:
- Dashboard: http://127.0.0.1:8000/
- Interactive API docs: http://127.0.0.1:8000/docs
- Backend status: http://127.0.0.1:8000/api/health

Keep the terminal open while testing the website. To stop the server, press Ctrl+C.

## Step 5 — Test it

1. Open the dashboard.
2. Click **Generate demo reading**.
3. Watch the sensor cards and history table update.
4. Click **Check model status**. It should explain that the ML model is not connected.
5. Click **Refresh** to reload saved readings.
6. Click **Clear demo data** if you want to reset the local demo database.

Demo readings are randomly generated fake values and are labelled as demo data.

## Step 6 — Send a test reading through the API

Open http://127.0.0.1:8000/docs.
1. Expand `POST /api/readings`.
2. Click "Try it out".
3. Use this example request body:

```json
{
  "heart_rate": 82,
  "spo2": 98,
  "skin_temperature": 32.4,
  "pulse_feature": 0.51,
  "motion_detected": false,
  "source": "manual-test"
}
```

4. Click Execute.
5. Return to the dashboard and click Refresh.

These values are test examples, not medical readings.

## Step 7 — Connect the real ML model later

Your teammate and you must agree on:
- Input feature names, units, order and missing-value rules.
- Exact preprocessing from training.
- The model file format or separate inference API.
- Output fields and how to interpret them.
- Dataset quality, validation metrics, limitations and intended use.

Then edit `backend/ml_service.py`. Replace `get_demo_assessment()` with a call to the actual model and return a documented response. Do not assume a field like `risk_score` is a clinical probability unless the model is calibrated and validated for that interpretation.

## Step 8 — Optional ESP32 Wi-Fi test

The sketch in `esp32/glove.ino` sends a demonstration JSON payload to the backend. It does not yet read real sensors.

1. In Arduino IDE, select your ESP32 board.
2. Replace the Wi-Fi name and password.
3. Find your computer's local network IP address:
   - Windows: run `ipconfig` and look for the IPv4 Address on the active Wi-Fi adapter.
4. Replace `192.168.1.100` in the sketch with that IP address.
5. Start FastAPI so it listens on the local network:

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. Ensure the ESP32 and computer are on the same Wi-Fi network. Allow Python through your private-network firewall if asked.
7. Upload the sketch and open Serial Monitor at 115200 baud.
8. The dashboard should show entries with source `esp32-demo`.

If it fails, check the computer IP, Wi-Fi network, firewall, and backend terminal.

## Folder guide

- `frontend/index.html`: page content.
- `frontend/style.css`: colours, spacing and responsive layout.
- `frontend/app.js`: API requests and page updates.
- `backend/main.py`: FastAPI routes, input validation and SQLite storage.
- `backend/ml_service.py`: placeholder for teammate's ML model.
- `esp32/glove.ino`: optional networking demo only.

## Before deployment

This is a local hackathon starter, not a production medical system. Before deploying, remove or protect the delete endpoint, restrict CORS, add authentication and authorization where needed, use HTTPS, define retention/deletion rules, minimize sensitive data, and obtain appropriate consent—especially for minors.
