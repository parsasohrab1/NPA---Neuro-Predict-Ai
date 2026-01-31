"""
HL7 v2 Integration Service
سرویس برای یکپارچه‌سازی با دستگاه‌های پزشکی با استفاده از HL7 v2
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class HL7v2Message:
    """HL7 v2 Message Parser and Builder"""
    
    def __init__(self, message: Optional[str] = None):
        self.segments = []
        self.field_separator = "|"
        self.component_separator = "^"
        self.repetition_separator = "~"
        self.escape_character = "\\"
        self.subcomponent_separator = "&"
        
        if message:
            self.parse(message)
    
    def parse(self, message: str) -> None:
        """
        Parse HL7 v2 message
        
        Args:
            message: HL7 v2 message string
        """
        # Remove carriage returns and split by segment separator
        message = message.replace("\r", "\n")
        lines = message.split("\n")
        
        for line in lines:
            line = line.strip()
            if line and line.startswith("MSH"):
                # Parse MSH segment to get separators
                self._parse_separators(line)
            
            if line:
                segment = self._parse_segment(line)
                if segment:
                    self.segments.append(segment)
    
    def _parse_separators(self, msh_line: str) -> None:
        """Parse separators from MSH segment"""
        if len(msh_line) >= 4:
            self.field_separator = msh_line[3]
        if len(msh_line) >= 5:
            self.component_separator = msh_line[4]
        if len(msh_line) >= 6:
            self.repetition_separator = msh_line[5]
        if len(msh_line) >= 7:
            self.escape_character = msh_line[6]
        if len(msh_line) >= 8:
            self.subcomponent_separator = msh_line[7]
    
    def _parse_segment(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single segment
        
        Returns:
            Dictionary with segment type and fields
        """
        fields = line.split(self.field_separator)
        if not fields:
            return None
        
        segment_type = fields[0]
        segment_data = {
            "type": segment_type,
            "fields": []
        }
        
        for i, field in enumerate(fields[1:], start=1):
            # Parse field with components
            components = self._parse_field(field)
            segment_data["fields"].append({
                "position": i,
                "value": field,
                "components": components
            })
        
        return segment_data
    
    def _parse_field(self, field: str) -> List[str]:
        """Parse field into components"""
        if not field:
            return []
        return field.split(self.component_separator)
    
    def get_segment(self, segment_type: str) -> Optional[Dict[str, Any]]:
        """Get first segment of specified type"""
        for segment in self.segments:
            if segment["type"] == segment_type:
                return segment
        return None
    
    def get_segments(self, segment_type: str) -> List[Dict[str, Any]]:
        """Get all segments of specified type"""
        return [seg for seg in self.segments if seg["type"] == segment_type]
    
    def get_field(self, segment_type: str, field_position: int) -> Optional[str]:
        """Get field value from segment"""
        segment = self.get_segment(segment_type)
        if segment and field_position <= len(segment["fields"]):
            return segment["fields"][field_position - 1]["value"]
        return None
    
    def to_string(self) -> str:
        """Convert message to HL7 v2 string format"""
        lines = []
        for segment in self.segments:
            line = segment["type"]
            for field in segment["fields"]:
                line += self.field_separator + field["value"]
            lines.append(line)
        return "\r".join(lines) + "\r"
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate HL7 v2 message
        
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        # Check for MSH segment
        msh = self.get_segment("MSH")
        if not msh:
            errors.append("Missing MSH segment")
            return False, errors
        
        # Validate MSH fields
        if len(msh["fields"]) < 9:
            errors.append("MSH segment missing required fields")
        
        return len(errors) == 0, errors


