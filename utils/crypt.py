import bcrypt


async def crypt_pass(password: str):
    """
    Crypt password
    :param password: str
    :return: hash crypt password
    """
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt).decode('utf-8')
    return hashed
