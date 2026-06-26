# RUN APPLICATION - Cyber SuRaksha 2.0

## 1. Prerequisites

### System Requirements
*   **Operating System**: Windows (PowerShell recommended)
*   **Python**: Version 3.10 or higher
*   **Node.js**: Version 18.x or higher
*   **Package Managers**: `pip` (Python) and `npm` (Node.js)

### Project Frameworks
*   **Backend**: Native Python (No web server framework)
*   **Frontend**: React built with Vite
*   **Key Python Dependencies**: `PyMuPDF`, `chromadb`, `pandas`, `networkx`, `sentence-transformers`
*   **Key Node Dependencies**: `cytoscape`, `react-cytoscapejs`, `recharts`

---

## 2. First-Time Setup

You will need **two** terminals for the initial setup.

### Terminal 1: Backend Setup
Open a PowerShell terminal at the project root (`D:\SuRaksha`):

1. **Create a virtual environment**:
   ```powershell
   python -m venv venv
   ```
2. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Terminal 2: Frontend Setup
Open a second PowerShell terminal at the frontend directory (`D:\SuRaksha\frontend\dashboard`):

1. **Install Node modules**:
   ```powershell
   npm install
   ```

---

## 3. Daily Startup Procedure

**No backend server is required.** The entire intelligence engine runs offline and generates static JSON files. The frontend is a static React application that imports these JSONs directly.

To start the demo, you only need **one** terminal.

### Start the UI
1. Open PowerShell and navigate to the frontend directory:
   ```powershell
   cd D:\SuRaksha\frontend\dashboard
   ```
2. Start the Vite development server:
   ```powershell
   npm run dev
   ```
3. **Expected URL**: Open your browser and navigate to `http://localhost:5173`

---

## 4. Backend Regeneration (Optional)

The application already contains the fully processed data for the current 103 RBI PDFs. **Regeneration is entirely unnecessary for daily demos.**

However, if you add new PDFs to the dataset, you must regenerate the backend outputs and manually copy them to the frontend. 

### Step A: Regenerate Data
In your activated Python virtual environment (`D:\SuRaksha`):
```powershell
python taxonomy_builder.py
python cross_reference_parser.py
python reference_graph_v2.py
python map_generator.py
python map_dashboard_feed.py
```

### Step B: Sync Data to Frontend
The backend outputs to `D:\SuRaksha\maps\` and the project root, but the frontend reads from `D:\SuRaksha\frontend\dashboard\src\data\`. You must manually copy the newly generated files over:

```powershell
Copy-Item -Path D:\SuRaksha\maps\*.json -Destination D:\SuRaksha\frontend\dashboard\src\data\ -Force
Copy-Item -Path D:\SuRaksha\data\requirements\requirements_taxonomy.json -Destination D:\SuRaksha\frontend\dashboard\src\data\ -Force
Copy-Item -Path D:\SuRaksha\reference_graph_v2.json -Destination D:\SuRaksha\frontend\dashboard\src\data\ -Force
```
*Note: Vite automatically copies and bundles these JSON files into the build during `npm run dev` or `npm run build`.*

---

## 5. Folder Structure
```text
D:\SuRaksha\
├── venv\                          # Python virtual environment
├── requirements.txt               # Backend dependencies
├── dataset\                       # Raw RBI PDFs
├── maps\                          # Backend JSON output directory
├── data\requirements\             # Taxonomy JSON output
├── frontend\
│   └── dashboard\
│       ├── package.json           # Frontend dependencies
│       └── src\
│           ├── data\              # Frontend JSON data directory
│           └── pages\             # React UI components
```

---

## 6. Common Errors & Troubleshooting

*   **Error**: `Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
    *   **Fix**: Run PowerShell as Administrator and execute: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`, then try activating the venv again.
*   **Error**: `ModuleNotFoundError: No module named 'chromadb'`
    *   **Fix**: Ensure your Python virtual environment is activated (`.\venv\Scripts\Activate.ps1`) before running backend scripts.
*   **Error**: Frontend shows outdated data after running backend scripts.
    *   **Fix**: You forgot to copy the JSON files. Execute the `Copy-Item` commands in Step 4B to sync the backend output to `frontend\dashboard\src\data\`.
*   **Error**: `npm ERR! code ENOENT` when running `npm install`.
    *   **Fix**: Ensure you are in the correct directory (`D:\SuRaksha\frontend\dashboard`).

---

## 7. Shutdown Procedure
1. In the terminal running `npm run dev`, press `Ctrl + C` and type `Y` to terminate the frontend server.
2. If you are in the Python virtual environment, type `deactivate` to exit it.
3. Close the terminals.