class HL7v2Service:
    """Service for HL7 v2 operations"""
    
    def __init__(self, hl7_server_url: Optional[str] = None):
        self.hl7_server_url = hl7_server_url
    
    def create_admit_message(
        self,
        patient_id: str,
        patient_name: str,
        birth_date: str,
        gender: str,
        admission_date: str,
        admitting_doctor: str
    ) -> HL7v2Message:
        """
        Create ADT^A01 (Admit Patient) message
        
        Args:
            patient_id: Patient identifier
            patient_name: Patient name (Last^First^Middle)
            birth_date: Birth date (YYYYMMDD)
            gender: Gender (M/F/O/U)
            admission_date: Admission date (YYYYMMDDHHMMSS)
            admitting_doctor: Admitting doctor name
        
        Returns:
            HL7v2Message object
        """
        now = datetime.now()
        message_control_id = f"MSG{now.strftime('%Y%m%d%H%M%S')}"
        
        # MSH Segment
        msh = f"MSH|^~\\&|NEUROPREDICT|HOSPITAL|LAB|LAB|{now.strftime('%Y%m%d%H%M%S')}||ADT^A01^ADT_A01|{message_control_id}|P|2.5"
        
        # EVN Segment
        evn = f"EVN|A01|{now.strftime('%Y%m%d%H%M%S')}|||{admitting_doctor}"
        
        # PID Segment
        pid = f"PID|1||{patient_id}||{patient_name}||{birth_date}|{gender}|||"
        
        # PV1 Segment
        pv1 = f"PV1|1|I|ICU^ICU^01|||{admitting_doctor}^ADMITTING|||SUR||||1|||{admitting_doctor}||{admission_date}|||"
        
        message_text = f"{msh}\r{evn}\r{pid}\r{pv1}\r"
        
        return HL7v2Message(message_text)
    
    def create_observation_message(
        self,
        patient_id: str,
        observation_id: str,
        observation_code: str,
        observation_value: str,
        observation_units: str,
        observation_date: str,
        status: str = "F"
    ) -> HL7v2Message:
        """
        Create ORU^R01 (Observation Result) message
        
        Args:
            patient_id: Patient identifier
            observation_id: Observation identifier
            observation_code: Observation code (LOINC)
            observation_value: Observation value
            observation_units: Units
            observation_date: Observation date (YYYYMMDDHHMMSS)
            status: Result status (F=Final, P=Preliminary)
        
        Returns:
            HL7v2Message object
        """
        now = datetime.now()
        message_control_id = f"MSG{now.strftime('%Y%m%d%H%M%S')}"
        
        # MSH Segment
        msh = f"MSH|^~\\&|NEUROPREDICT|HOSPITAL|LAB|LAB|{now.strftime('%Y%m%d%H%M%S')}||ORU^R01^ORU_R01|{message_control_id}|P|2.5"
        
        # PID Segment
        pid = f"PID|1||{patient_id}|||||||"
        
        # OBR Segment (Observation Request)
        obr = f"OBR|1|{observation_id}||{observation_code}||||{observation_date}|||||||||||{status}||||||"
        
        # OBX Segment (Observation Result)
        obx = f"OBX|1|NM|{observation_code}||{observation_value}|{observation_units}||||{status}|||{observation_date}"
        
        message_text = f"{msh}\r{pid}\r{obr}\r{obx}\r"
        
        return HL7v2Message(message_text)
    
    def create_lab_result_message(
        self,
        patient_id: str,
        test_code: str,
        test_name: str,
        result_value: str,
        units: str,
        reference_range: str,
        result_status: str = "F"
    ) -> HL7v2Message:
        """
        Create ORU^R01 message for lab results
        
        Args:
            patient_id: Patient identifier
            test_code: Test code (LOINC)
            test_name: Test name
            result_value: Result value
            units: Units
            reference_range: Reference range
            result_status: Result status
        
        Returns:
            HL7v2Message object
        """
        now = datetime.now()
        message_control_id = f"MSG{now.strftime('%Y%m%d%H%M%S')}"
        observation_date = now.strftime('%Y%m%d%H%M%S')
        
        # MSH Segment
        msh = f"MSH|^~\\&|NEUROPREDICT|HOSPITAL|LAB|LAB|{observation_date}||ORU^R01^ORU_R01|{message_control_id}|P|2.5"
        
        # PID Segment
        pid = f"PID|1||{patient_id}|||||||"
        
        # OBR Segment
        obr = f"OBR|1|||{test_code}^{test_name}||||{observation_date}|||||||||||{result_status}||||||"
        
        # OBX Segment
        obx = f"OBX|1|NM|{test_code}^{test_name}||{result_value}|{units}||{reference_range}||{result_status}|||{observation_date}"
        
        message_text = f"{msh}\r{pid}\r{obr}\r{obx}\r"
        
        return HL7v2Message(message_text)
    
    def create_vital_signs_message(
        self,
        patient_id: str,
        vital_signs: Dict[str, Any]
    ) -> HL7v2Message:
        """
        Create ORU^R01 message for vital signs
        
        Args:
            patient_id: Patient identifier
            vital_signs: Dictionary of vital signs
                {
                    "blood_pressure": {"systolic": 120, "diastolic": 80},
                    "heart_rate": 72,
                    "temperature": 98.6,
                    "respiratory_rate": 16,
                    "oxygen_saturation": 98
                }
        
        Returns:
            HL7v2Message object
        """
        now = datetime.now()
        message_control_id = f"MSG{now.strftime('%Y%m%d%H%M%S')}"
        observation_date = now.strftime('%Y%m%d%H%M%S')
        
        # MSH Segment
        msh = f"MSH|^~\\&|NEUROPREDICT|HOSPITAL|DEVICE|DEVICE|{observation_date}||ORU^R01^ORU_R01|{message_control_id}|P|2.5"
        
        # PID Segment
        pid = f"PID|1||{patient_id}|||||||"
        
        # OBR Segment
        obr = f"OBR|1|||VITALS^Vital Signs||||{observation_date}|||||||||||F||||||"
        
        obx_segments = []
        obx_count = 1
        
        # Blood Pressure
        if "blood_pressure" in vital_signs:
            bp = vital_signs["blood_pressure"]
            systolic = bp.get("systolic", "")
            diastolic = bp.get("diastolic", "")
            if systolic and diastolic:
                obx = f"OBX|{obx_count}|NM|8480-6^Systolic BP||{systolic}|mmHg||||F|||{observation_date}"
                obx_segments.append(obx)
                obx_count += 1
                obx = f"OBX|{obx_count}|NM|8462-4^Diastolic BP||{diastolic}|mmHg||||F|||{observation_date}"
                obx_segments.append(obx)
                obx_count += 1
        
        # Heart Rate
        if "heart_rate" in vital_signs:
            hr = vital_signs["heart_rate"]
            obx = f"OBX|{obx_count}|NM|8867-4^Heart Rate||{hr}|/min||||F|||{observation_date}"
            obx_segments.append(obx)
            obx_count += 1
        
        # Temperature
        if "temperature" in vital_signs:
            temp = vital_signs["temperature"]
            obx = f"OBX|{obx_count}|NM|8310-5^Body Temperature||{temp}|F||||F|||{observation_date}"
            obx_segments.append(obx)
            obx_count += 1
        
        # Respiratory Rate
        if "respiratory_rate" in vital_signs:
            rr = vital_signs["respiratory_rate"]
            obx = f"OBX|{obx_count}|NM|9279-1^Respiratory Rate||{rr}|/min||||F|||{observation_date}"
            obx_segments.append(obx)
            obx_count += 1
        
        # Oxygen Saturation
        if "oxygen_saturation" in vital_signs:
            spo2 = vital_signs["oxygen_saturation"]
            obx = f"OBX|{obx_count}|NM|2708-6^Oxygen Saturation||{spo2}|%||||F|||{observation_date}"
            obx_segments.append(obx)
        
        message_text = f"{msh}\r{pid}\r{obr}\r" + "\r".join(obx_segments) + "\r"
        
        return HL7v2Message(message_text)
    
    def parse_message(self, message: str) -> HL7v2Message:
        """
        Parse HL7 v2 message
        
        Args:
            message: HL7 v2 message string
        
        Returns:
            HL7v2Message object
        """
        return HL7v2Message(message)
    
    def extract_patient_info(self, message: HL7v2Message) -> Dict[str, Any]:
        """
        Extract patient information from message
        
        Args:
            message: HL7v2Message object
        
        Returns:
            Dictionary with patient information
        """
        patient_info = {}
        
        pid = message.get_segment("PID")
        if pid:
            patient_info["patient_id"] = message.get_field("PID", 3)
            patient_info["name"] = message.get_field("PID", 5)
            patient_info["birth_date"] = message.get_field("PID", 7)
            patient_info["gender"] = message.get_field("PID", 8)
        
        return patient_info
    
    def extract_observations(self, message: HL7v2Message) -> List[Dict[str, Any]]:
        """
        Extract observations from message
        
        Args:
            message: HL7v2Message object
        
        Returns:
            List of observation dictionaries
        """
        observations = []
        
        obx_segments = message.get_segments("OBX")
        for obx in obx_segments:
            observation = {
                "observation_id": obx["fields"][1]["value"] if len(obx["fields"]) > 1 else "",
                "code": obx["fields"][3]["value"] if len(obx["fields"]) > 3 else "",
                "value": obx["fields"][5]["value"] if len(obx["fields"]) > 5 else "",
                "units": obx["fields"][6]["value"] if len(obx["fields"]) > 6 else "",
                "status": obx["fields"][11]["value"] if len(obx["fields"]) > 11 else "",
                "date": obx["fields"][14]["value"] if len(obx["fields"]) > 14 else ""
            }
            observations.append(observation)
        
        return observations
    
    def send_message(
        self,
        message: HL7v2Message,
        destination: Optional[str] = None
    ) -> bool:
        """
        Send HL7 v2 message to destination
        
        Args:
            message: HL7v2Message object
            destination: Destination URL (optional, uses default if not provided)
        
        Returns:
            True if successful
        """
        # در production، اینجا باید message را به HL7 server بفرستیم
        # از طریق MLLP (Minimal Lower Layer Protocol) یا HTTP
        
        destination = destination or self.hl7_server_url
        
        if not destination:
            logger.warning("No HL7 server URL configured")
            return False
        
        try:
            # اینجا باید MLLP یا HTTP connection برقرار کنیم
            # و message را بفرستیم
            
            message_str = message.to_string()
            logger.info(f"Sending HL7 v2 message to {destination}")
            logger.debug(f"Message: {message_str[:200]}...")
            
            # در production، اینجا باید actual sending logic باشد
            # برای حالا فقط log می‌کنیم
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending HL7 v2 message: {e}")
            return False

