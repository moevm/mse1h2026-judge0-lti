from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository


class MockUserRepository(UserRepository):
    def __init__(self):
        self.users = {}
        self.next_id = 1

    def get_by_id(self, user_id: int):
        return self.users.get(user_id)

    def get_by_username(self, username: str):
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def add(self, user):
        user.id = self.next_id
        self.users[self.next_id] = user
        self.next_id += 1

    def get_all(self, filters=None):
        return list(self.users.values())

    def get_solved_count(self, user_id: int):
        return 0

    def clear(self):
        self.users.clear()
        self.next_id = 1


class MockRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self):
        self.tokens = {}
        self.next_id = 1

    def add(self, token):
        token.id = self.next_id
        self.tokens[self.next_id] = token
        self.next_id += 1

    def get_by_hash(self, token_hash: str):
        for token in self.tokens.values():
            if token.token_hash == token_hash:
                return token
        return None

    def delete_all_by_user(self, user_id: int):
        to_delete = [tid for tid, t in self.tokens.items() if t.user_id == user_id]
        for tid in to_delete:
            del self.tokens[tid]

    def revoke(self, token):
        token.revoked = True

    def clear(self):
        self.tokens.clear()
        self.next_id = 1