from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from db import create_database, create_user_database, get_db_connection, get_user_db_connection
from hashlib import sha256
import sqlite3
import secrets
from fastapi.middleware.cors import CORSMiddleware
import shutil
from fastapi.staticfiles import StaticFiles


create_database()
create_user_database()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="images"), name="images")

class User(BaseModel):
    username: str
    password: str

sessions = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    return sessions[token]

@app.get("/properties/")
def get_properties(query: str = None):
    connection = get_db_connection()
    cursor = connection.cursor()
    query_condition = "WHERE title LIKE ? OR location LIKE ?" if query else ""
    cursor.execute(f"SELECT * FROM properties {query_condition}", (f"%{query}%", f"%{query}%") if query else ())
    properties = cursor.fetchall()
    connection.close()

    return {
        "properties": [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "price": row[3],
                "location": row[4],
                "rooms": row[5],
                "area": row[6],
                "image_path": f"http://127.0.0.1:8000/images/{row[7]}" if row[7] else None,
            }
            for row in properties
        ]
    }

@app.post("/properties/")
async def create_property(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    location: str = Form(...),
    rooms: int = Form(...),
    area: float = Form(...),
    image: UploadFile = File(None),
    current_user: str = Depends(get_current_user)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    image_filename = None
    if image:
        try:
            image_filename = image.filename
            image_path = f"images/{image_filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    try:
        cursor.execute("""
            INSERT INTO properties (title, description, price, location, rooms, area, image_path, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, price, location, rooms, area, image_filename, current_user))
        connection.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Failed to insert property into database")
    finally:
        connection.close()

    return {"message": "Property created successfully!", "image_path": image_filename}

@app.get("/properties/{property_id}")
def get_property(property_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
    property = cursor.fetchone()
    connection.close()
    if property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return {
        "id": property[0],
        "title": property[1],
        "description": property[2],
        "price": property[3],
        "location": property[4],
        "rooms": property[5],
        "area": property[6],
        "image_path": f"http://127.0.0.1:8000/images/{property[7]}" if property[7] else None,
        "username": property[8]
    }

@app.delete("/properties/{property_id}")
def delete_property(property_id: int, current_user: str = Depends(get_current_user)):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM properties WHERE id = ?", (property_id,))
    property_owner = cursor.fetchone()
    if property_owner is None:
        raise HTTPException(status_code=404, detail="Property not found")
    if property_owner[0] != current_user:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this property")
    cursor.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    connection.commit()
    connection.close()
    return {"message": "Property deleted successfully!"}

@app.put("/properties/{property_id}")
async def update_property(
    property_id: int,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    location: str = Form(...),
    rooms: int = Form(...),
    area: float = Form(...),
    image: UploadFile = File(None),
    current_user: str = Depends(get_current_user)
):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT username, image_path FROM properties WHERE id = ?", (property_id,))
    property_owner = cursor.fetchone()
    if property_owner is None:
        raise HTTPException(status_code=404, detail="Property not found")
    if property_owner[0] != current_user:
        raise HTTPException(status_code=403, detail="You are not authorized to edit this property")

    image_filename = property_owner[1]
    if image:
        try:
            image_filename = image.filename
            image_path = f"images/{image_filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    try:
        cursor.execute("""
            UPDATE properties
            SET title = ?, description = ?, price = ?, location = ?, rooms = ?, area = ?, image_path = ?
            WHERE id = ?
        """, (title, description, price, location, rooms, area, image_filename, property_id))
        connection.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Failed to update property")
    finally:
        connection.close()

    return {"message": "Property updated successfully!"}

@app.post("/register/")
def register_user(user: User):
    connection = get_user_db_connection()
    cursor = connection.cursor()
    hashed_password = sha256(user.password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, hashed_password))
        connection.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        connection.close()
    return {"message": "User registered successfully"}

@app.post("/login/")
def login_user(user: User):
    connection = get_user_db_connection()
    cursor = connection.cursor()
    hashed_password = sha256(user.password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user.username, hashed_password))
    db_user = cursor.fetchone()
    connection.close()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    session_token = secrets.token_hex(16)
    sessions[session_token] = user.username
    return {"message": "Login successful", "token": session_token}

@app.get("/profile/")
def get_profile(current_user: str = Depends(get_current_user)):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM properties WHERE username = ?", (current_user,))
    properties = cursor.fetchall()
    connection.close()

    return {
        "username": current_user,
        "properties": [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "price": row[3],
                "location": row[4],
                "rooms": row[5],
                "area": row[6],
                "image_path": f"http://127.0.0.1:8000/images/{row[7]}" if row[7] else None,
            }
            for row in properties
        ]
    }
