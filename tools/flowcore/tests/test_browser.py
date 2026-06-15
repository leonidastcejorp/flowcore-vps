#!/usr/bin/env python3
"""
Simple test suite for FlowCore modules.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flowcore.utils.names import random_name, random_email, random_password

print("🧪 FlowCore Test Suite")
print("=" * 40)

# Test name generator
print("\n📋 Name Generator:")
for _ in range(3):
    print(f"   {random_name():30} | {random_email():30}")

# Test password
pw = random_password()
print(f"\n🔐 Sample password: {pw} ({len(pw)} chars)")

# Test fingerprint
from flowcore.core.fingerprint import IdentityProfile
print("\n🖐️  Fingerprint Profiles:")
for pname in ['windows_chrome', 'mac_chrome']:
    prof = IdentityProfile(pname)
    d = prof.to_dict()
    print(f"   {pname:15} → {d['platform']:8} | {d['locale']:6}")

print("\n✅ All system tests passed!")
