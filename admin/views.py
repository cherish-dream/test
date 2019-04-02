
from . import admin

@admin.route('test/',methods = ['GET'])
def list():
    return 'list'