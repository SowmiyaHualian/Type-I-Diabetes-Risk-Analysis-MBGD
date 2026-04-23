"""Enhanced prediction module with validation and database integration."""

from typing import Dict, Tuple, Any
from pathlib import Path

from validation import validate_input, ValidationError
from database import get_db
from predict import predict_risk as base_predict_risk


def predict_with_validation(
    payload: Dict[str, Any],
    user_id: int = None,
    username: str = None
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Enhanced prediction with input validation and database storage.
    
    Args:
        payload: User input dictionary
        user_id: Optional user ID
        username: Optional username for storing user
        
    Returns:
        Tuple of (success, result_dict, error_message)
    """
    
    # Step 1: Validate input
    is_valid, validated_data, error_msg = validate_input(payload)
    
    if not is_valid:
        return False, {}, error_msg
    
    # Step 2: Make prediction
    try:
        prediction = base_predict_risk(payload)
    except Exception as e:
        return False, {}, f"Prediction failed: {str(e)}"
    
    # Step 3: Store in database (if enabled)
    try:
        db = get_db()
        
        # Get or create user
        if username:
            user_id = db.store_user(username, email=payload.get('email'))
        elif not user_id:
            user_id = db.store_user(f"anonymous_{Path(__file__).stat().st_mtime}")
        
        # Store input data
        input_id = db.store_input_data(user_id, validated_data)
        
        # Store prediction
        db.store_prediction(user_id, input_id, prediction)
        
        prediction['database_id'] = input_id
    except Exception as e:
        # Don't fail prediction if database fails
        print(f"Warning: Database storage failed: {e}")
        prediction['database_id'] = None
    
    # Step 4: Add validation metadata
    prediction['validation_metadata'] = {
        'input_validated': True,
        'validated_fields': list(validated_data.keys()),
    }
    
    return True, prediction, ""


def get_user_history(user_id: int) -> Dict[str, Any]:
    """Get prediction history for a user."""
    try:
        db = get_db()
        predictions = db.get_user_predictions(user_id)
        return {
            'success': True,
            'predictions': predictions,
            'total': len(predictions),
        }
    except Exception as e:
        return {
            'success': False,
            'predictions': [],
            'total': 0,
            'error': str(e),
        }


def get_system_statistics() -> Dict[str, Any]:
    """Get system-wide statistics."""
    try:
        db = get_db()
        stats = db.get_statistics()
        return {
            'success': True,
            'statistics': stats,
        }
    except Exception as e:
        return {
            'success': False,
            'statistics': {},
            'error': str(e),
        }


def export_predictions(filename: str = None) -> Dict[str, Any]:
    """Export all predictions to CSV."""
    try:
        db = get_db()
        if filename is None:
            from datetime import datetime
            filename = f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        path = db.export_to_csv(filename)
        return {
            'success': True,
            'file_path': path,
            'filename': filename,
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }
