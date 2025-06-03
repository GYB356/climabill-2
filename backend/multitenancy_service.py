from typing import Dict, Optional, List
from fastapi import Request, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import logging
from auth_models import Tenant, TenantPlan