from core.auth.utils import get_password_hash, verify_password

# Created with the previous passlib CryptContext(schemes=["bcrypt"]); existing
# users' hashes look like this and must keep verifying.
PASSLIB_SHORT = "$2b$12$s/gCvTCKOqd/mF0buEvb1OvFp4/VvOVWYMyOLBZ8hw6kewjQlO0Lu"
PASSLIB_LONG = "$2b$12$/mzQmsgCFZcLxbOFMpSflOBjvXiErk6rHoHKQt237eMd.wqHBUF9y"
SHORT = "Str0ng!Passw0rd"
LONG = "L0ng!" + "x" * 95


def test_passlib_hashes_still_verify():
    assert verify_password(SHORT, PASSLIB_SHORT)
    assert not verify_password("wrong", PASSLIB_SHORT)
    # passlib used only the first 72 bytes, like bcrypt itself
    assert verify_password(LONG, PASSLIB_LONG)
    assert verify_password(LONG[:72], PASSLIB_LONG)
    assert not verify_password(LONG[:71], PASSLIB_LONG)


def test_new_hashes_round_trip():
    for password in (SHORT, LONG, "ünïcödé-Pässwört1!"):
        hashed = get_password_hash(password)
        assert hashed.startswith("$2b$")
        assert verify_password(password, hashed)
        assert not verify_password(
            password + "x" if len(password) < 72 else "x", hashed
        )


def test_malformed_hash_is_rejected():
    assert not verify_password(SHORT, "not-a-bcrypt-hash")
