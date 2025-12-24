"""
Data Service Module for Eco Club Dashboard
Handles data loading and processing from Excel files.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple
import re
import logging


class DataService:
    """Service class for loading and processing Eco Club data."""
    
    def __init__(self, data_folder: str = "."):
        """
        Initialize the DataService.
        
        Args:
            data_folder: Path to the folder containing Excel files
        """
        self.data_folder = Path(data_folder)
        
        # CSV files (faster)
        self.school_master_csv = self.data_folder / "School Master.csv"
        self.notifications_csv = self.data_folder / "Notifications.csv"
        self.tree_csv = self.data_folder / "Tree_Data.csv"
        
        # Excel files (fallback)
        self.school_master_xlsx = self.data_folder / "School Master.xlsx"
        self.notifications_xlsx = self.data_folder / "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
        self.tree_xlsx = self.data_folder / "UTTAR PRADESH.xlsx"
        
        # Auto-convert Excel to CSV if CSV doesn't exist or is older
        self._auto_convert_to_csv()
    
    def normalize_udise(self, s: pd.Series, width: int = 11) -> pd.Series:
        """Normalize UDISE codes to standard format - optimized version."""
        # Fast string operations - all vectorized
        return (s.astype(str)
                 .str.strip()
                 .str.replace('.0', '', regex=False)
                 .str.replace(r'\D', '', regex=True)
                 .str.zfill(width))
    
    def _auto_convert_to_csv(self):
        """Auto-convert Excel files to CSV if needed for faster loading."""
        try:
            # Convert School Master if needed
            if self.school_master_xlsx.exists() and (
                not self.school_master_csv.exists() or 
                self.school_master_xlsx.stat().st_mtime > self.school_master_csv.stat().st_mtime
            ):
                df = pd.read_excel(self.school_master_xlsx, dtype=str)
                df.to_csv(self.school_master_csv, index=False)
            
            # Convert Notifications if needed
            if self.notifications_xlsx.exists() and (
                not self.notifications_csv.exists() or 
                self.notifications_xlsx.stat().st_mtime > self.notifications_csv.stat().st_mtime
            ):
                df = pd.read_excel(self.notifications_xlsx, dtype=str)
                df.to_csv(self.notifications_csv, index=False)
            
            # Convert Tree Data if needed
            if self.tree_xlsx.exists() and (
                not self.tree_csv.exists() or 
                self.tree_xlsx.stat().st_mtime > self.tree_csv.stat().st_mtime
            ):
                df = pd.read_excel(self.tree_xlsx, dtype=str)
                df.to_csv(self.tree_csv, index=False)
        except Exception as e:
            logging.warning(f"CSV conversion failed: {e}. Will use Excel files instead.")
    
    def load_data(self) -> Tuple[pd.DataFrame, bool, str]:
        """
        Load and process data from Excel files.
        
        Returns:
            Tuple containing:
                - Processed DataFrame with merged data
                - Success flag (True if data loaded successfully)
                - Error message (empty string if successful)
        """
        try:
            # Use CSV if available (10-20x faster)
            if self.school_master_csv.exists() and self.notifications_csv.exists() and self.tree_csv.exists():
                # Load from CSV - super fast!
                school_master_df = pd.read_csv(
                    self.school_master_csv,
                    dtype=str,
                    usecols=['District Name', 'School Name', 'UDISE Code', 'School Management', 'School Category']
                )
                
                notifications_df = pd.read_csv(self.notifications_csv, dtype=str)
                
                tree_df = pd.read_csv(
                    self.tree_csv,
                    dtype=str,
                    usecols=['UDISE ID', 'Saplings']
                )
            else:
                # Fallback to Excel
                if not self.school_master_xlsx.exists():
                    return pd.DataFrame(), False, f"Data files not found in {self.data_folder} folder"
                
                school_master_df = pd.read_excel(
                    self.school_master_xlsx,
                    dtype=str,
                    usecols=['District Name', 'School Name', 'UDISE Code', 'School Management', 'School Category'],
                    engine='openpyxl'
                )
                
                notifications_df = pd.read_excel(self.notifications_xlsx, dtype=str, engine='openpyxl')
                tree_df = pd.read_excel(self.tree_xlsx, dtype=str, usecols=['UDISE ID', 'Saplings'], engine='openpyxl')
            
            # Process and merge data
            processed_df = self._process_data(school_master_df, notifications_df, tree_df)
            
            return processed_df, True, ""
            
        except Exception as e:
            return pd.DataFrame(), False, f"Error loading data: {str(e)}"
    
    def _process_data(self, school_master_df: pd.DataFrame, notifications_df: pd.DataFrame, 
                      tree_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and merge school master, notifications, and tree data.
        
        Args:
            school_master_df: DataFrame containing all schools
            notifications_df: DataFrame containing schools that uploaded notifications
            tree_df: DataFrame containing tree plantation data
            
        Returns:
            Processed DataFrame with notification and tree status
        """
        # Create a copy to avoid modifying original data
        df = school_master_df.copy()
        
        # Rename 'District Name' to 'District' if it exists
        if 'District Name' in df.columns:
            df = df.rename(columns={'District Name': 'District'})
        
        # Normalize UDISE Code in master
        df['UDISE Code'] = self.normalize_udise(df['UDISE Code'])
        df = df[df['UDISE Code'].astype(bool)]
        df = df.drop_duplicates(subset=['UDISE Code'], keep='first')
        
        # Process Notifications - optimized
        df['Notification Uploaded'] = 'No'
        if not notifications_df.empty:
            # Find UDISE column
            notif_udise_col = [col for col in notifications_df.columns 
                              if 'UDISE' in str(col).upper()][0] if any('UDISE' in str(col).upper() 
                              for col in notifications_df.columns) else None
            
            if notif_udise_col:
                uploaded_codes = set(self.normalize_udise(notifications_df[notif_udise_col]))
                df['Notification Uploaded'] = df['UDISE Code'].isin(uploaded_codes).map({True: 'Yes', False: 'No'})
        
        # Process Tree Data - optimized
        df['Trees Planted'] = 0
        df['Tree Uploaded'] = 'No'
        
        if not tree_df.empty and 'UDISE ID' in tree_df.columns and 'Saplings' in tree_df.columns:
            # Normalize and aggregate in one go
            tree_df['UDISE ID'] = self.normalize_udise(tree_df['UDISE ID'])
            tree_df['Saplings'] = pd.to_numeric(tree_df['Saplings'], errors='coerce').fillna(0).astype(int)
            
            # Group by UDISE
            tree_summary = tree_df.groupby('UDISE ID')['Saplings'].sum().reset_index()
            tree_summary.columns = ['UDISE Code', 'Trees Planted']
            
            # Drop the existing column before merge to avoid conflicts
            df = df.drop(columns=['Trees Planted'])
            
            # Merge efficiently
            df = df.merge(tree_summary, on='UDISE Code', how='left')
            df['Trees Planted'] = df['Trees Planted'].fillna(0).astype(int)
            df['Tree Uploaded'] = (df['Trees Planted'] > 0).map({True: 'Yes', False: 'No'})
        
        # Select and reorder columns for display
        required_columns = ['District', 'School Name', 'UDISE Code', 'School Management', 'School Category', 
                           'Notification Uploaded', 'Trees Planted', 'Tree Uploaded']
        
        # Check if all required columns exist (except the ones we just added)
        base_columns = ['District', 'School Name', 'School Management', 'School Category']
        missing_columns = [col for col in base_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in School Master.xlsx: {', '.join(missing_columns)}")
        
        # Filter to only required columns
        df = df[required_columns]
        
        # Sort by District and School Name
        df = df.sort_values(['District', 'School Name']).reset_index(drop=True)
        
        return df
    
    def get_districts(self, df: pd.DataFrame) -> list:
        """
        Get sorted list of unique districts.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Sorted list of district names
        """
        if df.empty:
            return []
        return sorted(df['District'].unique().tolist())
    
    def get_schools_by_district(self, df: pd.DataFrame, district: str) -> list:
        """
        Get sorted list of schools for a specific district.
        
        Args:
            df: Processed DataFrame
            district: District name
            
        Returns:
            Sorted list of school names
        """
        if df.empty or district == "All":
            return []
        
        filtered_df = df[df['District'] == district]
        return sorted(filtered_df['School Name'].unique().tolist())
    
    def filter_data(self, df: pd.DataFrame, district: str, school: str, school_category: str,
                    notif_status: str, tree_status: str) -> pd.DataFrame:
        """
        Filter data based on selected criteria.
        
        Args:
            df: Processed DataFrame
            district: Selected district filter
            school: Selected school filter
            school_category: Selected school category filter
            notif_status: Selected notification status filter
            tree_status: Selected tree status filter
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        # Apply district filter
        if district != "All":
            filtered_df = filtered_df[filtered_df['District'] == district]
        
        # Apply school filter
        if school != "All":
            filtered_df = filtered_df[filtered_df['School Name'] == school]
        
        # Apply school category filter
        if school_category == "Secondary":
            # Already filtered to Secondary only in base data
            pass
        
        # Apply notification status filter
        if notif_status == "Notification NOT Uploaded":
            filtered_df = filtered_df[filtered_df['Notification Uploaded'] == 'No']
        elif notif_status == "Notification Uploaded":
            filtered_df = filtered_df[filtered_df['Notification Uploaded'] == 'Yes']
        
        # Apply tree status filter
        if tree_status == "Tree NOT Uploaded":
            filtered_df = filtered_df[filtered_df['Tree Uploaded'] == 'No']
        elif tree_status == "Tree Uploaded":
            filtered_df = filtered_df[filtered_df['Tree Uploaded'] == 'Yes']
        
        return filtered_df
