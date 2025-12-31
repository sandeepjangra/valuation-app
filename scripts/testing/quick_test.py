#!/usr/bin/env python3
import asyncio
import aiohttp

async def quick_test():
    async with aiohttp.ClientSession() as session:
        # Login
        async with session.post('http://localhost:8000/api/auth/login', 
                               json={'email': 'sk.tindwal@gmail.com', 'password': 'admin123'}) as resp:
            data = await resp.json()
            token = data['data']['access_token']
            
        # Create report
        headers = {'Authorization': f'Bearer {token}'}
        async with session.post('http://localhost:8000/api/reports', 
                               json={'bank_code': 'SBI', 'template_id': 'land-property', 
                                    'property_address': 'Debug Test', 'report_data': {'test': 'value'}}, 
                               headers=headers) as resp:
            print(f'Report creation status: {resp.status}')

asyncio.run(quick_test())