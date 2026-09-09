# SatQuery Backend — Important Commands

## 1. Activate Virtual Environment

From the project root:

```powershell
.\myenv\Scripts\Activate.ps1
```

Verify:

```powershell
python --version
where.exe python
```

---

## 2. Move to Backend

```powershell
cd backend
```

---

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

Check installed packages:

```powershell
pip list
```

---

## 4. Start FastAPI Server

```powershell
uvicorn app.main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 5. Run Tests

Run all tests:

```powershell
pytest -v
```

Run a specific test file:

```powershell
pytest tests/test_datasets.py -v
```

Run a specific test:

```powershell
pytest tests/test_datasets.py::test_upload_file -v
```

Stop after the first failure:

```powershell
pytest -x -v
```

Show print/debug output:

```powershell
pytest -v -s
```

---

## 6. MongoDB

Open MongoDB Shell:

```powershell
mongosh
```

Show databases:

```javascript
show dbs
```

Select SatQuery database:

```javascript
use satquery
```

Show collections:

```javascript
show collections
```

View datasets:

```javascript
db.datasets.find().pretty()
```

Count datasets:

```javascript
db.datasets.countDocuments()
```

View GridFS files:

```javascript
db.fs.files.find().pretty()
```

Count GridFS files:

```javascript
db.fs.files.countDocuments()
```

Count GridFS chunks:

```javascript
db.fs.chunks.countDocuments()
```

Exit MongoDB Shell:

```javascript
exit
```

---

## 7. Test API from Browser

Health endpoint:

```text
http://127.0.0.1:8000/api/v1/health
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 8. Git — Check Changes

Check repository status:

```powershell
git status
```

See code changes:

```powershell
git diff
```

See staged changes:

```powershell
git diff --cached
```

---

## 9. Git — Add Changes

Add only backend changes:

```powershell
git add backend/
```

Or add everything:

```powershell
git add .
```

---

## 10. Git — Commit

Example:

```powershell
git commit -m "Implement Phase 1 backend foundation"
```

Other useful examples:

```powershell
git commit -m "Add dataset management API"
```

```powershell
git commit -m "Add GridFS file storage"
```

```powershell
git commit -m "Add raster upload validation"
```

```powershell
git commit -m "Add backend tests"
```

---

## 11. Git — Push

```powershell
git push
```

---

## 12. Git — Pull Latest Changes

```powershell
git pull
```

---

## 13. Git — Branch Information

Show current branch:

```powershell
git branch --show-current
```

Show all branches:

```powershell
git branch
```

Create a branch:

```powershell
git checkout -b feature/backend-task
```

Switch branch:

```powershell
git checkout branch-name
```

---

## 14. Normal Development Workflow

Every time you work on the backend:

```text
Activate environment
        ↓
cd backend
        ↓
Edit code
        ↓
Run tests
        ↓
Check git diff
        ↓
Commit
        ↓
Push
```

Commands:

```powershell
.\myenv\Scripts\Activate.ps1
cd backend
pytest -v
git status
git diff
git add backend/
git commit -m "Your message"
git push
```

---

## 15. Before Giving Work to the Team

Run:

```powershell
pytest -v
```

Expected current result:

```text
16 passed
```

Then:

```powershell
git status
```

Then:

```powershell
git diff
```

Make sure there are no:

* Temporary debug prints
* Accidental files
* Temporary raster files
* Unintended changes
* Secrets or `.env` files

Then commit and push:

```powershell
git add backend/
git commit -m "Complete Phase 1 backend foundation"
git push
```

---

## 16. Most Important Commands

If you only remember the essentials:

```powershell
# Start environment
.\myenv\Scripts\Activate.ps1

# Enter backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Start API
uvicorn app.main:app --reload

# Run tests
pytest -v

# Check changes
git status
git diff

# Commit
git add backend/
git commit -m "Your message"

# Push
git push
