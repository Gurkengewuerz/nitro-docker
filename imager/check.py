import requests
import json
from collections.abc import Iterable

def check_figuremap_parts(url="http://localhost:8080/assets/gamedata/FigureMap.json"):
    """
    Fetches FigureMap.json and checks if any library.parts is not iterable.
    
    Args:
        url: The URL to fetch the FigureMap.json from
    
    Returns:
        Dictionary with validation results
    """
    try:
        # Fetch the data
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if libraries exists
        if 'libraries' not in data:
            return {
                'success': False,
                'error': 'No "libraries" key found in JSON'
            }
        
        libraries = data['libraries']
        
        # Check if libraries itself is iterable
        if not isinstance(libraries, Iterable) or isinstance(libraries, str):
            return {
                'success': False,
                'error': 'libraries is not iterable (or is a string)'
            }
        
        # Check each library's parts
        issues = []
        for idx, library in enumerate(libraries):
            if not library:
                continue
                
            library_id = library.get('id', f'unknown_at_index_{idx}')
            
            # Check if parts exists
            if 'parts' not in library:
                issues.append({
                    'library_id': library_id,
                    'issue': 'Missing "parts" key'
                })
                continue
            
            parts = library['parts']
            
            # Check if parts is iterable (but not a string)
            if not isinstance(parts, Iterable) or isinstance(parts, str):
                issues.append({
                    'library_id': library_id,
                    'issue': f'parts is not iterable (type: {type(parts).__name__})'
                })
        
        # Return results
        if issues:
            return {
                'success': False,
                'total_libraries': len(libraries),
                'issues_found': len(issues),
                'issues': issues
            }
        else:
            return {
                'success': True,
                'total_libraries': len(libraries),
                'message': 'All library.parts are iterable'
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Failed to fetch URL: {str(e)}'
        }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse JSON: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


if __name__ == "__main__":
    result = check_figuremap_parts()
    
    print("=" * 60)
    print("FigureMap Parts Validation Results")
    print("=" * 60)
    
    if result['success']:
        print(f"✓ SUCCESS: {result['message']}")
        print(f"  Total libraries checked: {result['total_libraries']}")
    else:
        if 'error' in result:
            print(f"✗ ERROR: {result['error']}")
        else:
            print(f"✗ VALIDATION FAILED")
            print(f"  Total libraries: {result['total_libraries']}")
            print(f"  Issues found: {result['issues_found']}")
            print("\nDetailed issues:")
            for issue in result['issues']:
                print(f"  - Library '{issue['library_id']}': {issue['issue']}")
    
    print("=" * 60)