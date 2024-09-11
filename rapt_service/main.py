from fastapi import FastAPI, Depends

app = FastAPI()

def check_permissions(permissions: list[str]) -> dict:
    print(permissions)
    return {"permissions": permissions}

@app.get("/protected-resource")
async def protected_resource(user: dict = Depends(check_permissions(["read:resource"]))):
    return {"message": "You have access to this resource", "user": user}

@app.post("/admin-action")
async def admin_action(user: dict = Depends(check_permissions(["admin"]))):
    return {"message": "Admin action performed", "user": user}