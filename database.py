"""SQLite Database module for storing predictions and user data."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class DatabaseManager:
    """Manages SQLite database for predictions and user history."""
    
    DB_PATH = Path(__file__).parent / "predictions.db"
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        self.db_path = db_path or self.DB_PATH
        self.connection: Optional[sqlite3.Connection] = None
        self.init_db()
    
    def connect(self) -> sqlite3.Connection:
        """Create database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def init_db(self) -> None:
        """Initialize database tables."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User inputs table (stores all input parameters)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                age INTEGER,
                gender TEXT,
                bmi REAL,
                weight_kg REAL,
                height_cm REAL,
                glucose_level REAL,
                hba1c REAL,
                c_peptide REAL,
                family_history BOOLEAN,
                ketone_presence BOOLEAN,
                symptoms_polyuria BOOLEAN,
                symptoms_polydipsia BOOLEAN,
                symptoms_weight_loss BOOLEAN,
                symptoms_fatigue BOOLEAN,
                symptoms_blurred_vision BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Predictions table (stores prediction results)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_id INTEGER,
                user_id INTEGER,
                risk_level TEXT,
                confidence REAL,
                glucose_class TEXT,
                ketone_class TEXT,
                bmi_class TEXT,
                medical_interpretation TEXT,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (input_id) REFERENCES user_inputs(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Model evaluation metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                roc_auc REAL,
                confusion_matrix TEXT,
                training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accuracy_percentage TEXT,
                total_samples INTEGER,
                notes TEXT
            )
        ''')
        
        conn.commit()
    
    def store_user(self, username: str, email: Optional[str] = None) -> int:
        """Store or retrieve user."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user:
            return user[0]
        
        cursor.execute(
            'INSERT INTO users (username, email) VALUES (?, ?)',
            (username, email)
        )
        conn.commit()
        return cursor.lastrowid
    
    def store_input_data(self, user_id: int, input_data: Dict[str, Any]) -> int:
        """Store user input data."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_inputs (
                user_id, age, gender, bmi, weight_kg, height_cm,
                glucose_level, hba1c, c_peptide, family_history,
                ketone_presence, symptoms_polyuria, symptoms_polydipsia,
                symptoms_weight_loss, symptoms_fatigue, symptoms_blurred_vision
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            input_data.get('age', 0),
            input_data.get('gender', ''),
            input_data.get('bmi', 0),
            input_data.get('weight_kg', 0),
            input_data.get('height_cm', 0),
            input_data.get('glucose_level', 0),
            input_data.get('hba1c', 0),
            input_data.get('c_peptide', 0),
            1 if input_data.get('family_history') else 0,
            1 if input_data.get('ketone_presence') else 0,
            1 if input_data.get('symptoms', {}).get('polyuria') else 0,
            1 if input_data.get('symptoms', {}).get('polydipsia') else 0,
            1 if input_data.get('symptoms', {}).get('weight_loss') else 0,
            1 if input_data.get('symptoms', {}).get('fatigue') else 0,
            1 if input_data.get('symptoms', {}).get('blurred_vision') else 0,
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def store_prediction(self, user_id: int, input_id: int, prediction: Dict[str, Any]) -> int:
        """Store prediction result."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions (
                user_id, input_id, risk_level, confidence,
                glucose_class, ketone_class, bmi_class,
                medical_interpretation, model_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            input_id,
            prediction.get('risk_level', ''),
            prediction.get('confidence', 0),
            prediction.get('glucose', ''),
            prediction.get('ketones', ''),
            prediction.get('bmi', ''),
            prediction.get('medical_interpretation', ''),
            prediction.get('used_model', 'Unknown'),
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def store_model_metrics(self, model_name: str, metrics: Dict[str, Any]) -> None:
        """Store model evaluation metrics."""
        conn = self.connect()
        cursor = conn.cursor()
        
        confusion_matrix_str = json.dumps(metrics.get('confusion_matrix', []))
        
        cursor.execute('''
            INSERT INTO model_metrics (
                model_name, accuracy, precision, recall,
                f1_score, roc_auc, confusion_matrix,
                accuracy_percentage, total_samples, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model_name,
            metrics.get('accuracy', 0),
            metrics.get('precision', 0),
            metrics.get('recall', 0),
            metrics.get('f1_score', 0),
            metrics.get('roc_auc', 0),
            confusion_matrix_str,
            f"{metrics.get('accuracy', 0):.2%}",
            metrics.get('total_samples', 0),
            metrics.get('notes', ''),
        ))
        
        conn.commit()
    
    def get_user_predictions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve user's prediction history."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT
                p.id, p.risk_level, p.confidence, p.glucose_class,
                p.ketone_class, p.bmi_class, p.created_at,
                ui.age, ui.glucose_level, ui.hba1c
            FROM predictions p
            JOIN user_inputs ui ON p.input_id = ui.id
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_all_predictions(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve all predictions (for admin/analytics)."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT
                p.id, p.risk_level, p.confidence, p.glucose_class,
                p.ketone_class, ui.age, ui.gender, ui.glucose_level,
                ui.hba1c, p.created_at, u.username
            FROM predictions p
            JOIN user_inputs ui ON p.input_id = ui.id
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total_predictions = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT risk_level, COUNT(*) as count
            FROM predictions
            GROUP BY risk_level
        ''')
        risk_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute('''
            SELECT AVG(confidence) FROM predictions
        ''')
        avg_confidence = cursor.fetchone()[0] or 0
        
        return {
            'total_users': total_users,
            'total_predictions': total_predictions,
            'risk_breakdown': risk_breakdown,
            'average_confidence': avg_confidence,
        }
    
    def get_model_metrics(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve model evaluation metrics."""
        conn = self.connect()
        cursor = conn.cursor()
        
        if model_name:
            cursor.execute('''
                SELECT * FROM model_metrics
                WHERE model_name = ?
                ORDER BY training_date DESC
            ''', (model_name,))
        else:
            cursor.execute('''
                SELECT * FROM model_metrics
                ORDER BY training_date DESC
            ''')
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def export_to_csv(self, filename: str = "predictions_export.csv") -> str:
        """Export all predictions to CSV."""
        import csv
        
        predictions = self.get_all_predictions()
        
        export_path = Path(__file__).parent / "exports" / filename
        export_path.parent.mkdir(exist_ok=True)
        
        if not predictions:
            return str(export_path)
        
        keys = predictions[0].keys()
        
        with open(export_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(predictions)
        
        return str(export_path)


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def init_database() -> None:
    """Initialize database."""
    get_db()
