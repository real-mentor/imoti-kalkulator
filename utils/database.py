"""
Supabase интеграция — auth и CRUD операции.
Всички функции са thread-safe и връщат (data, error) tuple.
"""
from __future__ import annotations
import os
from typing import Optional, Tuple, Any, Dict, List

_client = None


def _get_supabase_config() -> tuple:
    """
    Чете SUPABASE_URL и SUPABASE_KEY по приоритет:
    1. st.secrets  — Streamlit Cloud (App Settings → Secrets)
    2. os.environ  — GitHub Actions / Docker / системни env vars
    3. .env файл   — локална разработка
    """
    # 1. Streamlit secrets
    try:
        import streamlit as st
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        if url and key:
            return url, key
    except Exception:
        pass

    # 2. Environment variables (вече заредени от shell или CI)
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if url and key:
        return url, key

    # 3. .env файл (локална разработка)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
    except ImportError:
        pass

    return url, key


def get_client():
    """Singleton Supabase клиент."""
    global _client
    if _client is None:
        from supabase import create_client
        url, key = _get_supabase_config()
        if not url or not key or "тук_ще_сложа" in url:
            raise ValueError(
                "Supabase URL и KEY не са конфигурирани. "
                "Streamlit Cloud: App Settings → Secrets → добави SUPABASE_URL и SUPABASE_KEY. "
                "Локално: добави .env файл."
            )
        _client = create_client(url, key)
    return _client


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────

def register(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Регистрация на нов потребител.
    Връща (user_data, None) при успех или (None, error_message) при грешка.
    """
    try:
        sb = get_client()
        res = sb.auth.sign_up({"email": email, "password": password})
        if res.user:
            return {"id": res.user.id, "email": res.user.email}, None
        return None, "Регистрацията не успя. Опитай отново."
    except Exception as e:
        msg = str(e)
        if "already registered" in msg or "already been registered" in msg:
            return None, "Имейлът вече е регистриран. Влез в акаунта си."
        if "Password should be at least" in msg:
            return None, "Паролата трябва да е поне 6 символа."
        return None, f"Грешка при регистрация: {msg}"


def login(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Вход с имейл и парола.
    Връща (user_data, None) при успех или (None, error_message) при грешка.
    """
    try:
        sb = get_client()
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res.user and res.session:
            return {
                "id": res.user.id,
                "email": res.user.email,
                "access_token": res.session.access_token,
            }, None
        return None, "Неуспешен вход. Провери имейл и парола."
    except Exception as e:
        msg = str(e)
        if "Invalid login credentials" in msg:
            return None, "Грешен имейл или парола."
        if "Email not confirmed" in msg:
            return None, "Имейлът не е потвърден. Провери пощата си."
        return None, f"Грешка при вход: {msg}"


def logout() -> Tuple[bool, Optional[str]]:
    """Изход от акаунта."""
    try:
        get_client().auth.sign_out()
        return True, None
    except Exception as e:
        return False, str(e)


def change_password(new_password: str) -> Tuple[bool, Optional[str]]:
    """Промяна на парола за логнатия потребител."""
    try:
        get_client().auth.update_user({"password": new_password})
        return True, None
    except Exception as e:
        return False, f"Грешка при промяна на парола: {str(e)}"


# ─────────────────────────────────────────────────────────────
# PROFILES
# ─────────────────────────────────────────────────────────────

def save_profile(user_id: str, profile_data: Dict) -> Tuple[bool, Optional[str]]:
    """Запазва или обновява профила на потребителя (upsert)."""
    try:
        sb = get_client()
        sb.table("profiles").upsert({
            "user_id": user_id,
            "data": profile_data,
        }, on_conflict="user_id").execute()
        return True, None
    except Exception as e:
        return False, f"Грешка при запазване на профил: {str(e)}"


def load_profile(user_id: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Зарежда профила на потребителя."""
    try:
        sb = get_client()
        res = sb.table("profiles").select("data").eq("user_id", user_id).execute()
        if res.data:
            return res.data[0]["data"], None
        return None, None  # Профилът не съществува все още
    except Exception as e:
        return None, f"Грешка при зареждане на профил: {str(e)}"


# ─────────────────────────────────────────────────────────────
# SAVED CALCULATIONS
# ─────────────────────────────────────────────────────────────

def save_calculation(
    user_id: str,
    name: str,
    property_data: Dict,
    results: Dict,
    strategy: str = "",
) -> Tuple[Optional[str], Optional[str]]:
    """
    Запазва калкулация. Връща (calc_id, None) при успех.
    """
    try:
        sb = get_client()
        res = sb.table("saved_calculations").insert({
            "user_id": user_id,
            "name": name,
            "property_data": property_data,
            "results": results,
            "strategy": strategy,
            "notes": "",
        }).execute()
        if res.data:
            return res.data[0]["id"], None
        return None, "Калкулацията не беше запазена."
    except Exception as e:
        return None, f"Грешка при запазване: {str(e)}"


def load_calculations(user_id: str) -> Tuple[List[Dict], Optional[str]]:
    """Зарежда всички калкулации на потребителя, сортирани по дата (нови първи)."""
    try:
        sb = get_client()
        res = (
            sb.table("saved_calculations")
            .select("id, name, property_data, results, strategy, notes, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or [], None
    except Exception as e:
        return [], f"Грешка при зареждане: {str(e)}"


def delete_calculation(user_id: str, calc_id: str) -> Tuple[bool, Optional[str]]:
    """Изтрива калкулация (само ако принадлежи на потребителя)."""
    try:
        sb = get_client()
        sb.table("saved_calculations").delete().eq("id", calc_id).eq("user_id", user_id).execute()
        return True, None
    except Exception as e:
        return False, f"Грешка при изтриване: {str(e)}"


def save_note(
    user_id: str, calc_id: str, note_text: str
) -> Tuple[bool, Optional[str]]:
    """Записва/обновява бележка към калкулация."""
    try:
        sb = get_client()
        sb.table("saved_calculations").update({"notes": note_text}).eq(
            "id", calc_id
        ).eq("user_id", user_id).execute()
        return True, None
    except Exception as e:
        return False, f"Грешка при запазване на бележка: {str(e)}"


# ─────────────────────────────────────────────────────────────
# GDPR — ИЗТРИВАНЕ НА АКАУНТ
# ─────────────────────────────────────────────────────────────

def delete_account(user_id: str) -> Tuple[bool, Optional[str]]:
    """
    Изтрива всички данни на потребителя (GDPR).
    Profiles и saved_calculations се изтриват каскадно от PostgreSQL.
    """
    try:
        sb = get_client()
        # Ръчно изтриване (каскадата от auth.users работи автоматично)
        sb.table("saved_calculations").delete().eq("user_id", user_id).execute()
        sb.table("profiles").delete().eq("user_id", user_id).execute()
        # Изход
        sb.auth.sign_out()
        return True, None
    except Exception as e:
        return False, f"Грешка при изтриване на акаунт: {str(e)}"
