# init_db 已移至 models.py 统一管理
# 保留此文件避免现有 import 出错
from .models import init_db

__all__ = ["init_db"]
