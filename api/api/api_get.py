from api_config import *
import calmsize
# home link for API. It will welcome API user
class Index(object):
    def on_get(self, req, resp):
        resp.json = {"message": "Connectivity API v0.1. See docs for API endpoints.",
                     "status": "success"}

class CheckFiles(object):
    def on_get(self, req, resp):
        files = list(map(lambda x: {'file': x.split(LOCAL_FOLDER)[1], 'size': str(calmsize.size(os.stat(x).st_size)) }, glob.glob(LOCAL_FOLDER+'*.*')))
        resp.json = {"files": files}


class HealthCheck(object):
    def on_get(self, req, resp):
        resp.json = {"message": "It works!",
                     "status": "success"}

# assigning API routes for given handler classes
api.add_route('/', Index())
api.add_route('/listfiles', CheckFiles())
api.add_route('/health', HealthCheck())
