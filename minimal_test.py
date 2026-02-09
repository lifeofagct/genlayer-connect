# { "Depends": "py-genlayer:test" }
from genlayer import *

class MinimalTest(gl.Contract):
    def __init__(self):
        self.message = "Contract is working!"
        self.counter = 0
    
    @gl.public.view
    def test_simple(self) -> str:
        """Just return a simple string - no AI, no complexity"""
        return "Hello! This contract works!"
    
    @gl.public.view
    def get_message(self) -> str:
        """Return stored message"""
        return self.message
    
    @gl.public.write
    def increment_counter(self) -> int:
        """Increment counter and return it"""
        self.counter += 1
        return self.counter
    
    @gl.public.view
    def get_counter(self) -> int:
        """Get current counter value"""
        return self.counter
