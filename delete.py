import requests

def delete_reports(report_ids, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    results = []
    for report_id in report_ids:
        url = f'http://10.96.28.189:8000/api/reports/{report_id}/'
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
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM4MjQwMjA2LCJpYXQiOjE3MzgyMzY2MDYsImp0aSI6ImQ2NTk5NjIxYWJmNzQ0Y2E4NDY2NjliOGE1YzZiMzA2IiwidXNlcl9pZCI6Mn0.dG5xDCrrztE6w7fJ15t6lmZBLCI868T3R50S2eO6g-w"  # Replace with your actual token
report_ids = [46,47,48,49,50]  # Add all the report IDs you want to delete

results = delete_reports(report_ids, access_token)

# Print summary
print("\nDeletion Summary:")
successful = len([r for r in results if r.get('success', False)])
failed = len(results) - successful
print(f"Successfully deleted: {successful}")
print(f"Failed to delete: {failed}")