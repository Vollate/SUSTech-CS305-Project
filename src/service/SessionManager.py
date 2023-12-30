import time
import secrets

SESSION_TIMEOUT = 3600

class SessionManager:
  def __init__(self):
    self.sessions = {}

  def create_session(self, username):
    session_id = secrets.token_urlsafe()
    self.sessions[session_id] = {'username': username, 'timestamp': time.time()}
    return session_id

  def validate_session(self, session_id):
    session_data = self.sessions.get(session_id)
    if session_data:
        if session_data['timestamp'] - time.time() > SESSION_TIMEOUT:
            del self.sessions[session_id]
            return None
        session_data['timestamp'] = time.time()
        return session_data['username']
    return None