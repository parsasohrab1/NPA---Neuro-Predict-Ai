"""
EHR/HIS Integration Service
سرویس برای یکپارچه‌سازی با سیستم‌های EHR/HIS
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
import logging

logger = logging.getLogger(__name__)


class EHRService:
    """Service for EHR/HIS integration"""
    
    def __init__(self, ehr_api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.ehr_api_url = ehr_api_url
        self.api_key = api_key
        self.timeout = 30.0
    
    async def get_patient_data(
        self,
        patient_id: str
    ) -> Dict[str, Any]:
        """
        دریافت اطلاعات بیمار از EHR
        
        Args:
            patient_id: شناسه بیمار در EHR
        
        Returns:
            اطلاعات بیمار
        """
        if not self.ehr_api_url:
            logger.warning("EHR API URL not configured")
            return {}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.get(
                    f"{self.ehr_api_url}/patients/{patient_id}",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Error fetching patient data from EHR: {e}")
            return {}
    
    async def get_patient_lab_results(
        self,
        patient_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        دریافت نتایج آزمایش‌های بیمار از EHR
        
        Args:
            patient_id: شناسه بیمار
            start_date: تاریخ شروع (YYYY-MM-DD)
            end_date: تاریخ پایان (YYYY-MM-DD)
        
        Returns:
            لیست نتایج آزمایش
        """
        if not self.ehr_api_url:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                params = {}
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date
                
                response = await client.get(
                    f"{self.ehr_api_url}/patients/{patient_id}/lab-results",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                return response.json().get("results", [])
        
        except httpx.HTTPError as e:
            logger.error(f"Error fetching lab results from EHR: {e}")
            return []
    
    async def get_patient_medications(
        self,
        patient_id: str
    ) -> List[Dict[str, Any]]:
        """
        دریافت داروهای بیمار از EHR
        
        Args:
            patient_id: شناسه بیمار
        
        Returns:
            لیست داروها
        """
        if not self.ehr_api_url:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.get(
                    f"{self.ehr_api_url}/patients/{patient_id}/medications",
                    headers=headers
                )
                response.raise_for_status()
                return response.json().get("medications", [])
        
        except httpx.HTTPError as e:
            logger.error(f"Error fetching medications from EHR: {e}")
            return []
    
    async def get_patient_vital_signs(
        self,
        patient_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        دریافت علائم حیاتی بیمار از EHR
        
        Args:
            patient_id: شناسه بیمار
            start_date: تاریخ شروع
            end_date: تاریخ پایان
        
        Returns:
            لیست علائم حیاتی
        """
        if not self.ehr_api_url:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                params = {}
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date
                
                response = await client.get(
                    f"{self.ehr_api_url}/patients/{patient_id}/vital-signs",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                return response.json().get("vital_signs", [])
        
        except httpx.HTTPError as e:
            logger.error(f"Error fetching vital signs from EHR: {e}")
            return []
    
    async def send_prediction_result(
        self,
        patient_id: str,
        prediction_result: Dict[str, Any]
    ) -> bool:
        """
        ارسال نتیجه پیش‌بینی به EHR
        
        Args:
            patient_id: شناسه بیمار
            prediction_result: نتیجه پیش‌بینی
        
        Returns:
            True اگر موفق بود
        """
        if not self.ehr_api_url:
            logger.warning("EHR API URL not configured")
            return False
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Content-Type": "application/json"
                }
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                payload = {
                    "patient_id": patient_id,
                    "prediction": prediction_result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "NeuroPredict-AI"
                }
                
                response = await client.post(
                    f"{self.ehr_api_url}/patients/{patient_id}/predictions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return True
        
        except httpx.HTTPError as e:
            logger.error(f"Error sending prediction to EHR: {e}")
            return False
    
    async def sync_patient_data(
        self,
        patient_id: str
    ) -> Dict[str, Any]:
        """
        همگام‌سازی کامل اطلاعات بیمار از EHR
        
        Args:
            patient_id: شناسه بیمار
        
        Returns:
            اطلاعات همگام‌سازی شده
        """
        sync_result = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "patient_data": {},
            "lab_results": [],
            "medications": [],
            "vital_signs": [],
            "success": False
        }
        
        try:
            # دریافت اطلاعات بیمار
            patient_data = await self.get_patient_data(patient_id)
            sync_result["patient_data"] = patient_data
            
            # دریافت نتایج آزمایش
            lab_results = await self.get_patient_lab_results(patient_id)
            sync_result["lab_results"] = lab_results
            
            # دریافت داروها
            medications = await self.get_patient_medications(patient_id)
            sync_result["medications"] = medications
            
            # دریافت علائم حیاتی
            vital_signs = await self.get_patient_vital_signs(patient_id)
            sync_result["vital_signs"] = vital_signs
            
            sync_result["success"] = True
        
        except Exception as e:
            logger.error(f"Error syncing patient data: {e}")
            sync_result["error"] = str(e)
        
        return sync_result

