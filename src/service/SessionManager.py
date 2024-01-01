import time
import uuid


class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.SESSION_TIMEOUT = 3600

    def create_session(self, username, cookie_data=None):
        if cookie_data is None:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {'username': username, 'timestamp': time.time()}
            return session_id, False
        session_id = cookie_data.split('=')[1]
        if session_id is None or cookie_data.split('=')[0] != 'session_id':
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {'username': username, 'timestamp': time.time()}
            return session_id, False
        if session_id in self.sessions:
            self.sessions[session_id]['timestamp'] = time.time()
            return session_id, True
        else:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {'username': username, 'timestamp': time.time()}
            return session_id, False

    def validate_session(self, cookie_data):
        session_id = cookie_data.split('=')[1]
        if session_id is None or cookie_data.split('=')[0] != 'session-id':
            return False
        session_data = self.sessions.get(session_id)
        if session_data:
            if session_data['timestamp'] - time.time() > self.SESSION_TIMEOUT:
                del self.sessions[session_id]
                return False
            return True
        return False
