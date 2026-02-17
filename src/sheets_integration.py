"""
Google Sheets Integration using gspread
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Scopes for Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


class GoogleSheetsIntegration:
    """Handles 2-way sync with Google Sheets"""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Initialize Google Sheets integration
        
        Args:
            credentials_path: Path to service account JSON
            spreadsheet_id: Google Sheets ID
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API
        
        Returns:
            bool: True if authentication successful
        """
        try:
            if not Path(self.credentials_path).exists():
                logger.warning(f"Credentials file not found: {self.credentials_path}")
                logger.warning("Google Sheets sync will be disabled")
                return False
            
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )
            
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            logger.info(f"✅ Authenticated with Google Sheets: {self.spreadsheet.title}")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def get_sheet(self, sheet_name: str):
        """Get worksheet by name"""
        if not self.spreadsheet:
            raise ValueError("Not authenticated with Google Sheets")
        
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Sheet '{sheet_name}' not found")
            return None
    
    def read_pilots(self, sheet_name: str = "Pilots") -> pd.DataFrame:
        """
        Read pilots from Google Sheet
        
        Args:
            sheet_name: Name of the sheet
            
        Returns:
            pd.DataFrame: Pilots data
        """
        try:
            sheet = self.get_sheet(sheet_name)
            if not sheet:
                return pd.DataFrame()
            
            records = sheet.get_all_records()
            df = pd.DataFrame(records)
            
            logger.info(f"✅ Loaded {len(df)} pilots from '{sheet_name}'")
            return df
            
        except Exception as e:
            logger.error(f"Failed to read pilots: {e}")
            return pd.DataFrame()
    
    def read_missions(self, sheet_name: str = "Missions") -> pd.DataFrame:
        """
        Read missions from Google Sheet
        
        Args:
            sheet_name: Name of the sheet
            
        Returns:
            pd.DataFrame: Missions data
        """
        try:
            sheet = self.get_sheet(sheet_name)
            if not sheet:
                return pd.DataFrame()
            
            records = sheet.get_all_records()
            df = pd.DataFrame(records)
            
            logger.info(f"✅ Loaded {len(df)} missions from '{sheet_name}'")
            return df
            
        except Exception as e:
            logger.error(f"Failed to read missions: {e}")
            return pd.DataFrame()
    
    def read_drones(self, sheet_name: str = "Drones") -> pd.DataFrame:
        """
        Read drones from Google Sheet
        
        Args:
            sheet_name: Name of the sheet
            
        Returns:
            pd.DataFrame: Drones data
        """
        try:
            sheet = self.get_sheet(sheet_name)
            if not sheet:
                return pd.DataFrame()
            
            records = sheet.get_all_records()
            df = pd.DataFrame(records)
            
            logger.info(f"✅ Loaded {len(df)} drones from '{sheet_name}'")
            return df
            
        except Exception as e:
            logger.error(f"Failed to read drones: {e}")
            return pd.DataFrame()
    
    def update_assignment_status(
        self,
        assignment_id: str,
        pilot_name: str,
        status: str,
        sheet_name: str = "Assignments"
    ) -> bool:
        """
        Update assignment status in Google Sheets
        
        Args:
            assignment_id: Assignment ID
            pilot_name: Assigned pilot name
            status: New status
            sheet_name: Name of assignments sheet
            
        Returns:
            bool: True if successful
        """
        try:
            sheet = self.get_sheet(sheet_name)
            if not sheet:
                return False
            
            # Find row with matching assignment ID
            cell = sheet.find(assignment_id)
            if not cell:
                logger.warning(f"Assignment {assignment_id} not found in sheet")
                return False
            
            row = cell.row
            
            # Update status column (adjust column letter as needed)
            sheet.update_cell(row, 4, status)  # Column D for status
            sheet.update_cell(row, 3, pilot_name)  # Column C for pilot
            
            logger.info(f"✅ Updated assignment {assignment_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update assignment: {e}")
            return False
    
    def append_assignment(
        self,
        assignment_data: Dict,
        sheet_name: str = "Assignments"
    ) -> bool:
        """
        Append new assignment to Google Sheets
        
        Args:
            assignment_data: Assignment details
            sheet_name: Name of assignments sheet
            
        Returns:
            bool: True if successful
        """
        try:
            sheet = self.get_sheet(sheet_name)
            if not sheet:
                return False
            
            # Format data as row
            row_data = [
                assignment_data.get("id", ""),
                assignment_data.get("mission_id", ""),
                assignment_data.get("pilot_name", ""),
                assignment_data.get("status", "pending"),
                assignment_data.get("created_at", ""),
                assignment_data.get("notes", "")
            ]
            
            sheet.append_row(row_data)
            
            logger.info(f"✅ Created assignment: {assignment_data.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append assignment: {e}")
            return False
    
    def sync_pilot_availability(
        self,
        pilot_id: str,
        status: str,
        days_available: int,
        sheet_name: str = "Pilots"
    ) -> bool:
        """
        Update pilot availability in Google Sheets
        
        Args:
            pilot_id: Pilot ID
            status: Availability status
            days_available: Days available
            sheet_name: Name of pilots sheet
            
        Returns:
            bool: True if successful
        """
        try:
            sheet = self.get_sheet(sheet_name)
            if not sheet:
                return False
            
            cell = sheet.find(pilot_id)
            if not cell:
                logger.warning(f"Pilot {pilot_id} not found in sheet")
                return False
            
            row = cell.row
            
            # Update status and availability columns
            sheet.update_cell(row, 7, status)  # Column G for status
            sheet.update_cell(row, 8, days_available)  # Column H for days available
            
            logger.info(f"✅ Updated pilot {pilot_id}: {status}, {days_available} days available")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync pilot: {e}")
            return False
    
    def update_mission_status(
        self,
        mission_id: str,
        status: str,
        assigned_pilot: str = None,
        sheet_name: str = "Missions"
    ) -> bool:
        """
        Update mission status in Google Sheets
        
        Args:
            mission_id: Mission ID
            status: New status
            assigned_pilot: Assigned pilot name
            sheet_name: Name of missions sheet
            
        Returns:
            bool: True if successful
        """
        try:
            sheet = self.get_sheet(sheet_name)
            if not sheet:
                return False
            
            cell = sheet.find(mission_id)
            if not cell:
                logger.warning(f"Mission {mission_id} not found in sheet")
                return False
            
            row = cell.row
            
            # Update status column
            sheet.update_cell(row, 6, status)  # Column F for status
            
            if assigned_pilot:
                sheet.update_cell(row, 7, assigned_pilot)  # Column G for assigned pilot
            
            logger.info(f"✅ Updated mission {mission_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update mission: {e}")
            return False
    
    def create_activity_log(
        self,
        activity: Dict,
        sheet_name: str = "Activity Log"
    ) -> bool:
        """
        Log activity to activity sheet
        
        Args:
            activity: Activity details
            sheet_name: Name of activity sheet
            
        Returns:
            bool: True if successful
        """
        try:
            # Try to get sheet, create if doesn't exist
            sheet = self.get_sheet(sheet_name)
            if not sheet:
                sheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                # Add headers
                sheet.append_row(["Timestamp", "Action", "Pilot", "Mission", "Status", "Details"])
            
            row_data = [
                activity.get("timestamp", ""),
                activity.get("action_type", ""),
                activity.get("pilot_name", ""),
                activity.get("mission_id", ""),
                activity.get("status", ""),
                activity.get("details", "")
            ]
            
            sheet.append_row(row_data)
            
            logger.info(f"✅ Logged activity: {activity.get('action_type')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            return False
