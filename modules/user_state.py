"""
User State Manager Module
Manages user states and transitions between different bot modules.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class UserState(Enum):
    """Enumeration of possible user states"""
    ONBOARDING = "onboarding"
    OPTION_SELECTION = "option_selection"
    SETUP = "setup"
    PAYMENT = "payment"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class UserStateManager:
    def __init__(self):
        self.state_transitions = {
            UserState.ONBOARDING: [UserState.OPTION_SELECTION],
            UserState.OPTION_SELECTION: [UserState.SETUP],
            UserState.SETUP: [UserState.PAYMENT],
            UserState.PAYMENT: [UserState.ACTIVE, UserState.CANCELLED],
            UserState.ACTIVE: [UserState.EXPIRED, UserState.CANCELLED],
            UserState.EXPIRED: [UserState.OPTION_SELECTION],
            UserState.CANCELLED: [UserState.OPTION_SELECTION]
        }
    
    async def get_user_state(self, user_id: int) -> Optional[str]:
        """Get user's current state from database"""
        # This will be called by the database manager
        # The actual implementation is in the database module
        pass
    
    async def set_user_state(self, user_id: int, state: UserState, state_data: Dict[str, Any] = None):
        """Set user's current state"""
        # This will be called by the database manager
        # The actual implementation is in the database module
        pass
    
    def can_transition_to(self, current_state: UserState, target_state: UserState) -> bool:
        """Check if transition from current state to target state is allowed"""
        allowed_transitions = self.state_transitions.get(current_state, [])
        return target_state in allowed_transitions
    
    def get_allowed_transitions(self, current_state: UserState) -> list:
        """Get list of allowed transitions from current state"""
        return self.state_transitions.get(current_state, [])
    
    def validate_state_data(self, state: UserState, data: Dict[str, Any]) -> bool:
        """Validate state data based on current state"""
        if state == UserState.ONBOARDING:
            return True  # No specific requirements
        
        elif state == UserState.OPTION_SELECTION:
            return True  # No specific requirements
        
        elif state == UserState.SETUP:
            # Should have collected some key texts
            return 'key_texts' in data and len(data.get('key_texts', [])) > 0
        
        elif state == UserState.PAYMENT:
            # Should have selected subscription type
            return 'subscription_type' in data
        
        elif state == UserState.ACTIVE:
            # Should have active subscription and completed setup
            return 'subscription_id' in data and 'setup_completed' in data
        
        elif state == UserState.EXPIRED:
            return True  # No specific requirements
        
        elif state == UserState.CANCELLED:
            return True  # No specific requirements
        
        return False
