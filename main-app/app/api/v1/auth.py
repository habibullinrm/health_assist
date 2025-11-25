from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from pathlib import Path

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Role

router = APIRouter()

# Настройка Jinja2 шаблонов
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/auth/login")
async def login_via_yandex(telegram_id: str):
    """
    Redirects user to Yandex OAuth page.
    Passes telegram_id as state to link accounts later.
    """
    if not settings.YANDEX_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yandex Client ID not configured"
        )

    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": settings.YANDEX_REDIRECT_URI,
        "state": telegram_id,  # Pass telegram_id to link account
    }
    
    # Construct URL manually to avoid encoding issues or use httpx to build it if needed, 
    # but simple string formatting is enough here.
    url = "https://oauth.yandex.ru/authorize?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    return RedirectResponse(url)


@router.get("/auth/yandex/callback")
async def yandex_callback(
    request: Request,
    code: str,
    state: str,  # This is the telegram_id we passed
    db: AsyncSession = Depends(get_db)
):
    """
    Handles callback from Yandex.
    Exchanges code for token, gets user info, creates/updates user.
    Returns HTML page with auto-redirect to Telegram bot.
    """
    async with httpx.AsyncClient() as client:
        # 1. Exchange code for token
        token_response = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.YANDEX_CLIENT_ID,
                "client_secret": settings.YANDEX_CLIENT_SECRET,
            },
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve token from Yandex"
            )
            
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # 2. Get user info
        user_info_response = await client.get(
            "https://login.yandex.ru/info",
            headers={"Authorization": f"OAuth {access_token}"},
        )

        if user_info_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user info from Yandex"
            )

        user_info = user_info_response.json()
        
    # 3. Process user in DB
    yandex_id = user_info.get("id")
    email = user_info.get("default_email")
    full_name = user_info.get("real_name") or user_info.get("display_name")
    sex = user_info.get("sex") # "male", "female", null
    birthday = user_info.get("birthday") # "YYYY-MM-DD" or null
    
    # Calculate age if birthday is present (simplified)
    age = None
    if birthday:
        try:
            from datetime import datetime
            birth_date = datetime.strptime(birthday, "%Y-%m-%d")
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except ValueError:
            pass

    # Check if user exists by Yandex ID or Telegram ID (state)
    # We assume 'state' is the telegram_id (external_id in our DB)
    telegram_id = state
    
    # Find user by telegram_id
    query = select(User).where(User.external_id == telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user:
        # Update existing user
        user.yandex_id = yandex_id
        user.email = email
        if full_name:
            user.full_name = full_name
        if sex:
            user.sex = sex
        if age is not None:
            user.age = age

        await db.commit()
        await db.refresh(user)

        # Return HTML template with redirect to Telegram bot
        return templates.TemplateResponse(
            "auth_success.html",
            {
                "request": request,
                "user_name": user.full_name,
                "bot_username": settings.BOT_USERNAME
            }
        )
    else:
        # Create new user?
        # Usually the flow starts from Telegram, so the user might not exist yet if they haven't started the bot?
        # But if they clicked the link in the bot, they must have started the bot.
        # However, we might not have saved them in DB yet if we only save on specific actions.
        # Let's assume we create a new user if not found, or error out.
        # For now, let's create/update.

        # We need a role. Let's assume role_id=1 is "user" or "patient".
        # We should probably check if role exists or handle it safely.
        # For simplicity, let's assume role_id=1 exists.

        new_user = User(
            external_id=telegram_id,
            yandex_id=yandex_id,
            email=email,
            full_name=full_name or "Unknown",
            sex=sex,
            age=age,
            role_id=1, # Default role
            phone=None # Yandex might not give phone
        )
        db.add(new_user)
        try:
            await db.commit()
            await db.refresh(new_user)
        except Exception as e:
            await db.rollback()
            # If error (e.g. role not found), log it
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        # Return HTML template with redirect to Telegram bot
        return templates.TemplateResponse(
            "auth_success.html",
            {
                "request": request,
                "user_name": new_user.full_name,
                "bot_username": settings.BOT_USERNAME
            }
        )


@router.get("/auth/check/{telegram_id}")
async def check_auth(telegram_id: str, db: AsyncSession = Depends(get_db)):
    """
    Checks if user with telegram_id exists and is authorized.
    """
    query = select(User).where(User.external_id == telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user:
        return {"authorized": True, "user": user.full_name, "yandex_id": user.yandex_id}
    else:
        raise HTTPException(status_code=404, detail="User not found")
