import re
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient, DESCENDING
from info import DATABASE_URL, DATABASE_NAME, MAX_BTN

myclient = MongoClient(DATABASE_URL)
mydb = myclient[DATABASE_NAME]
mycol = mydb['Files']

async def save_file(media):
    """Save file in database"""

    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    file = {
        '_id': media.file_unique_id,
        'file_name': file_name,
        'file_id': media.file_id,
        'file_size': media.file_size
    }
    try:
        # Insert new file at the beginning of the collection
        mycol.insert_one(file)
        print(f'{file_name} is saved')
        return "Saved"
    except DuplicateKeyError:
        print(f'{file_name} is already saved')
        return "Duplicates"


async def get_database_size():
    size = mydb.command("dbstats")['dataSize']
    return size


async def total_files_count():
    count = mycol.count_documents({})
    return count


async def get_search_results(query, max_results=MAX_BTN, offset=0, filter=False, language=None):
    """For given query return (results, next_offset, total_results)"""
    
    query = query.strip()
    if filter:  # For better results
        query = query.replace(' ', r'(\s|\.|\+|\-|_)')
        raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        return None, None, None

    filter = {'file_name': regex}
    total_results = mycol.count_documents(filter)
    next_offset = offset + max_results
    if next_offset >= total_results:
        next_offset = ""
    
    # Sort by $natural in descending order to get documents in insertion order
    cursor = mycol.find(filter).sort('$natural', DESCENDING).skip(offset).limit(max_results)
    
    if language:
        lang_files = [file for file in cursor if language.lower() in file['file_name'].lower()]
        files = lang_files[offset:offset + max_results]
        total_results = len(lang_files)
        next_offset = offset + max_results
        if next_offset >= total_results:
            next_offset = ""
        return files, next_offset, total_results
    
    files = list(cursor)
    return files, next_offset, total_results

async def get_file_details(file_unique_id):
    filter = {'_id': file_unique_id}
    file = mycol.find_one(filter)
    return file

async def delete_all_files():
    """Delete all files from the collection"""
    try:
        result = mycol.delete_many({})
        print(f'{result.deleted_count} files deleted')
        return result.deleted_count
    except Exception as e:
        print(f'Error deleting files: {str(e)}')
        return 0

async def delete_files_by_name(file_name):
    """Delete all files with the given name"""
    try:
        result = mycol.delete_many({'file_name': file_name})
        if result.deleted_count > 0:
            print(f'All files with name {file_name} deleted successfully')
            return True
        else:
            print(f'No files with name {file_name} found')
            return False
    except Exception as e:
        print(f'Error deleting files: {str(e)}')
        return False
