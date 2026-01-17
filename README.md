# Eagle Pacific Data Tool 🦅

A standardized trade data processing tool for Eagle Pacific Logistics.

## Setup Instructions

1. **Create Virtual Environment**:
   ```powershell
   python -m venv venv
   ```

2. **Activate Environment**:
   - Windows PowerShell: `.\venv\Scripts\Activate.ps1`
   - Windows CMD: `.\venv\Scripts\activate.bat`

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run Application**:
   ```powershell
   streamlit run app.py
   ```

## Project Structure
- `app.py`: Main Streamlit UI.
- `processor.py`: Core logic for data cleaning, filtering, and calculation.
- `requirements.txt`: Python package dependencies.
- `venv/`: Local virtual environment.
