import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from fastapi import FastAPI, HTTPException
import uvicorn
import os
from pydantic import BaseModel

# Initialize Firebase Admin SDK
options = {
    'serviceAccountId': 'firebase-adminsdk-6bqbs@user-management-system-994a9.iam.gserviceaccount.com',
}
cred = credentials.Certificate('user-management-system-994a9-firebase-adminsdk-6bqbs-36f6846d26.json')
firebase_admin.initialize_app(cred, options=options)

action_code_settings = auth.ActionCodeSettings(
    url='http://0.0.0.0:8000/signin',
    handle_code_in_app=True,
    ios_bundle_id='com.example.ios',
    android_package_name='com.example.android',
    android_install_app=True,
    android_minimum_version='12',
    dynamic_link_domain='coolapp.page.link',
)

db = firestore.client()

app = FastAPI(
    title='Fastapi Docs',
    docs_url='/'
)

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

@app.post('/register')
async def register_user(request: RegisterRequest):
    try:
        print(request)

        if request.password != request.confirmPassword:
            return {"message": "passwords don't match"}
        
        user = auth.create_user(email=request.email, password=request.password)
        print(user)
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
        return {"error": str(e)}
    
@app.post('/profile/{userId}/{operation}/{token}')
async def update_data(userId, operation, token, request: UpdateRequest):
    doc_ref = db.collection("UserData").document(userId)
    temp_token = doc_ref.get()
    print(temp_token.to_dict()["token"])
    if(temp_token.to_dict()["token"] != token):
        return {"message": "invalid token"}
    if operation == "retrieve":
        auth.delete_user(userId)
        db.collection('UserData').document(userId).delete()
        return {"message": "user deleted"}
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
            return {"erroe message": "could not get the document from firebase"}
        
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
