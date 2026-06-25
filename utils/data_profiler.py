import pandas as pd
import numpy as np

def profile_data(df, sales_col=None, profit_col=None, customers_col=None):
    """
    Analyzes the uploaded DataFrame and calculates key data quality indicators:
    records count, duplicate records, missing values, and a composite Data Quality Score.
    """
    total_records = len(df)
    total_cols = len(df.columns)
    
    if total_records == 0:
        return {
            "total_records": 0,
            "total_columns": total_cols,
            "missing_cells": 0,
            "missing_pct": 0.0,
            "duplicate_rows": 0,
            "duplicate_pct": 0.0,
            "quality_score": 100.0,
            "type_summary": pd.DataFrame()
        }
    
    # Calculate missing values
    missing_cells = df.isnull().sum().sum()
    total_cells = df.size
    missing_pct = (missing_cells / total_cells) * 100 if total_cells > 0 else 0.0
    
    # Calculate duplicates
    duplicate_rows = df.duplicated().sum()
    duplicate_pct = (duplicate_rows / total_records) * 100
    
    # Custom Data Quality Score Calculation
    # - Start at 100%
    # - Deduct for missing values (weighted heavily)
    # - Deduct for duplicates (weighted moderately)
    # - Deduct for negative sales/customers (logical data issues)
    missing_deduction = missing_pct * 1.5
    duplicate_deduction = duplicate_pct * 1.0
    
    logical_issues_deduction = 0.0
    if sales_col and sales_col in df.columns:
        try:
            neg_sales = (df[sales_col].astype(float) < 0).sum()
            logical_issues_deduction += (neg_sales / total_records) * 20.0
        except Exception:
            pass
            
    if customers_col and customers_col in df.columns:
        try:
            neg_cust = (df[customers_col].astype(float) < 0).sum()
            logical_issues_deduction += (neg_cust / total_records) * 20.0
        except Exception:
            pass
            
    quality_score = 100.0 - missing_deduction - duplicate_deduction - logical_issues_deduction
    quality_score = max(0.0, min(100.0, quality_score))
    
    # Compile column summaries
    column_details = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct = (null_count / total_records) * 100
        unique_count = df[col].nunique()
        dtype = str(df[col].dtype)
        
        # Determine sample values
        samples = df[col].dropna().head(3).tolist()
        sample_str = ", ".join([str(s) for s in samples])
        if len(sample_str) > 40:
            sample_str = sample_str[:37] + "..."
            
        column_details.append({
            "Column Name": col,
            "Data Type": dtype,
            "Unique Count": unique_count,
            "Null Values": null_count,
            "Null Pct": f"{null_pct:.2f}%",
            "Sample Values": sample_str
        })
        
    column_summary_df = pd.DataFrame(column_details)
    
    return {
        "total_records": total_records,
        "total_columns": total_cols,
        "missing_cells": missing_cells,
        "missing_pct": round(missing_pct, 2),
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": round(duplicate_pct, 2),
        "quality_score": round(quality_score, 1),
        "type_summary": column_summary_df
    }
