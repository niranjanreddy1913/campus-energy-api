# Reference only (Interns/mongodb). Credentials removed: set MONGO_URI in your environment / .env.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

#docker build -t fastapi-mongodb-app .


#docker run -d -p 8000:8000 --name fastapi-mongodb-app fastapi-mongodb-app

#https://www.youtube.com/watch?v=rIrNIzy6U_g

#https://www.youtube.com/watch?v=zJ6WbK9zFpI&list=PL2We04F3Y_42mOz2jsBqB_TOGIgaB8KkL&index=1


# Initialize FastAPI
app = FastAPI()

# MongoDB connection details
MONGO_DETAILS = os.environ.get("MONGO_URI", "mongodb://localhost:27017")   # never hard-code credentials
client = MongoClient(MONGO_DETAILS)
db = client.genai
collection = db.projects

# Pydantic models for request and response
class Project(BaseModel):
    projectName: str
    projectDescription: str

class ProjectInDB(Project):
    id: str

# Helper function to convert MongoDB document to ProjectInDB
def project_helper(project) -> ProjectInDB:
    return ProjectInDB(
        id=str(project["_id"]),
        projectName=project["projectName"],
        projectDescription=project["projectDescription"],
    )

# Create a new project
@app.post("/projects/", response_model=ProjectInDB)
async def create_project(project: Project):
    project_dict = project.dict()


    result = collection.insert_one(project_dict)
    created_project = collection.find_one({"_id": result.inserted_id})
    return project_helper(created_project)

# Get a project by ID
@app.get("/projects/{project_id}", response_model=ProjectInDB)
async def read_project(project_id: str):
    project = collection.find_one({"_id": ObjectId(project_id)})
    if project:
        return project_helper(project)
    raise HTTPException(status_code=404, detail="Project not found")

# Get all projects
@app.get("/projects/", response_model=List[ProjectInDB])
async def read_projects():
    projects = []

    for project in collection.find():
        projects.append(project_helper(project))
    return projects

# Update a project by ID
@app.put("/projects/{project_id}", response_model=ProjectInDB)
async def update_project(project_id: str, project: Project):
    updated_project = collection.find_one_and_update(
        {"_id": ObjectId(project_id)},
        {"$set": project.dict()},
        return_document=True
    )
    if updated_project:
        return project_helper(updated_project)
    raise HTTPException(status_code=404, detail="Project not found")

# Delete a project by ID
@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = collection.delete_one({"_id": ObjectId(project_id)})
    if result.deleted_count == 1:
        return {"message": "Project deleted"}
    raise HTTPException(status_code=404, detail="Project not found")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
