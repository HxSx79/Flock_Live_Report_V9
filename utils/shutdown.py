import os
import signal
from flask import request

class ShutdownManager:
    @staticmethod
    def shutdown_server():
        """Shutdown the server properly"""
        # Get the process ID
        pid = os.getpid()
        
        # Try werkzeug shutdown first
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
            return True
            
        # If werkzeug shutdown fails, try sending SIGTERM
        try:
            os.kill(pid, signal.SIGTERM)
            return True
        except:
            pass
            
        # Last resort: force exit
        try:
            os._exit(0)
            return True
        except:
            return False