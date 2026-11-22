# IMPLEMENTATION GUIDE & RUNBOOK

## 1. Prerequisites & Environment

- **Operating System:** Windows 10/11, Linux, or macOS.
- **Python Version:** Python 3.11 or 3.12 (Tested on Python 3.12.10).
- **Core Libraries:**
  - Optimization: `pulp>=2.8.0,<3.0.0`, `highspy>=1.7.0`
  - Computation: `numpy>=1.26.0`, `scipy>=1.13.0`, `pandas>=2.2.0`
  - Visualization: `plotly>=5.20.0`, `matplotlib>=3.8.0`, `streamlit>=1.35.0`
  - Testing: `pytest>=8.0.0`

---

## 2. Setup Instructions (Windows PowerShell)

```powershell
# 1. Navigate to scratch project directory
Set-Location "C:\Users\boric\.gemini\antigravity\scratch\UAV-Fog-Cloud-Optimization"

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Verify installed packages
python -m pip list

# 4. Run test suite
pytest
```

---

## 3. Running the Interactive Dashboard

```powershell
Set-Location "C:\Users\boric\.gemini\antigravity\scratch\UAV-Fog-Cloud-Optimization"
.\venv\Scripts\streamlit.exe run app.py
```

The application will launch on `http://localhost:8501`.

---

## 4. Running Verification Benchmarks via CLI

To verify parameter sweeps directly from the terminal without the UI:

```powershell
.\venv\Scripts\python.exe -c "from simulation.engine import SimulationEngine; engine = SimulationEngine(); df = engine.run_parameter_sweep('uav_scaling', iterations_per_point=3); print(df.head(10))"
```

The resulting CSV will be saved in `data/results/uav_scaling_results.csv`.
