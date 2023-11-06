# Importing the required modules
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from fastapi import FastAPI, HTTPException
import uvicorn
import os
from pydantic import BaseModel

# Initialize Firebase Admin SDK
options = {
    'serviceAccountId': 'example.iam.gserviceaccount.com',
}
cred = credentials.Certificate('/path/service-account-key.json')
firebase_admin.initialize_app(cred, options=options)

db = firestore.client()

# Initialising the fast api app
app = FastAPI(
    title='Fastapi Docs',
    docs_url='/'
)

# Creating the templates for json objects on API endpoints
class RegisterRequest(BaseModel):
    username: str
    email: str
    fullname: str
    password: str
    confirmPassword: str

class LoginRequest(BaseModel):
    userId: str

class UpdateRequest(BaseModel):
    username: str
    fullname: str

class ResetPasswordRequest(BaseModel):
    email: str

# POST /register endpoint for registering new users
@app.post('/register')
async def register_user(request: RegisterRequest):
    try:
        # checking if the passwords match or not
        if request.password != request.confirmPassword:
            return {"error message": "passwords don't match"}
        # Adding new user to the database
        user = auth.create_user(email=request.email, password=request.password)
        doc_ref = db.collection("UserData").document(user.uid)
        

        data = {
            "username" : request.username,
            "email": request.email,
            "fullname": request.fullname,
            "created_at": SERVER_TIMESTAMP,
            "token": ""
        }
        doc_ref.set(data)

        return {"message": "User registered successfully", "user_id": user.uid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# POST /login endpoint for signing into existing user IDs with custom token
@app.post('/login')
async def get_auth_token(request: LoginRequest):
    try:
        # Email exists, attempt to sign in
        custom_token = auth.create_custom_token(request.userId).decode('utf-8')
        user = os.system("node Signin.js " + str(custom_token))
        
        doc_ref = db.collection("UserData").document(request.userId)
        field_updates = {
            "token": custom_token
        }
        doc_ref.update(field_updates)

        return {"message": "Sign-in successful",  "token": custom_token, "user": user}
    except Exception as e:
        # Handle authentication error, e.g., wrong password, user not found
        return {"error message": str(e)}
    
# POST /profile/{userId}/{operation}/{token} endpoint for deleting a user or updating username and full name i th efirestore database
@app.post('/profile/{userId}/{operation}/{token}')
async def update_data(userId, operation, token, request: UpdateRequest):

    # Matching the tokens in the databse and that is given in the endpoint
    doc_ref = db.collection("UserData").document(userId)
    temp_token = doc_ref.get()
    print(temp_token.to_dict()["token"])

    # If tokens don't match then changes can't be made
    if(temp_token.to_dict()["token"] != token):
        return {"error message": "invalid token"}
    
    # Retrieve is used to completely delete a user from both firestoe database and firebase authentication
    if operation == "retrieve":
        auth.delete_user(userId)
        db.collection('UserData').document(userId).delete()
        return {"error message": "user deleted"}
    # Update is to chane username or full name or both
    elif operation == "update":
        try:
            doc_ref = db.collection('UserData').document(userId)
            field_updates = {
                "username": request.username,
                "fullname": request.fullname
            }
            doc_ref.update(field_updates)
            return {"message": userId + " data updated"}
        except:
            return {"error message": "could not get the document from firebase"}
        
# MAIN 
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
