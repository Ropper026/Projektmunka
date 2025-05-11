## Telepítési és üzembe helyezési útmutató

1. **Környezeti előfeltételek:**  
   - Python 3.8+ 
   - Git

2. **Projekt klónozása:**  
   ```
   git clone https://github.com/Ropper026/Projektmunka
   cd projektmunka
   ```

3. **Python virtuális környezet létrehozása és aktiválása:**  
   ```
   python -m venv venv
   # Windows: (Powershell-ben)
   venv\Scripts\activate.ps1
   Ha ez nem működik, először ezt kell futtatni egy adminisztrátor jogú powershellben:
   Set-ExecutionPolicy RemoteSigned -> A (Yes to All)
   # Linux/Mac:
   source venv/bin/activate
   ```

4. **Backend modulok telepítése:**  
   ```
   pip install fastapi uvicorn
   ```

5. **Backend szerver indítása:**
   ```
   cd backend
   uvicorn main:app --reload
   ```

6. **Alkalmazás megnyitása:**
   - Nyisd meg a böngészőben az index.html fájlt
