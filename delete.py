import requests

def delete_reports(report_ids, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    results = []
    for report_id in report_ids:
        url = f'http://192.168.0.108:8000/api/reports/{report_id}/'
        try:
            response = requests.delete(url, headers=headers)
            results.append({
                'report_id': report_id,
                'status': response.status_code,
                'success': response.ok
            })
            print(f"Deleting report {report_id}: {'Success' if response.ok else 'Failed'} (Status: {response.status_code})")
        except Exception as e:
            print(f"Error deleting report {report_id}: {str(e)}")
            results.append({
                'report_id': report_id,
                'status': None,
                'error': str(e)
            })
    
    return results

# Usage
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM4MDA4OTYwLCJpYXQiOjE3MzgwMDUzNjAsImp0aSI6IjQzN2M4YjI5M2ExODQwZTNhNzZiMmVkMDE2NDllMDBkIiwidXNlcl9pZCI6Mn0.p_0JCxZzQY9zf1wRvRk811i7bPa5k098J0pAR77z_2c"  # Replace with your actual token
report_ids = [9,10,11,12,13,14,15,16]  # Add all the report IDs you want to delete

results = delete_reports(report_ids, access_token)

# Print summary
print("\nDeletion Summary:")
successful = len([r for r in results if r.get('success', False)])
failed = len(results) - successful
print(f"Successfully deleted: {successful}")
print(f"Failed to delete: {failed}")