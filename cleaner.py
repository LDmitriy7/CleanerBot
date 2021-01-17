from telethon.tl.functions.users import GetFullUserRequest, GetUsersRequest
from telethon.tl.types import InputUser
import unicodedata
from datetime import datetime


def add_user_to_base(fp, current_users, user_id, access_hash):
    user = f'{user_id} {access_hash}'
    if user not in current_users:
        print(user, file=fp)
        fp.flush()


def is_inactive(was_online, max_days_ago):
    if isinstance(was_online, datetime):
        was_online = was_online.timestamp()
        time_now = datetime.now().timestamp()
        time_diff = time_now - was_online
        max_time_diff = max_days_ago * 24 * 60 * 60
        if time_diff > max_time_diff:
            return time_diff


def check_AL(text):
    for char in text:
        char_type = unicodedata.bidirectional(char)
        if char_type in ['R', 'AL', 'RLE', 'RLO', 'AN']:
            return True


async def find_bots(app, channel: str):
    with open('ids_db') as fp:
        CURRENT_USERS = fp.read().strip().split('\n')
    fp = open('ids_db', 'a')
    async for user in app.iter_participants(channel):
        print('pp')
        user_id, access_hash = user.id, user.access_hash
        add_user_to_base(fp, CURRENT_USERS, user_id, access_hash)

        input_user = InputUser(user_id, access_hash)
        full_user = await app(GetFullUserRequest(input_user))
        about = full_user.about
        user_string = f'{user.first_name} {user.last_name} ({about})'
        if check_AL(user_string):
            yield user_id, user_string
    fp.close()


async def find_inactive(app, max_days_ago: int):
    with open('ids_db') as fp:
        CURRENT_USERS = fp.read().strip().split('\n')
    USERS = []

    for user in CURRENT_USERS:
        user_id, access_hash = user.split()
        user = InputUser(int(user_id), int(access_hash))
        USERS.append(user)

    users = await app(GetUsersRequest(USERS))
    for user in users:
        try:
            was_online = user.status.to_dict().get('was_online')
            time_diff = is_inactive(was_online, max_days_ago)
            if time_diff:
                user_string = f'{user.first_name} {user.last_name}'
                yield user.id, user_string, time_diff
        except:
            pass
