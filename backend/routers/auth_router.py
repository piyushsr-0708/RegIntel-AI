"""
Authentication router - Login and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..crud import get_user_by_username, update_last_login, create_audit_log
from ..schemas import Token, UserLogin
from ..auth import get_current_user
from .. import models

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint - Returns JWT token
    
    Args:
        form_data: OAuth2 form with username and password
        db: Database session
    
    Returns:
        JWT access token
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = get_user_by_username(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Update last login
    update_last_login(db, user.id)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=user.id,
        action="login",
        details=f"User {user.username} logged in"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserLogin)
def get_current_user_info(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information
    
    Returns:
        User details including department info
    """
    department_name = None
    if current_user.department_id:
        department = db.query(models.Department).filter(
            models.Department.id == current_user.department_id
        ).first()
        if department:
            department_name = department.name
    
    return UserLogin(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        department_id=current_user.department_id,
        department_name=department_name
    )
