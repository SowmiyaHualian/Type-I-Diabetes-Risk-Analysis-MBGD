"""Input validation module for Type 1 Diabetes Prediction System."""

from typing import Dict, Tuple, Any
import re


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """Validates all user input fields with range checking and cross-field validation."""
    
    # Define valid ranges for each field
    RANGES = {
        "age": (1, 120),
        "bmi": (10, 60),
        "glucose_level": (50, 400),  # Covers both fasting and random
        "hba1c": (3.0, 14.0),
        "c_peptide": (0.0, 10.0),
        "weight_kg": (20, 200),
        "height_cm": (100, 250),
    }
    
    # Fields that must have values
    REQUIRED_FIELDS = {
        "age": "Age",
        "gender": "Gender",
        "bmi": "BMI or Weight/Height",
        "glucose_level": "Glucose Level (Fasting or Random)",
        "hba1c": "HbA1c",
        "family_history": "Family History",
        "ketone_presence": "Ketone Presence",
    }
    
    @staticmethod
    def validate_age(age: Any) -> int:
        """Validate age is within realistic range."""
        try:
            age_val = int(float(str(age).strip()))
            min_age, max_age = InputValidator.RANGES["age"]
            if not (min_age <= age_val <= max_age):
                raise ValidationError(f"Age must be between {min_age} and {max_age} years")
            return age_val
        except (ValueError, TypeError):
            raise ValidationError("Age must be a valid number")
    
    @staticmethod
    def validate_gender(gender: Any) -> str:
        """Validate gender is one of allowed values."""
        valid_genders = ["Male", "Female", "Other", "M", "F"]
        gender_str = str(gender).strip().title()
        if not any(g.lower() == gender_str.lower() for g in valid_genders):
            raise ValidationError(f"Gender must be one of: {', '.join(valid_genders)}")
        return gender_str
    
    @staticmethod
    def validate_bmi(bmi: Any) -> float:
        """Validate BMI is within realistic range."""
        try:
            bmi_val = float(str(bmi).strip())
            min_bmi, max_bmi = InputValidator.RANGES["bmi"]
            if not (min_bmi <= bmi_val <= max_bmi):
                raise ValidationError(f"BMI must be between {min_bmi} and {max_bmi}")
            return bmi_val
        except (ValueError, TypeError):
            raise ValidationError("BMI must be a valid number")
    
    @staticmethod
    def validate_weight_height(weight_kg: Any, height_cm: Any) -> Tuple[float, float]:
        """Validate and calculate BMI from weight and height."""
        try:
            weight = float(str(weight_kg).strip())
            height = float(str(height_cm).strip())
            
            min_w, max_w = InputValidator.RANGES["weight_kg"]
            min_h, max_h = InputValidator.RANGES["height_cm"]
            
            if not (min_w <= weight <= max_w):
                raise ValidationError(f"Weight must be between {min_w} and {max_w} kg")
            if not (min_h <= height <= max_h):
                raise ValidationError(f"Height must be between {min_h} and {max_h} cm")
            
            # Calculate BMI
            height_m = height / 100
            bmi = weight / (height_m * height_m)
            return weight, height
        except (ValueError, TypeError):
            raise ValidationError("Weight and height must be valid numbers")
    
    @staticmethod
    def validate_glucose(glucose: Any, test_type: str = "random") -> float:
        """Validate glucose level based on test type."""
        try:
            glucose_val = float(str(glucose).strip())
            min_glucose, max_glucose = InputValidator.RANGES["glucose_level"]
            
            if not (min_glucose <= glucose_val <= max_glucose):
                raise ValidationError(f"Glucose level must be between {min_glucose} and {max_glucose} mg/dL")
            
            # Sanity check based on test type
            if test_type == "fasting" and glucose_val < 70:
                raise ValidationError("Fasting glucose is typically above 70 mg/dL. Please verify.")
            
            return glucose_val
        except (ValueError, TypeError):
            raise ValidationError("Glucose level must be a valid number")
    
    @staticmethod
    def validate_hba1c(hba1c: Any) -> float:
        """Validate HbA1c percentage."""
        try:
            hba1c_val = float(str(hba1c).strip())
            min_hba1c, max_hba1c = InputValidator.RANGES["hba1c"]
            
            if not (min_hba1c <= hba1c_val <= max_hba1c):
                raise ValidationError(f"HbA1c must be between {min_hba1c} and {max_hba1c}%")
            
            return hba1c_val
        except (ValueError, TypeError):
            raise ValidationError("HbA1c must be a valid number")
    
    @staticmethod
    def validate_c_peptide(c_peptide: Any) -> float:
        """Validate C-Peptide level."""
        try:
            if c_peptide is None or str(c_peptide).strip() == "":
                return 0.0  # Optional field, default to 0
            
            c_pep_val = float(str(c_peptide).strip())
            min_cp, max_cp = InputValidator.RANGES["c_peptide"]
            
            if not (min_cp <= c_pep_val <= max_cp):
                raise ValidationError(f"C-Peptide must be between {min_cp} and {max_cp}")
            
            return c_pep_val
        except (ValueError, TypeError):
            raise ValidationError("C-Peptide must be a valid number")
    
    @staticmethod
    def validate_boolean_field(value: Any, field_name: str) -> bool:
        """Validate boolean fields (Yes/No, Present/Absent)."""
        str_val = str(value).strip().lower()
        
        if str_val in {"yes", "y", "true", "1", "present", "positive", "pos"}:
            return True
        elif str_val in {"no", "n", "false", "0", "absent", "negative", "neg"}:
            return False
        else:
            raise ValidationError(f"{field_name} must be Yes/No or Present/Absent")
    
    @staticmethod
    def cross_field_validation(age: int, bmi: float, glucose: float, symptoms_count: int) -> None:
        """Perform cross-field validation for unrealistic combinations."""
        
        # Very young age with very high BMI is unusual but possible
        if age < 10 and bmi > 35:
            raise ValidationError(
                "Unusual combination: Very young age with high BMI. "
                "Please verify your age and weight/height values."
            )
        
        # Very old age with very low glucose might indicate data error
        if age > 100 and glucose < 80:
            raise ValidationError(
                "Unusual combination: Very advanced age with low glucose. "
                "Please verify your values."
            )
        
        # Very high glucose with no symptoms is less likely (but possible)
        if glucose > 300 and symptoms_count == 0:
            raise ValidationError(
                "Note: Very high glucose (>300) with no symptoms is unusual. "
                "Please verify you've selected all applicable symptoms."
            )
        
        # Extreme BMI values
        if bmi < 12 or bmi > 55:
            raise ValidationError(
                f"Extreme BMI value ({bmi:.1f}). Please double-check your weight and height."
            )
    
    @staticmethod
    def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entire payload and return cleaned/validated data.
        
        Args:
            payload: Dictionary of user input
            
        Returns:
            Dictionary of validated data
            
        Raises:
            ValidationError: If any validation fails
        """
        errors = []
        validated = {}
        
        try:
            # Age validation
            if "age" not in payload or not payload["age"]:
                errors.append("Age is required")
            else:
                validated["age"] = InputValidator.validate_age(payload["age"])
            
            # Gender validation
            if "gender" not in payload or not payload["gender"]:
                errors.append("Gender is required")
            else:
                validated["gender"] = InputValidator.validate_gender(payload["gender"])
            
            # Weight and Height OR BMI
            bmi_provided = "bmi" in payload and payload["bmi"]
            weight_height_provided = (
                "weight_kg" in payload and payload["weight_kg"] and
                "height_cm" in payload and payload["height_cm"]
            )
            
            if not bmi_provided and not weight_height_provided:
                errors.append("Either BMI or (Weight and Height) is required")
            elif weight_height_provided:
                weight, height = InputValidator.validate_weight_height(
                    payload["weight_kg"], payload["height_cm"]
                )
                validated["weight_kg"] = weight
                validated["height_cm"] = height
                validated["bmi"] = weight / ((height / 100) ** 2)
            else:
                validated["bmi"] = InputValidator.validate_bmi(payload["bmi"])
            
            # Glucose level
            glucose_type = payload.get("glucose_test_type", "random")
            fasting_glucose = payload.get("fasting_glucose")
            random_glucose = payload.get("random_glucose")
            
            if fasting_glucose:
                validated["glucose_level"] = InputValidator.validate_glucose(
                    fasting_glucose, "fasting"
                )
            elif random_glucose:
                validated["glucose_level"] = InputValidator.validate_glucose(
                    random_glucose, "random"
                )
            else:
                errors.append("Either Fasting or Random glucose level is required")
            
            # HbA1c
            if "hba1c" not in payload or not payload["hba1c"]:
                errors.append("HbA1c is required")
            else:
                validated["hba1c"] = InputValidator.validate_hba1c(payload["hba1c"])
            
            # C-Peptide (optional)
            if "c_peptide" in payload and payload["c_peptide"]:
                validated["c_peptide"] = InputValidator.validate_c_peptide(payload["c_peptide"])
            else:
                validated["c_peptide"] = 0.0
            
            # Family History
            if "family_history" not in payload or not payload["family_history"]:
                errors.append("Family History is required")
            else:
                validated["family_history"] = InputValidator.validate_boolean_field(
                    payload["family_history"], "Family History"
                )
            
            # Ketone Presence
            if "ketone_presence" not in payload or not payload["ketone_presence"]:
                errors.append("Ketone Presence is required")
            else:
                validated["ketone_presence"] = InputValidator.validate_boolean_field(
                    payload["ketone_presence"], "Ketone Presence"
                )
            
            # Symptoms (count for cross-field validation)
            symptoms_count = 0
            symptom_fields = [
                "symptoms.polyuria",
                "symptoms.polydipsia",
                "symptoms.weight_loss",
                "symptoms.fatigue",
                "symptoms.blurred_vision",
            ]
            for field in symptom_fields:
                if field in payload and str(payload[field]).lower() in {"true", "1", "on", "yes"}:
                    symptoms_count += 1
            
            validated["symptoms_count"] = symptoms_count
            
            # Raise any collected errors
            if errors:
                raise ValidationError(". ".join(errors))
            
            # Cross-field validation
            InputValidator.cross_field_validation(
                validated["age"],
                validated["bmi"],
                validated["glucose_level"],
                symptoms_count
            )
            
            return validated
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Unexpected validation error: {str(e)}")


def validate_input(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
    """
    Public function to validate input.
    
    Args:
        payload: User input dictionary
        
    Returns:
        Tuple of (is_valid, validated_data, error_message)
    """
    try:
        validated = InputValidator.validate_payload(payload)
        return True, validated, ""
    except ValidationError as e:
        return False, {}, str(e)
