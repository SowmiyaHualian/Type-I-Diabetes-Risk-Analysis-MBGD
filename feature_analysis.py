"""Feature quality and correlation analysis module."""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json


class FeatureAnalyzer:
    """Analyzes feature quality, correlations, and relationships."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialize with data."""
        self.data = data
        self.feature_columns = [
            "Age", "Gender", "BMI", "Glucose_Level", "HbA1c",
            "Family_History", "Frequent_Urination", "Excessive_Thirst",
            "Unexplained_Weight_Loss", "Fatigue", "Blurred_Vision",
            "C_Peptide", "Autoantibodies"
        ]
    
    def calculate_feature_correlation(self, target_col: str = "Type1_Diabetes_Indicator") -> Dict[str, float]:
        """Calculate correlation of each feature with target."""
        correlations = {}
        
        for col in self.feature_columns:
            if col in self.data.columns and target_col in self.data.columns:
                # Calculate correlation (Pearson for numeric, Point-biserial for binary)
                valid_data = self.data[[col, target_col]].dropna()
                if len(valid_data) > 1:
                    correlation = valid_data[col].corr(valid_data[target_col])
                    correlations[col] = float(correlation) if not np.isnan(correlation) else 0.0
        
        return correlations
    
    def identify_redundant_features(self, threshold: float = 0.9) -> List[Tuple[str, str, float]]:
        """Identify highly correlated feature pairs (redundancy)."""
        redundant_pairs = []
        
        numeric_data = self.data[self.feature_columns].select_dtypes(include=[np.number])
        
        if numeric_data.shape[1] < 2:
            return redundant_pairs
        
        corr_matrix = numeric_data.corr().abs()
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                correlation = corr_matrix.iloc[i, j]
                if correlation > threshold:
                    feat1 = corr_matrix.columns[i]
                    feat2 = corr_matrix.columns[j]
                    redundant_pairs.append((feat1, feat2, float(correlation)))
        
        return redundant_pairs
    
    def calculate_feature_importance_scores(self) -> Dict[str, Dict[str, float]]:
        """Calculate multiple importance metrics for features."""
        importance_scores = {}
        
        for col in self.feature_columns:
            if col not in self.data.columns:
                continue
            
            series = self.data[col].dropna()
            
            if len(series) == 0:
                continue
            
            scores = {
                'variance': float(series.var()),
                'std_dev': float(series.std()),
                'skewness': float(series.skew()),
                'missing_ratio': float(self.data[col].isna().sum() / len(self.data)),
            }
            
            # Normalize variance to 0-1 range for comparison
            if scores['variance'] > 0:
                scores['normalized_variance'] = min(1.0, scores['variance'] / series.mean() ** 2)
            else:
                scores['normalized_variance'] = 0.0
            
            importance_scores[col] = scores
        
        return importance_scores
    
    def get_feature_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed statistics for each feature."""
        stats = {}
        
        for col in self.feature_columns:
            if col not in self.data.columns:
                continue
            
            series = self.data[col].dropna()
            
            if len(series) == 0:
                continue
            
            is_numeric = pd.api.types.is_numeric_dtype(series)
            
            stat_dict = {
                'count': int(len(series)),
                'missing': int(self.data[col].isna().sum()),
                'data_type': str(series.dtype),
            }
            
            if is_numeric:
                stat_dict.update({
                    'mean': float(series.mean()),
                    'median': float(series.median()),
                    'std': float(series.std()),
                    'min': float(series.min()),
                    'max': float(series.max()),
                    'q25': float(series.quantile(0.25)),
                    'q75': float(series.quantile(0.75)),
                })
            else:
                stat_dict['unique_values'] = int(series.nunique())
                stat_dict['most_common'] = str(series.mode()[0]) if len(series.mode()) > 0 else 'N/A'
            
            stats[col] = stat_dict
        
        return stats
    
    def detect_outliers(self, method: str = 'iqr') -> Dict[str, List[int]]:
        """Detect outliers in numeric features."""
        outliers = {}
        
        numeric_data = self.data[self.feature_columns].select_dtypes(include=[np.number])
        
        for col in numeric_data.columns:
            series = self.data[col].dropna()
            
            if method == 'iqr':
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_indices = [
                    int(idx) for idx, val in series.items()
                    if val < lower_bound or val > upper_bound
                ]
                
                if outlier_indices:
                    outliers[col] = {
                        'count': len(outlier_indices),
                        'indices': outlier_indices[:10],  # First 10
                        'bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)},
                    }
        
        return outliers
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive feature analysis report."""
        report = {
            'total_samples': int(len(self.data)),
            'total_features': len(self.feature_columns),
            'feature_statistics': self.get_feature_statistics(),
            'feature_importance': self.calculate_feature_importance_scores(),
            'redundant_features': self.identify_redundant_features(),
            'outliers': self.detect_outliers(),
            'data_quality': self._assess_data_quality(),
        }
        
        return report
    
    def _assess_data_quality(self) -> Dict[str, Any]:
        """Assess overall data quality."""
        total_cells = len(self.data) * len(self.feature_columns)
        missing_cells = self.data[self.feature_columns].isna().sum().sum()
        completeness = 1.0 - (missing_cells / total_cells)
        
        # Check for duplicates
        duplicate_rows = self.data.duplicated(subset=self.feature_columns).sum()
        
        return {
            'completeness': float(completeness),
            'missing_cells': int(missing_cells),
            'duplicate_rows': int(duplicate_rows),
            'quality_score': float(completeness * (1 - min(duplicate_rows / len(self.data), 0.5))),
        }
    
    def recommend_feature_drops(self, variance_threshold: float = 0.01) -> List[str]:
        """Recommend features to drop based on low variance."""
        recommendations = []
        importance = self.calculate_feature_importance_scores()
        
        for feature, scores in importance.items():
            if scores['variance'] < variance_threshold:
                recommendations.append(feature)
        
        return recommendations


def analyze_dataset(data_path: Path) -> Dict[str, Any]:
    """Analyze a dataset and return comprehensive report."""
    try:
        if data_path.suffix.lower() in {'.xlsx', '.xls'}:
            df = pd.read_excel(data_path)
        else:
            df = pd.read_csv(data_path)
        
        analyzer = FeatureAnalyzer(df)
        report = analyzer.generate_report()
        
        return {
            'success': True,
            'report': report,
            'message': 'Analysis completed successfully'
        }
    
    except Exception as e:
        return {
            'success': False,
            'report': {},
            'message': f'Analysis failed: {str(e)}'
        }


def save_analysis_report(report: Dict[str, Any], output_path: Path) -> str:
    """Save analysis report to JSON file."""
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    return str(output_path)
