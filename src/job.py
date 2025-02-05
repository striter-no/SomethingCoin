from hashlib import sha256
from random import randint, choice
from string import ascii_letters, digits
import base64

import src.db as db

alph = ascii_letters + digits

def gen_str(length=10) -> str:
    return "".join(choice(alph) for i in range(length))

def hash_coin(i_str: str) -> str:
    return base64.b64encode(
        sha256(i_str.encode()).digest()
    ).decode()

def start_job(diff: int) -> tuple[str, str]:
    token, pref = "", ""

    pref = f"smth{''.join([str(randint(0, 9)) for i in range(4)])}"
    i_str = gen_str(length=20*diff)
    b64_hashed = hash_coin(pref+i_str)
    
    indx = randint(0, len(b64_hashed) - diff*3)
    token = b64_hashed[indx: indx+diff*3]

    return token, pref

def get_job(user_id: str, args: list[str], msg_conf: dict, users_dbase: db.DataBase) -> str:
    """Get job for user with given id from database."""

    if not users_dbase.exists(user_id):
        users_dbase.set(user_id, {
            "balance": 0,
            "mined": 0,
            "job": None,
            "job_diff": 0
        })

        return msg_conf["new"]["job"]
    
    user = users_dbase.get(user_id)

    if args[0] in ['r', 'reset']:
        user["job"] = None
        users_dbase.set(user_id, user)
        return msg_conf["ok"]["job-res"]

    if user["job"] is not None:
        return msg_conf["exists"]["job"] + f" __Токен и префикс задачи:__ **{user["job"][0]} {user["job"][1]}** (diff: {user["job_diff"]})"


    diff = min(3, max(int(args[0]), 1))

    user["job"] = start_job(diff)
    user["job_diff"] = diff
    users_dbase.set(user_id, user)

    return msg_conf["ok"]["job"] + f" __Токен и префикс задачи:__ **{user["job"][0]} {user["job"][1]}** (diff: {user["job_diff"]})"


def mine(user_id: str, args: list[str], msg_conf: dict, users_dbase: db.DataBase) -> str:
    if not users_dbase.exists(user_id):
        return msg_conf["new"]["mine"]
    
    if users_dbase.get(user_id)["job"] is None:
        return msg_conf["exists"]["mine"]
    
    user = users_dbase.get(user_id)
    i_str = args[0]
    b64_hashed = hash_coin(i_str)

    if user["job"][0] in b64_hashed:
        user["balance"] += 1 * user["job_diff"]
        user["mined"] += 1 * user["job_diff"]
        user["job"] = None

        users_dbase.set(user_id, user)
        return msg_conf["ok"]["mine"] + f" __Вы получили {1 * user["job_diff"]} монету.__"
    
    return msg_conf["fail"]["mine"]

def balance(user_id: str, args: list[str], msg_conf: dict, users_dbase: db.DataBase) -> str:
    if not users_dbase.exists(user_id):
        return msg_conf["new"]["balance"]
    
    return f"__Ваш баланс:__ **{users_dbase.get(user_id)["balance"]}**\n__Намайнено__: **{users_dbase.get(user_id)["mined"]}**"

def pay(user_id: str, args: list[str], msg_conf: dict, users_dbase: db.DataBase) -> str:
    if not users_dbase.exists(user_id):
        return msg_conf["new"]["pay"]
    
    user = users_dbase.get(user_id)
    
    coins = int(args[0])
    to_user = args[1]

    if coins > user["balance"]:
        return msg_conf["fail"]["pay-bal"]
    
    if not users_dbase.exists(to_user):
        return msg_conf["fail"]["pay-us"]
    
    user_to = users_dbase.get(to_user)
    user["balance"] -= coins
    user_to["balance"] += coins
    
    return msg_conf["ok"]["pay"] + f" __Вы перевели {coins} монет на аккаунт {to_user}.__"