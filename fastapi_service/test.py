import asyncio
import sys
from httpx import AsyncClient, ASGITransport
from main import app
from database import engine, Base

async def run_tests():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        passed = 0
        failed = 0

        try:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
            passed += 1
        except Exception as e:
            failed += 1

        try:
            resp = await client.post(
                "/auth/register",
                json={"email": "test@example.com", "password": "pass123"}
            )
            assert resp.status_code == 201
            assert resp.json() == {"message": "Регистрация успешна"}
            passed += 1
        except Exception as e:
            failed += 1

        try:
            await client.post(
                "/auth/register",
                json={"email": "duplicate@example.com", "password": "pass"}
            )
            resp2 = await client.post(
                "/auth/register",
                json={"email": "duplicate@example.com", "password": "pass"}
            )
            assert resp2.status_code == 400
            assert "уже существует" in resp2.json()["detail"]
            passed += 1
        except Exception as e:
            failed += 1

        try:
            await client.post(
                "/auth/register",
                json={"email": "login@example.com", "password": "loginpass"}
            )
            resp = await client.post(
                "/auth/login",
                json={"email": "login@example.com", "password": "loginpass"}
            )
            assert resp.status_code == 200
            assert "access_token" in resp.json()
            assert "refresh_token" in resp.json()
            passed += 1
        except Exception as e:
            failed += 1

        try:
            await client.post(
                "/auth/register",
                json={"email": "wrong@example.com", "password": "correct123"}
            )
            resp = await client.post(
                "/auth/login",
                json={"email": "wrong@example.com", "password": "wrong123"}
            )
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Неверный email или пароль"
            passed += 1
        except Exception as e:
            failed += 1

        try:
            resp = await client.get("/auth/me")
            assert resp.status_code == 403
            passed += 1
        except Exception as e:
            failed += 1

        try:
            await client.post(
                "/auth/register",
                json={"email": "token@example.com", "password": "tokenpass"}
            )
            login_resp = await client.post(
                "/auth/login",
                json={"email": "token@example.com", "password": "tokenpass"}
            )
            token = login_resp.json()["access_token"]
            
            resp = await client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert resp.status_code == 200
            assert resp.json()["email"] == "token@example.com"
            passed += 1
        except Exception as e:
            failed += 1

        try:
            await client.post(
                "/auth/register",
                json={"email": "refresh@example.com", "password": "refreshpass"}
            )
            login_resp = await client.post(
                "/auth/login",
                json={"email": "refresh@example.com", "password": "refreshpass"}
            )
            refresh_token = login_resp.json()["refresh_token"]
            
            resp = await client.post(
                "/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            assert resp.status_code == 200
            assert "access_token" in resp.json()
            assert "refresh_token" in resp.json()
            passed += 1
        except Exception as e:
            failed += 1

        print("\n" + "=" * 50)
        print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
        print("=" * 50)

        return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
