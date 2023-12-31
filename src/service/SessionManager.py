import time
import uuid

SESSION_TIMEOUT = 3600

class SessionManager:
  def __init__(self):
    self.sessions = {}

  def create_session(self, username, session_id=None):
    if session_id == None:
      session_id = str(uuid.uuid4())
      self.sessions[session_id] = {'username': username, 'timestamp': time.time()}
      return session_id, False
    elif session_id in self.sessions:
      self.sessions[session_id]['timestamp'] = time.time()
      return session_id, True
    elif session_id not in self.sessions:
      return None, False

  def validate_session(self, session_id):
    session_data = self.sessions.get(session_id)
    if session_data:
      if session_data['timestamp'] - time.time() > SESSION_TIMEOUT:
        del self.sessions[session_id]
        return False
      return True
    return False