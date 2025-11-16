"""
Integration Service - PACS/EHR/HL7/FHIR Integration
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
import json
import hmac
import hashlib

from ..core.config import settings
import redis.asyncio as redis


class HL7Message(BaseModel):
    """HL7 Message Model"""
    message_type: str
    message_control_id: str
    sending_application: str
    sending_facility: str
    receiving_application: str
    receiving_facility: str
    message_datetime: datetime
    data: Dict[str, Any]


class FHIRResource(BaseModel):
    """FHIR Resource Model"""
    resource_type: str
    id: Optional[str] = None
    data: Dict[str, Any]


class IntegrationService:
    """Service for integrating with external medical systems"""
    
    _redis: Optional[redis.Redis] = None

    @staticmethod
    async def _get_redis() -> Optional[redis.Redis]:
        if IntegrationService._redis is None:
            try:
                IntegrationService._redis = redis.from_url(
                    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                    decode_responses=True
                )
            except Exception:
                IntegrationService._redis = None
        return IntegrationService._redis

    # --- Security: HMAC signing/verification for outbound/inbound webhooks
    @staticmethod
    def sign_payload(payload: Dict[str, Any]) -> Optional[str]:
        if not settings.INTEGRATION_HMAC_SECRET:
            return None
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        signature = hmac.new(settings.INTEGRATION_HMAC_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return signature

    @staticmethod
    def verify_signature(payload: Dict[str, Any], signature: str) -> bool:
        if not settings.INTEGRATION_HMAC_SECRET:
            return False
        expected = IntegrationService.sign_payload(payload) or ""
        # constant time compare
        return hmac.compare_digest(expected, signature)

    # --- Idempotency
    @staticmethod
    async def is_idempotent(idempotency_key: str) -> bool:
        r = await IntegrationService._get_redis()
        if not r:
            return False
        try:
            return await r.exists(f"idemp:{idempotency_key}") == 1
        except Exception:
            return False

    @staticmethod
    async def mark_idempotent(idempotency_key: str, ttl_seconds: int = 24 * 3600) -> None:
        r = await IntegrationService._get_redis()
        if not r:
            return
        try:
            await r.setex(f"idemp:{idempotency_key}", ttl_seconds, "1")
        except Exception:
            pass

    @staticmethod
    async def send_hl7_message(message: HL7Message) -> Dict[str, Any]:
        """Send HL7 message to external system"""
        if not settings.HL7_FHIR_ENDPOINT:
            raise ValueError("HL7 endpoint not configured")
        
        # Format HL7 message (simplified - real implementation would use HL7 library)
        hl7_segments = [
            f"MSH|^~\\&|{message.sending_application}|{message.sending_facility}|"
            f"{message.receiving_application}|{message.receiving_facility}|"
            f"{message.message_datetime.strftime('%Y%m%d%H%M%S')}||{message.message_type}|"
            f"{message.message_control_id}|P|2.5"
        ]
        
        # Add data segments based on message type
        if message.message_type == "ADT^A01":  # Patient admit
            # Add patient demographics, etc.
            pass
        
        hl7_message = "\r".join(hl7_segments)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.HL7_FHIR_ENDPOINT}/hl7",
                    content=hl7_message,
                    headers={"Content-Type": "application/hl7-v2"}
                )
                response.raise_for_status()
                return {
                    "success": True,
                    "message_control_id": message.message_control_id,
                    "response": response.text
                }
            except httpx.HTTPError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message_control_id": message.message_control_id
                }
    
    @staticmethod
    async def send_fhir_resource(resource: FHIRResource) -> Dict[str, Any]:
        """Send FHIR resource to external system"""
        if not settings.HL7_FHIR_ENDPOINT:
            raise ValueError("FHIR endpoint not configured")
        
        url = f"{settings.HL7_FHIR_ENDPOINT}/fhir/{resource.resource_type}"
        if resource.id:
            url += f"/{resource.id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if resource.id:
                    # Update existing resource
                    response = await client.put(url, json=resource.data)
                else:
                    # Create new resource
                    response = await client.post(url, json=resource.data)
                
                response.raise_for_status()
                return {
                    "success": True,
                    "resource_type": resource.resource_type,
                    "resource_id": resource.id,
                    "response": response.json()
                }
            except httpx.HTTPError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "resource_type": resource.resource_type
                }
    
    @staticmethod
    async def get_fhir_resource(resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get FHIR resource from external system"""
        if not settings.HL7_FHIR_ENDPOINT:
            raise ValueError("FHIR endpoint not configured")
        
        url = f"{settings.HL7_FHIR_ENDPOINT}/fhir/{resource_type}/{resource_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None
    
    @staticmethod
    async def query_fhir_resources(
        resource_type: str,
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Query FHIR resources"""
        if not settings.HL7_FHIR_ENDPOINT:
            raise ValueError("FHIR endpoint not configured")
        
        url = f"{settings.HL7_FHIR_ENDPOINT}/fhir/{resource_type}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=search_params)
                response.raise_for_status()
                bundle = response.json()
                
                # Extract resources from FHIR Bundle
                resources = []
                if bundle.get("resourceType") == "Bundle" and "entry" in bundle:
                    for entry in bundle["entry"]:
                        if "resource" in entry:
                            resources.append(entry["resource"])
                
                return resources
            except httpx.HTTPError:
                return []
    
    @staticmethod
    async def fetch_pacs_study(study_instance_uid: str) -> Optional[Dict[str, Any]]:
        """Fetch study from PACS system"""
        if not settings.PACS_SERVER_URL:
            raise ValueError("PACS server not configured")
        
        url = f"{settings.PACS_SERVER_URL}/studies/{study_instance_uid}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None
    
    @staticmethod
    async def fetch_ehr_patient(patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch patient data from EHR system"""
        if not settings.EHR_API_URL:
            raise ValueError("EHR API not configured")
        
        url = f"{settings.EHR_API_URL}/patients/{patient_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None
    
    @staticmethod
    async def sync_patient_from_ehr(patient_id: str) -> Dict[str, Any]:
        """Sync patient data from EHR system"""
        ehr_data = await IntegrationService.fetch_ehr_patient(patient_id)
        
        if not ehr_data:
            return {
                "success": False,
                "error": "Patient not found in EHR system"
            }
        
        # Convert EHR data to internal format
        # This would typically involve mapping fields and creating/updating patient record
        return {
            "success": True,
            "patient_id": patient_id,
            "data": ehr_data
        }

    @staticmethod
    async def pull_patients_batch(updated_after: Optional[str] = None, cursor: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Pull-batch strategy to fetch patients incrementally."""
        if not settings.EHR_API_URL:
            raise ValueError("EHR API not configured")
        params: Dict[str, Any] = {"limit": limit}
        if updated_after:
            params["updated_after"] = updated_after
        if cursor:
            params["cursor"] = cursor
        url = f"{settings.EHR_API_URL}/patients"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                return {
                    "success": True,
                    "items": data.get("items", []),
                    "next_cursor": data.get("next_cursor"),
                    "total": data.get("total")
                }
            except httpx.HTTPError as e:
                return {"success": False, "error": str(e)}
    
    @staticmethod
    async def sync_imaging_from_pacs(study_instance_uid: str) -> Dict[str, Any]:
        """Sync imaging study from PACS system"""
        pacs_data = await IntegrationService.fetch_pacs_study(study_instance_uid)
        
        if not pacs_data:
            return {
                "success": False,
                "error": "Study not found in PACS system"
            }
        
        # Convert PACS data to internal format
        return {
            "success": True,
            "study_instance_uid": study_instance_uid,
            "data": pacs_data
        }

