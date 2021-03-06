from image import Image
from config import Config
from request import Request

class ImageRequest(Request):
    def __init__(self, request_json, queue, building=None):
        super().__init__(request_json)
        self.building = building
        self.build_queue = queue
        self.config = Config()
        self.needed_values = ["distro", "target", "subtarget", "board", "packages"]

    def get_sysupgrade(self):
        bad_request = self.check_bad_request()
        if bad_request:
            return bad_request

        self.profile = self.request_json["board"]
        if not self.check_profile:
            self.response_dict["error"] = "board not found"
            return self.respond(), 400

        
        if "network_profile" in self.request_json:
            if self.check_network_profile():
                self.request_json["error"] = "network profile not found"
                return self.respond(), 400
        else:
            self.network_profile = None
        
        self.image = Image()
        self.image.request_variables(self.distro, self.version, self.target, self.subtarget, self.profile, self.packages, self.network_profile)

        if self.image.created():
            self.response_dict["url"] =  self.config.get("update_server") + "/" + self.image.get_sysupgrade()
            return self.respond(), 200
        else:
            if not self.building == self.image.name:
                self.build_queue.put(self.image)
                # this does not really makes sense right now as the queue just grows
                # need OrderedSetQueue with index foo
                self.response_dict["queue"] = self.build_queue.qsize()
                return self.respond(), 201
            else:
                return "", 206

    def check_profile(self):
        if database.check_target(self.target, self.subtarget, self.profile):
            return True
        return False

    def check_network_profile(self):
        network_profile = self.request_json["network_profile"]
        network_profile_path = os.path.join(selt.config.get("network_profile_folder"), network_profile)

        if os.path.isdir(network_profile_path):
            logging.debug("found network_profile %s", network_profile)
            self.network_profile = network_profile
            return True
        logging.debug("could not find network_profile %s", network_profile)
        return False
