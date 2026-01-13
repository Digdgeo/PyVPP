#!/usr/bin/env python3
"""
Simple script to verify the status of HRVPP datasets
Run this periodically to check if VPP_Index becomes available again
"""

from hda import Client
from datetime import datetime

def verify_datasets():
    """
    Verifies the status of all HRVPP datasets
    """
    print("="*60)
    print("HRVPP Datasets Verification")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    client = Client()
    
    datasets = {
        'VPP_Index': 'EO:EEA:DAT:CLMS_HRVPP_VI',
        'VPP_ST': 'EO:EEA:DAT:CLMS_HRVPP_ST',
        'VPP_Pheno': 'EO:EEA:DAT:CLMS_HRVPP_VPP',
    }
    
    results = {}
    
    print("\nVerifying datasets...\n")
    
    for name, dataset_id in datasets.items():
        try:
            info = client.dataset(dataset_id)
            print(f"✅ {name:12} → AVAILABLE")
            print(f"   ID: {dataset_id}")
            print(f"   Title: {info.get('title', 'N/A')[:50]}")
            results[name] = 'AVAILABLE'
        except Exception as e:
            error_str = str(e)
            if "404" in error_str:
                print(f"❌ {name:12} → NOT AVAILABLE (404)")
                print(f"   ID: {dataset_id}")
                results[name] = 'NOT AVAILABLE (404)'
            elif "403" in error_str:
                print(f"⚠️  {name:12} → ACCESS DENIED (403)")
                print(f"   ID: {dataset_id}")
                results[name] = 'ACCESS DENIED'
            else:
                print(f"⚠️  {name:12} → ERROR")
                print(f"   ID: {dataset_id}")
                print(f"   Error: {e}")
                results[name] = f'ERROR: {e}'
        print()
    
    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    
    available = [k for k, v in results.items() if v == 'AVAILABLE']
    not_available = [k for k, v in results.items() if 'NOT AVAILABLE' in v]
    
    print(f"\n✅ Available: {len(available)}")
    for d in available:
        print(f"   - {d}")
    
    if not_available:
        print(f"\n❌ Not available: {len(not_available)}")
        for d in not_available:
            print(f"   - {d}")
    
    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)
    
    if results.get('VPP_Index') == 'AVAILABLE':
        print("\n🎉 VPP_Index is available again!")
        print("   You can use it normally in PyVPP.")
    else:
        print("\n📝 VPP_Index is still unavailable.")
        print("   Use VPP_ST or VPP_Pheno instead.")
        print("\n   Alternatives for LAI, FAPAR, NDVI:")
        print("   • Google Earth Engine")
        print("   • Sentinel Hub")
        print("   • Calculate from Sentinel-2")
    
    print("\n" + "="*60)
    
    return results


if __name__ == "__main__":
    try:
        results = verify_datasets()
    except Exception as e:
        print(f"\n❌ General error: {e}")
        print("\nMake sure that:")
        print("  1. You have the hda package installed")
        print("  2. Your .hdarc file is configured correctly")
        print("  3. You have internet connection")
